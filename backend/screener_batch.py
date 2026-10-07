import os
import sys
import datetime
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import requests
import FinanceDataReader as fdr
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class AccumulationRadarPipeline:
    def __init__(self, target_date: str = None, top_universe_count: int = 100):
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
            print("[Warning] Supabase 환경변수가 설정되지 않아 DB 저장을 생략합니다.")
            return None
        return create_client(url, key)

    def get_trading_value_top_universe(self) -> pd.DataFrame:
        """거래대금 상위 유니버스 수집"""
        print(f"[{self.target_date}] 거래대금 상위 {self.top_n} 종목 조회 중...")
        try:
            df_krx = fdr.StockListing('KRX')
            df_sorted = df_krx.sort_values(by="Amount", ascending=False).head(self.top_n).copy()
            df_sorted = df_sorted.set_index("Code")
            df_sorted["종목명"] = df_sorted["Name"]
            return df_sorted
        except Exception as e:
            print(f"FinanceDataReader 조회 실패: {e}")
            return pd.DataFrame()

    def get_investor_trend_naver(self, ticker: str, current_price: int) -> Dict[str, int]:
        """
        네이버 증권 trend JSON API 직접 호출 및 수급 리턴 검증 로그
        """
        safe_ticker = str(ticker).strip().zfill(6)
        url = f"https://m.stock.naver.com/api/stock/{safe_ticker}/trend"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": f"https://stock.naver.com/domestic/stock/{safe_ticker}/price"
        }

        try:
            res = self.session.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    latest = data[0]

                    # 1. 원본 수량(주) 파싱
                    bizdate = latest.get("bizdate", "날짜미상")
                    foreign_qty = int(str(latest.get("foreignPureBuyQuant", 0)).replace(",", ""))
                    inst_qty = int(str(latest.get("organPureBuyQuant", 0)).replace(",", ""))
                    
                    if "individualPureBuyQuant" in latest:
                        ind_qty = int(str(latest.get("individualPureBuyQuant", 0)).replace(",", ""))
                    else:
                        ind_qty = -(foreign_qty + inst_qty)

                    # 2. 금액 환산 (원 단위)
                    result_dict = {
                        "개인": ind_qty * current_price,
                        "외국인": foreign_qty * current_price,
                        "기관합계": inst_qty * current_price
                    }

                    # 3. 콘솔 검증 로그 (수량 및 억 단위 환산 출력)
                    f_억 = round(result_dict["외국인"] / 100_000_000, 1)
                    i_억 = round(result_dict["기관합계"] / 100_000_000, 1)
                    p_억 = round(result_dict["개인"] / 100_000_000, 1)

                    print(f"  🔍 [{bizdate}] {safe_ticker} 수급 수집 완료:")
                    print(f"      ├─ 순매수 수량: 외인 {foreign_qty:,}주 | 기관 {inst_qty:,}주 | 개인 {ind_qty:,}주")
                    print(f"      └─ 환산 금액  : 외인 {f_억}억 | 기관 {i_억}억 | 개인 {p_억}억 (단가: {current_price:,}원)")

                    return result_dict

        except Exception as e:
            print(f"  ⚠️ [{safe_ticker}] 수급 데이터 요청 실패: {e}")

        # 수집 실패 시 0 반환
        return {"개인": 0, "외국인": 0, "기관합계": 0}

    def analyze_ticker(self, ticker: str, name: str, net_row: Dict[str, int]) -> Dict[str, Any] | None:
        try:
            safe_ticker = str(ticker).strip().zfill(6)
            end_date = f"{self.target_date[:4]}-{self.target_date[4:6]}-{self.target_date[6:]}"
            start_date = (datetime.datetime.strptime(self.target_date, "%Y%m%d") - datetime.timedelta(days=70)).strftime("%Y-%m-%d")
            
            df_hist = fdr.DataReader(safe_ticker, start_date, end_date)
            if df_hist.empty or len(df_hist) < 10:
                return None

            volumes = df_hist["Volume"].values
            curr_vol = volumes[-1]
            mean_vol = np.mean(volumes[:-1])
            std_vol = np.std(volumes[:-1])
            vol_zscore = (curr_vol - mean_vol) / std_vol if std_vol > 0 else 0.5

            close_price = int(df_hist["Close"].iloc[-1])
            prev_close = int(df_hist["Close"].iloc[-2]) if len(df_hist) > 1 else close_price
            day_return = round(((close_price - prev_close) / prev_close) * 100, 2)

            individual = net_row.get("개인", 0)
            foreign = net_row.get("외국인", 0)
            institution = net_row.get("기관합계", 0)

            # 흔적 레이더 조건:
            # 1. 외인 또는 기관 순매수 > 0
            # 2. 개인 순매도 <= 0
            # 3. 주가 변동폭이 너무 크지 않은 구간 (-4% ~ +9%)
            if (foreign > 0 or institution > 0) and individual <= 0 and abs(day_return) < 9.0:
                score = round(min(99.0, max(50.0, float((vol_zscore * 12) + (abs(foreign + institution) / 100_000_000 * 0.15) + 45))), 1)
                return {
                    "ticker": safe_ticker,
                    "name": name,
                    "close_price": close_price,
                    "day_return": day_return,
                    "individual_net": int(individual),
                    "foreign_net": int(foreign),
                    "institution_net": int(institution),
                    "vol_zscore": round(max(0.5, float(vol_zscore)), 2),
                    "score": score
                }
        except Exception:
            return None

        return None

    def run(self):
        df_universe = self.get_trading_value_top_universe()
        if df_universe.empty:
            print("유니버스 데이터를 가져오지 못했습니다.")
            return

        ticker_list = df_universe.index.tolist()
        print(f"[{self.target_date}] 유니버스 {len(ticker_list)}종목 분석 시작...")

        results = []
        for idx, ticker in enumerate(ticker_list):
            name = df_universe.loc[ticker, "종목명"]
            curr_price = int(df_universe.loc[ticker].get("Close", 10000))
            
            # JSON API 기반 수급 추출
            net_data = self.get_investor_trend_naver(ticker, curr_price)
            signal = self.analyze_ticker(ticker, name, net_data)
            
            print(f"  [탐색핑] {name} / {curr_price} / {net_data} / {signal}")

            if signal:
                print(f"  👉 [포착] {name} ({signal['ticker']}) - 매집 점수: {signal['score']}점 | 외인: {round(signal['foreign_net']/100000000, 1)}억 | 기관: {round(signal['institution_net']/100000000, 1)}억")
                results.append(signal)

            if (idx + 1) % 25 == 0:
                print(f"  진행률: {idx + 1}/{len(ticker_list)} 완료...")

        if not results:
            print("조건에 부합하는 매집 종목이 없습니다.")
            return

        df_results = pd.DataFrame(results).sort_values(by="score", ascending=False)
        print(f"\n총 {len(df_results)}건의 매집 흔적 발굴 완료!")

        # Supabase 적재
        if self.supabase:
            formatted_date = f"{self.target_date[:4]}-{self.target_date[4:6]}-{self.target_date[6:]}"
            for _, row in df_results.iterrows():
                try:
                    self.supabase.table("stocks").upsert({
                        "ticker": row["ticker"],
                        "name": row["name"],
                        "market": "KRX"
                    }).execute()

                    self.supabase.table("accumulation_signals").upsert({
                        "ticker": row["ticker"],
                        "signal_date": formatted_date,
                        "close_price": row["close_price"],
                        "day_return": row["day_return"],
                        "vol_zscore": row["vol_zscore"],
                        "individual_net": row["individual_net"],
                        "foreign_net": row["foreign_net"],
                        "institution_net": row["institution_net"],
                        "score": row["score"]
                    }).execute()
                except Exception as db_err:
                    print(f"DB 저장 에러 ({row['ticker']}): {db_err}")

            print("⚡ Supabase 데이터베이스 동기화 완료!")


if __name__ == "__main__":
    pipeline = AccumulationRadarPipeline(top_universe_count=100)
    pipeline.run()