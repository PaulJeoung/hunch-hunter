import os
import datetime
from typing import Dict, Any
import numpy as np
import pandas as pd
import requests
import FinanceDataReader as fdr
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class ClosingBetPipeline:
    def __init__(self, top_universe_count: int = 100):
        today = datetime.datetime.today()
        # 최근 5일 중 평일 탐색
        for i in range(0, 5):
            check_day = today - datetime.timedelta(days=i)
            if check_day.weekday() < 5:
                self.target_date = check_day.strftime("%Y%m%d")
                break
        else:
            self.target_date = today.strftime("%Y%m%d")

        self.top_n = top_universe_count
        self.supabase = self._init_supabase()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://stock.naver.com/"
        })

    def _init_supabase(self) -> Client | None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("[Warning] Supabase 환경변수가 없어 DB 저장을 건너뜁니다.")
            return None
        return create_client(url, key)

    def calculate_obv_signal(self, df: pd.DataFrame) -> bool:
        """OBV 및 EMA(20) 골든크로스/상승 추세 판정"""
        if len(df) < 20:
            return False
        direction = np.where(df['Close'] > df['Close'].shift(1), 1,
                    np.where(df['Close'] < df['Close'].shift(1), -1, 0))
        obv = (df['Volume'] * direction).cumsum()
        obv_ema = obv.ewm(span=20, adjust=False).mean()
        return bool(obv.iloc[-1] > obv_ema.iloc[-1])

    def get_market_strength_naver(self, ticker: str) -> float:
        """
        네이버 증권 API를 통해 체결강도/수급강도(CVD 프록시) 조회
        """
        safe_ticker = str(ticker).strip().zfill(6)
        
        # 1차 시도: basic API (체결강도 확인)
        url_basic = f"https://m.stock.naver.com/api/stock/{safe_ticker}/basic"
        try:
            res = self.session.get(url_basic, timeout=3)
            if res.status_code == 200:
                data = res.json()
                if "executionStrength" in data and data["executionStrength"]:
                    strength = float(str(data["executionStrength"]).replace(",", ""))
                    cvd_ratio = round((strength - 100) / 2, 2)
                    return cvd_ratio
        except Exception:
            pass

        # 2차 시도: trend API (장마감 후 체결강도 누락 시 외인+기관 순매수 비율로 CVD 대체 계산)
        url_trend = f"https://m.stock.naver.com/api/stock/{safe_ticker}/trend"
        try:
            res = self.session.get(url_trend, timeout=3)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    latest = data[0]
                    foreign_qty = int(str(latest.get("foreignPureBuyQuant", 0)).replace(",", ""))
                    organ_qty = int(str(latest.get("organPureBuyQuant", 0)).replace(",", ""))
                    total_smart = foreign_qty + organ_qty
                    
                    # 스마트머니 순매수 유입이 있으면 양의 CVD 환산값 부여
                    if total_smart > 0:
                        return 10.0
                    elif total_smart < 0:
                        return -5.0
                    return 5.0
        except Exception:
            pass

        # 기본값: 0.0
        return 0.0

    def analyze_stock(self, ticker: str, name: str, trading_value: int) -> Dict[str, Any] | None:
        safe_ticker = str(ticker).strip().zfill(6)
        end_date = f"{self.target_date[:4]}-{self.target_date[4:6]}-{self.target_date[6:]}"
        start_date = (datetime.datetime.strptime(self.target_date, "%Y%m%d") - datetime.timedelta(days=70)).strftime("%Y-%m-%d")

        try:
            df_hist = fdr.DataReader(safe_ticker, start_date, end_date)
            if df_hist.empty or len(df_hist) < 20:
                return None

            latest = df_hist.iloc[-1]
            prev = df_hist.iloc[-2]

            close = int(latest["Close"])
            open_p = int(latest["Open"])
            high = int(latest["High"])
            low = int(latest["Low"])
            day_return = round(((close - prev["Close"]) / prev["Close"]) * 100, 2)

            # 1. 캔들 필터: 적정 양봉 (+1.5% ~ +15%), 윗꼬리가 전체 변동폭의 35% 이하
            candle_body = close - open_p
            candle_range = high - low
            upper_wick = high - max(close, open_p)

            is_valid_candle = (
                (1.5 <= day_return <= 15.0) and
                (candle_body > 0) and
                (candle_range == 0 or (upper_wick / candle_range <= 0.35))
            )
            if not is_valid_candle:
                return None

            # 2. OBV 추세 검증
            if not self.calculate_obv_signal(df_hist):
                return None

            # 3. CVD (수급강도) 검증
            cvd_ratio = self.get_market_strength_naver(safe_ticker)
            if cvd_ratio < 5.0:  # 최소 기준 (기준 충족 여부 확인)
                return None

            # 목표가 계산
            target_1 = int(round(close * 1.10))
            target_2 = int(round(close * 1.20))
            score = round(min(99.0, max(60.0, cvd_ratio * 2 + day_return * 3 + 40)), 1)

            return {
                "ticker": safe_ticker,
                "name": name,
                "close_price": close,
                "day_return": day_return,
                "trading_value": trading_value,
                "cvd_ratio": cvd_ratio,
                "obv_status": "BULL",
                "target_price_1": target_1,
                "target_price_2": target_2,
                "score": score
            }
        except Exception:
            return None

    def run(self):
        print(f"[{self.target_date}] 거래대금 상위 종목 수집 중...")
        df_krx = fdr.StockListing('KRX')
        
        # ⚠️ [핵심 수정] 인덱스 번호가 아니라 'Code' 컬럼을 고유 종목코드로 인덱싱
        if "Code" in df_krx.columns:
            df_krx = df_krx.set_index("Code")
            
        df_sorted = df_krx.sort_values(by="Amount", ascending=False).head(self.top_n).copy()

        results = []
        for ticker, row in df_sorted.iterrows():
            ticker_str = str(ticker).strip().zfill(6)
            name = row.get("Name", "")
            trading_val = int(row.get("Amount", 0))

            sig = self.analyze_stock(ticker_str, name, trading_val)

            print(f"  [종가핑] {name} / {trading_val} / {sig}")

            if sig:
                print(f"  🔥 [종가배팅 포착] {name} ({sig['ticker']}): 점수 {sig['score']}점 | 1차목표가: {sig['target_price_1']:,}원")
                results.append(sig)
            else:
                # 디버그용 출력 (선택사항)
                # print(f"  [미부합] {name} ({ticker_str})")
                pass

        if not results:
            print("조건에 부합하는 종가 배팅 종목이 없습니다.")
            return

        df_results = pd.DataFrame(results).sort_values(by="score", ascending=False)
        print(f"\n총 {len(df_results)}건의 종가 배팅 종목 발굴 완료!")

        if self.supabase:
            formatted_date = f"{self.target_date[:4]}-{self.target_date[4:6]}-{self.target_date[6:]}"
            for _, row in df_results.iterrows():
                try:
                    self.supabase.table("stocks").upsert({
                        "ticker": row["ticker"],
                        "name": row["name"],
                        "market": "KRX"
                    }).execute()

                    self.supabase.table("closing_bet_signals").upsert({
                        "ticker": row["ticker"],
                        "signal_date": formatted_date,
                        "close_price": row["close_price"],
                        "day_return": row["day_return"],
                        "trading_value": row["trading_value"],
                        "cvd_ratio": row["cvd_ratio"],
                        "obv_status": row["obv_status"],
                        "target_price_1": row["target_price_1"],
                        "target_price_2": row["target_price_2"],
                        "score": row["score"]
                    }).execute()
                except Exception as e:
                    print(f"DB 저장 오류: {e}")
            print(f"⚡ 총 {len(df_results)}건 종가 배팅 시그널 동기화 완료!")

if __name__ == "__main__":
    pipeline = ClosingBetPipeline(top_universe_count=100)
    pipeline.run()