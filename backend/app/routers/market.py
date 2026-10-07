import datetime
from fastapi import APIRouter
import FinanceDataReader as fdr
import pandas as pd

router = APIRouter(prefix="/api/market", tags=["Market"])

def get_market_snapshot():
    """
    네이버/KRX 통합 주가 마스터 데이터를 가져와 상태 라벨과 함께 반환
    """
    now = datetime.datetime.now()
    weekday = now.weekday()
    hour_minute = now.hour * 100 + now.minute

    # 시간대별 상태 문구 판별
    if weekday >= 5:
        status_label = "최근 거래일"
    elif hour_minute < 900:
        status_label = "전일"
    elif 900 <= hour_minute < 1530:
        status_label = "당일 (장중)"
    else:
        status_label = "당일"

    # KRX 전체 종목의 최신 시세 및 거래대금 일괄 조회 (초당 응답)
    df = fdr.StockListing('KRX')
    
    # 필수 컬럼 정리: Code(ticker), Name(name), Close(close), ChagesRatio(change_rate), Amount(trading_value), Marcap(market_cap)
    df = df.rename(columns={
        'Code': 'ticker',
        'Name': 'name',
        'Close': 'close',
        'Chg': 'change_rate',
        'ChagesRatio': 'change_rate',
        'Amount': 'trading_value',
        'Marcap': 'market_cap'
    })

    # 결측치 정제
    df['close'] = pd.to_numeric(df['close'], errors='coerce').fillna(0).astype(int)
    df['change_rate'] = pd.to_numeric(df['change_rate'], errors='coerce').fillna(0.0)
    df['trading_value'] = pd.to_numeric(df['trading_value'], errors='coerce').fillna(0).astype(int)
    df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce').fillna(0).astype(int)

    target_date = now.strftime("%Y%m%d")
    return target_date, status_label, df

@router.get("/volume-top50")
def get_volume_top50():
    try:
        target_date, status_label, df = get_market_snapshot()
        top50 = df.sort_values(by="trading_value", ascending=False).head(50)

        result = []
        for _, row in top50.iterrows():
            result.append({
                "ticker": str(row["ticker"]),
                "name": str(row["name"]),
                "close": int(row["close"]),
                "change_rate": round(float(row["change_rate"]), 2),
                "volume": 0,
                "trading_value": int(row["trading_value"])
            })

        return {"date": target_date, "status_label": status_label, "data": result}
    except Exception as e:
        print(f"volume-top50 처리 실패: {e}")
        return {"date": "", "status_label": "데이터 오류", "data": []}

@router.get("/indicators-top10")
def get_market_indicators_top10():
    try:
        target_date, status_label, df = get_market_snapshot()

        # 급등 TOP 10
        gainers_df = df.sort_values(by="change_rate", ascending=False).head(10)
        gainers = [{
            "ticker": str(r["ticker"]),
            "name": str(r["name"]),
            "close": int(r["close"]),
            "change_rate": round(float(r["change_rate"]), 2)
        } for _, r in gainers_df.iterrows()]

        # 급락 TOP 10
        losers_df = df.sort_values(by="change_rate", ascending=True).head(10)
        losers = [{
            "ticker": str(r["ticker"]),
            "name": str(r["name"]),
            "close": int(r["close"]),
            "change_rate": round(float(r["change_rate"]), 2)
        } for _, r in losers_df.iterrows()]

        # 시총 TOP 10
        caps_df = df.sort_values(by="market_cap", ascending=False).head(10)
        caps = [{
            "ticker": str(r["ticker"]),
            "name": str(r["name"]),
            "market_cap": int(r["market_cap"]),
            "close": int(r["close"])
        } for _, r in caps_df.iterrows()]

        return {
            "date": target_date,
            "status_label": status_label,
            "gainers": gainers,
            "losers": losers,
            "caps": caps
        }
    except Exception as e:
        print(f"indicators-top10 처리 실패: {e}")
        return {"date": "", "status_label": "데이터 오류", "gainers": [], "losers": [], "caps": []}