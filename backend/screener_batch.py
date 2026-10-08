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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def _init_supabase(self) -> Client | None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("[Warning] Supabase 환경변수가 설정되지 않아 DB 저장을 생략합니다.")
            return None
        return create_client(url, key)

    def get_trading_value_top_universe(self) -> pd.DataFrame:
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
        safe_ticker = str(ticker).strip().zfill(6)
        url = f"https://m.stock.naver.com/api/stock/{safe_ticker}/trend"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"https://stock.naver.com/domestic/stock/{safe_ticker}/price"
        }

        def parse_quant(val) -> int:
            if val is None:
                return 0
            val_str = str(val).replace(",", "").replace("+", "").strip()
            try:
                return int(val_str)
            except (ValueError, TypeError):
                return 0

        try:
            res = self.session.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    latest = data[0]

                    # 1. 외인 키명 완벽 대응 (foreignerPureBuyQuant 우선, foreignPureBuyQuant 보조)
                    foreign_qty = parse_quant(
                        latest.get("foreignerPureBuyQuant") or latest.get("foreignPureBuyQuant")
                    )

                    # 2. 기관 키명 대응 (organPureBuyQuant 또는 institutionPureBuyQuant)
                    inst_qty = parse_quant(
                        latest.get("organPureBuyQuant") or latest.get("institutionPureBuyQuant")
                    )

                    # 3. 개인 키명 대응
                    if "individualPureBuyQuant" in latest and latest.get("individualPureBuyQuant") is not None:
                        ind_qty = parse_quant(latest.get("individualPureBuyQuant"))
                    else:
                        ind_qty = -(foreign_qty + inst_qty)

                    res_dict = {
                        "개인": int(ind_qty * current_price),
                        "외국인": int(foreign_qty * current_price),
                        "기관합계": int(inst_qty * current_price)
                    }

                    # 수급 확인용 디버그 로그 (주수 및 환산 억단위)
                    f_억 = round(res_dict["외국인"] / 100_000_000, 1)
                    i_억 = round(res_dict["기관합계"] / 100_000_000, 1)
                    p_억 = round(res_dict["개인"] / 100_000_000, 1)
                    print(f"  📊 [{safe_ticker}] 외인: {foreign_qty:+,}주({f_억:+}억) | 기관: {inst_qty:+,}주({i_억:+}억) | 개인: {ind_qty:+,}주({p_억:+}억)")

                    return res_dict

        except Exception as e:
            print(f"  ⚠️ [{safe_ticker}] 수급 조회 실패: {e}")

        return {"개인": 0, "외국인": 0, "기관합계": 0}

    def analyze_ticker(self, ticker: str, name: str, net_row: Dict[str, int]) -> Dict[str, Any] | None:
        try:
            safe_ticker = str(ticker).strip().zfill(6)
            end_date = f"{self.target_date[:4]}-{self.target_date[4:6]}-{self.target_date[6:]}"
            start_date = (datetime.datetime.strptime(self.target_date, "%Y%m%d") - datetime.timedelta(days=70)).strftime("%Y-%m-%d")

            df_hist = fdr.DataReader(safe_ticker, start_date, end_date)
            if df_hist.empty or len(df_hist) < 15:
                return None

            close_price = int(df_hist["Close"].iloc[-1])
            prev_close = int(df_hist["Close"].iloc[-2]) if len(df_hist) > 1 else close_price
            day_return = round(((close_price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0

            # ---------------------------------------------------------
            # 1. 필수 제외: 조회 시점 상한가/하한가 (±28% 이상) 배제
            # ---------------------------------------------------------
            if abs(day_return) >= 28.0:
                return None

            # ---------------------------------------------------------
            # 2. 최근 5일 / 10일 상한가(+29% 이상) 발생 빈도 검증
            # ---------------------------------------------------------
            df_hist["daily_return"] = df_hist["Close"].pct_change() * 100
            
            # 최근 5거래일, 10거래일의 상한가 일수 산출
            limit_up_count_5d = int((df_hist["daily_return"].iloc[-5:] >= 29.0).sum())
            limit_up_count_10d = int((df_hist["daily_return"].iloc[-10:] >= 29.0).sum())

            # [세력 이탈 필터] 5일 이내 상한가 2회 이상 또는 10일 이내 3회 이상 -> 제외
            if limit_up_count_5d >= 2 or limit_up_count_10d >= 3:
                return None

            # ---------------------------------------------------------
            # 3. 거래량 Z-Score 산출
            # ---------------------------------------------------------
            volumes = df_hist["Volume"].values
            curr_vol = float(volumes[-1])
            mean_vol = float(np.mean(volumes[:-1]))
            std_vol = float(np.std(volumes[:-1]))

            if std_vol > 0:
                vol_zscore = (curr_vol - mean_vol) / std_vol
                if np.isnan(vol_zscore) or np.isinf(vol_zscore):
                    vol_zscore = 0.5
            else:
                vol_zscore = 0.5

            # ---------------------------------------------------------
            # 4. 수급 및 가격 조건 판정
            # ---------------------------------------------------------
            individual = net_row.get("개인", 0)
            foreign = net_row.get("외국인", 0)
            institution = net_row.get("기관합계", 0)

            # 세력 매집 흔적 조건:
            # - 스마트머니(외인/기관) 매수 유입 > 0
            # - 개인 순매도 <= 0
            # - 잠잠한 주가 구간 (-4% ~ +9%)
            if (foreign > 0 or institution > 0) and individual <= 0 and abs(day_return) < 9.0:
                
                # 순매수한 주체의 양수치만 인정
                smart_money_buy = max(0, foreign) + max(0, institution)

                # 5일 매집 연속성 점수 (5일 변동성 압축도 및 수급 기반)
                # 최근 5일 가격 변동폭(고가-저가)이 안정적인지 측정
                range_5d = ((df_hist["High"].iloc[-5:] - df_hist["Low"].iloc[-5:]) / df_hist["Close"].iloc[-5:]).mean()
                acc_score_5d = round(float(np.clip((1.0 - range_5d) * 50 + (smart_money_buy / 100_000_000 * 0.1), 30.0, 99.0)), 1)

                # 당일 종합 매집 점수
                raw_score = (vol_zscore * 12.0) + ((smart_money_buy / 100_000_000) * 0.15) + 45.0

                # 5일 내 상한가 1회 발생 시: 피로감 반영 감점 (-15점)
                if limit_up_count_5d == 1:
                    raw_score -= 15.0

                score = round(float(np.clip(raw_score, 40.0, 99.0)), 1)

                return {
                    "ticker": safe_ticker,
                    "name": name,
                    "close_price": close_price,
                    "day_return": day_return,
                    "individual_net": int(individual),
                    "foreign_net": int(foreign),
                    "institution_net": int(institution),
                    "vol_zscore": round(max(0.5, float(vol_zscore)), 2),
                    "limit_up_count_5d": limit_up_count_5d,
                    "acc_score_5d": acc_score_5d,
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
        print(f"[{self.target_date}] 유니버스 {len(ticker_list)}종목 정밀 분석 시작...")

        results = []
        for idx, ticker in enumerate(ticker_list):
            safe_ticker = str(ticker).strip().zfill(6)
            row = df_universe.loc[ticker]
            
            # 중복 행 방어: 종목코드로 조회 시 Series가 아닌 DataFrame으로 반환될 경우 1행 추출
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]

            name = str(row.get("종목명", row.get("Name", safe_ticker)))
            
            # [방어 로직] Close 값이 '-', None, 공백 문자열인 경우 예외 처리
            raw_close = str(row.get("Close", "10000")).replace(",", "").strip()
            if raw_close.isdigit():
                curr_price = int(raw_close)
            else:
                curr_price = 10000

            # 거래정지 또는 0원 종목 스킵
            if curr_price <= 0:
                continue

            net_data = self.get_investor_trend_naver(safe_ticker, curr_price)
            signal = self.analyze_ticker(safe_ticker, name, net_data)

            if signal:
                warn_tag = " [과열주의:5일내상한가]" if signal.get("limit_up_count_5d", 0) > 0 else ""
                print(f"  👉 [★포착] {name} ({signal['ticker']}) - 매집: {signal['score']}점 | 5일연속성: {signal['acc_score_5d']}점{warn_tag}")
                results.append(signal)

            if (idx + 1) % 25 == 0:
                print(f"  진행률: {idx + 1}/{len(ticker_list)} 완료...")

        if not results:
            print("조건에 부합하는 매집 종목이 없습니다.")
            return

        df_results = pd.DataFrame(results).sort_values(by="score", ascending=False)
        print(f"\n총 {len(df_results)}건의 매집 흔적 발굴 완료!")

        # Supabase 적재 (신규 컬럼 포함)
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
                        "limit_up_count_5d": row["limit_up_count_5d"],
                        "acc_score_5d": row["acc_score_5d"],
                        "score": row["score"]
                    }).execute()
                except Exception as db_err:
                    print(f"DB 저장 오류({row['ticker']}): {db_err}")

            print("⚡ Supabase 데이터베이스 동기화 완료!")

if __name__ == "__main__":
    pipeline = AccumulationRadarPipeline(top_universe_count=100)
    pipeline.run()