import os
from typing import Set, Dict, Any, List
from fastapi import APIRouter, Depends
from supabase import create_client, Client
from app.core.security import get_current_user, CurrentUser

router = APIRouter(prefix="/api/cross-analysis", tags=["Cross Analysis"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

def clean_date_str(val: Any) -> str:
    """날짜 필드가 문자열/date/timestamp 어떤 형태든 YYYY-MM-DD(10자리)로 정규화"""
    if not val:
        return ""
    return str(val).strip()[:10]

@router.get("/overlap-5d")
def get_overlap_signals_5d(user: CurrentUser = Depends(get_current_user)):
    if not supabase:
        return {"tier": user.role, "is_truncated": False, "total_count": 0, "data": []}

    try:
        # 1. 두 테이블에서 최근 기록된 날짜를 각각 충분히 가져와 실제 최근 5거래일(고유일자) 도출
        acc_dates_res = supabase.table("accumulation_signals") \
            .select("signal_date") \
            .order("signal_date", desc=True) \
            .limit(1000) \
            .execute()

        bet_dates_res = supabase.table("closing_bet_signals") \
            .select("signal_date") \
            .order("signal_date", desc=True) \
            .limit(1000) \
            .execute()

        all_dates: Set[str] = set()
        for r in (acc_dates_res.data or []):
            d = clean_date_str(r.get("signal_date"))
            if d:
                all_dates.add(d)

        for r in (bet_dates_res.data or []):
            d = clean_date_str(r.get("signal_date"))
            if d:
                all_dates.add(d)

        # 내림차순 정렬 후 최신 5거래일 확정 (예: 14일, 13일, 10일, 9일, 8일 등)
        recent_5_dates: List[str] = sorted(list(all_dates), reverse=True)[:5]
        
        # 데이터가 없으면 빈 배열 반환
        if not recent_5_dates:
            return {"tier": user.role, "is_truncated": False, "total_count": 0, "data": []}

        latest_date = recent_5_dates[0]          # 가장 최신 거래일
        oldest_target_date = recent_5_dates[-1]   # 5번째 거래일
        recent_dates_set = set(recent_5_dates)

        # 2. 최근 5개 거래일 범위의 시그널 데이터 조회 (JOIN 제거하여 누락 버그 방지)
        acc_res = supabase.table("accumulation_signals") \
            .select("ticker, signal_date, close_price, day_return, score") \
            .gte("signal_date", oldest_target_date) \
            .limit(5000) \
            .execute()

        bet_res = supabase.table("closing_bet_signals") \
            .select("ticker, signal_date, close_price, day_return, score") \
            .gte("signal_date", oldest_target_date) \
            .limit(5000) \
            .execute()

        acc_rows = acc_res.data or []
        bet_rows = bet_res.data or []

        # 3. 종목별 날짜 집계
        stock_map: Dict[str, Dict[str, Any]] = {}

        def get_or_create(ticker: str):
            if ticker not in stock_map:
                stock_map[ticker] = {
                    "ticker": ticker,
                    "name": "",
                    "close_price": 0,
                    "day_return": 0.0,
                    "acc_dates": set(),
                    "bet_dates": set(),
                    "latest_acc_score": 0.0,
                    "latest_bet_score": 0.0,
                    "latest_signal_date": ""
                }
            return stock_map[ticker]

        # 세력매집 시그널 매핑
        for row in acc_rows:
            s_date = clean_date_str(row.get("signal_date"))
            if s_date not in recent_dates_set:
                continue
            ticker = str(row["ticker"]).strip().zfill(6)
            item = get_or_create(ticker)
            item["acc_dates"].add(s_date)
            
            if s_date >= item["latest_signal_date"]:
                item["close_price"] = row.get("close_price") or item["close_price"]
                item["day_return"] = float(row.get("day_return") or 0.0)
                item["latest_acc_score"] = float(row.get("score") or 0.0)
                item["latest_signal_date"] = s_date

        # 종가배팅 시그널 매핑
        for row in bet_rows:
            s_date = clean_date_str(row.get("signal_date"))
            if s_date not in recent_dates_set:
                continue
            ticker = str(row["ticker"]).strip().zfill(6)
            item = get_or_create(ticker)
            item["bet_dates"].add(s_date)

            if s_date >= item["latest_signal_date"]:
                item["close_price"] = row.get("close_price") or item["close_price"]
                item["day_return"] = float(row.get("day_return") or 0.0)
                item["latest_bet_score"] = float(row.get("score") or 0.0)
                item["latest_signal_date"] = s_date

        # 4. 조건 필터링:
        # ① 5거래일 중 세력매집 2회 이상 (acc_days >= 2)
        # ② 5거래일 중 종가배팅 2회 이상 (bet_days >= 2)
        # ③ 5거래일 중 세력매집 1회 이상 & 종가배팅 1회 이상 (크로스 일치)
        filtered_stocks = []
        target_tickers = []

        for ticker, info in stock_map.items():
            acc_cnt = len(info["acc_dates"])
            bet_cnt = len(info["bet_dates"])

            is_acc_repeat = (acc_cnt >= 2)
            is_bet_repeat = (bet_cnt >= 2)
            is_cross_matched = (acc_cnt >= 1 and bet_cnt >= 1)

            if is_acc_repeat or is_bet_repeat or is_cross_matched:
                total_active_days = len(info["acc_dates"].union(info["bet_dates"]))
                is_today = (latest_date in info["acc_dates"]) or (latest_date in info["bet_dates"])

                base_score = max(info["latest_acc_score"], info["latest_bet_score"])
                bonus = (acc_cnt * 2) + (bet_cnt * 2) + (5 if is_cross_matched else 0)
                composite_score = round(base_score + bonus, 1)

                record = {
                    "ticker": ticker,
                    "name": ticker, # 종목명 조회 전 기본값
                    "close_price": info["close_price"],
                    "day_return": info["day_return"],
                    "acc_days": acc_cnt,
                    "bet_days": bet_cnt,
                    "total_days": total_active_days,
                    "is_acc_repeat": is_acc_repeat,
                    "is_bet_repeat": is_bet_repeat,
                    "is_cross_matched": is_cross_matched,
                    "is_today": is_today,
                    "composite_score": composite_score
                }
                filtered_stocks.append(record)
                target_tickers.append(ticker)

        # 5. 종목명(Name) 안전 매핑 (stocks 테이블에서 별도 조회)
        if target_tickers:
            stocks_res = supabase.table("stocks") \
                .select("ticker, name") \
                .in_("ticker", target_tickers) \
                .execute()
            name_dict = {str(r["ticker"]).strip().zfill(6): r.get("name") for r in (stocks_res.data or [])}

            for item in filtered_stocks:
                item["name"] = name_dict.get(item["ticker"]) or item["ticker"]

        # 정렬: 오늘 포착 우선 -> 크로스 포착 우선 -> 총 노출일수 -> 복합점수 순
        filtered_stocks.sort(
            key=lambda x: (x["is_today"], x["is_cross_matched"], x["total_days"], x["composite_score"]), 
            reverse=True
        )

        # 6. 유저 권한별 처리
        if user.role == "PRO" and user.subscription_status == "DEACTIVE":
            return {
                "tier": "PENDING",
                "is_truncated": True,
                "message": "현재 관리자 승인 대기 중입니다.",
                "total_count": len(filtered_stocks),
                "data": filtered_stocks[:2]
            }

        if user.role == "USER":
            return {
                "tier": "FREE",
                "is_truncated": True,
                "message": "PRO 구독 시 5일 중복 분석 전체 종목을 확인하실 수 있습니다.",
                "total_count": len(filtered_stocks),
                "data": filtered_stocks[:3]
            }

        return {
            "tier": user.role,
            "is_truncated": False,
            "message": "",
            "total_count": len(filtered_stocks),
            "data": filtered_stocks
        }

    except Exception as e:
        print(f"[CrossAnalysis Error] {e}")
        return {"tier": user.role, "is_truncated": False, "total_count": 0, "data": []}