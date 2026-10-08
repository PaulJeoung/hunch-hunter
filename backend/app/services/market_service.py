import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List
import FinanceDataReader as fdr
import pandas as pd
import requests

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.stock.naver.com/"
})


def get_market_status():
    now = datetime.datetime.now()
    weekday = now.weekday()
    hour_minute = now.hour * 100 + now.minute

    if weekday >= 5:
        status_label = "최근 거래일"
    elif hour_minute < 900:
        status_label = "전일"
    elif 900 <= hour_minute < 2000:
        status_label = "당일 (장중)"
    else:
        status_label = "당일"

    target_date = now.strftime("%Y%m%d")
    return target_date, status_label


def parse_val(val) -> float:
    if val is None:
        return 0.0
    s = str(val).replace(",", "").replace("+", "").replace("%", "").strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def fetch_m_naver(endpoint_type: str, market: str, page_size: int = 50) -> list:
    url = f"https://m.stock.naver.com/api/stocks/{endpoint_type}/{market}?page=1&pageSize={page_size}"
    try:
        res = SESSION.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                return data.get("stocks") or data.get("data") or []
            elif isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def get_stock_detail_naver(ticker: str, close_price: int) -> dict:
    safe_ticker = str(ticker).strip().zfill(6)
    execution_strength = None
    foreign_net = 0
    institution_net = 0
    individual_net = None
    market_cap = 0

    url_int = f"https://m.stock.naver.com/api/stock/{safe_ticker}/integration"
    try:
        res = SESSION.get(url_int, timeout=2.5)
        if res.status_code == 200:
            data = res.json()
            deal_trend = data.get("dealTrend", {})
            total_infos = data.get("totalInfos", [])

            if "executionStrength" in deal_trend:
                execution_strength = parse_val(deal_trend.get("executionStrength"))

            for info in total_infos:
                code_key = info.get("code")
                if code_key == "marketValue" or "시가총액" in str(info.get("key", "")):
                    market_cap = int(parse_val(info.get("value")))
    except Exception:
        pass

    if execution_strength is None or market_cap == 0:
        try:
            url_basic = f"https://m.stock.naver.com/api/stock/{safe_ticker}/basic"
            res = SESSION.get(url_basic, timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                if execution_strength is None and "executionStrength" in data:
                    execution_strength = parse_val(data.get("executionStrength"))
                if market_cap == 0 and "marketValue" in data:
                    market_cap = int(parse_val(data.get("marketValue")))
        except Exception:
            pass

    url_trend = f"https://m.stock.naver.com/api/stock/{safe_ticker}/trend"
    try:
        res = SESSION.get(url_trend, timeout=2.5)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                latest = data[0]
                f_qty = int(parse_val(latest.get("foreignerPureBuyQuant") or latest.get("foreignPureBuyQuant")))
                i_qty = int(parse_val(latest.get("organPureBuyQuant") or latest.get("institutionPureBuyQuant")))
                
                foreign_net = int(f_qty * close_price)
                institution_net = int(i_qty * close_price)

                if "individualPureBuyQuant" in latest and latest.get("individualPureBuyQuant") is not None:
                    p_qty = int(parse_val(latest.get("individualPureBuyQuant")))
                    individual_net = int(p_qty * close_price)
    except Exception:
        pass

    return {
        "execution_strength": round(execution_strength, 1) if execution_strength is not None else None,
        "market_cap": market_cap,
        "foreign_net": foreign_net,
        "institution_net": institution_net,
        "individual_net": individual_net
    }


def get_fallback_krx_df() -> pd.DataFrame:
    try:
        df = fdr.StockListing('KRX')
        col_map = {}
        for col in df.columns:
            c = col.lower()
            if c in ['code', 'ticker', 'symbol']: col_map[col] = 'ticker'
            elif c in ['name', '종목명']: col_map[col] = 'name'
            elif c in ['close', '종가']: col_map[col] = 'close'
            elif c in ['changesratio', 'chagesratio', 'chg', 'changerate', '등락률']: col_map[col] = 'change_rate'
            elif c in ['amount', 'trading_value', '거래대금']: col_map[col] = 'trading_value'
            elif c in ['marcap', 'market_cap', '시가총액']: col_map[col] = 'market_cap'
        df = df.rename(columns=col_map)
        for col in ['close', 'change_rate', 'trading_value', 'market_cap']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.replace('+', '', regex=False).str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
        return df[df['close'] > 0].copy()
    except Exception:
        return pd.DataFrame()


def get_volume_top50_data() -> Dict[str, Any]:
    target_date, status_label = get_market_status()
    raw_list = []

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            fut_p = executor.submit(fetch_m_naver, "tradingValue", "KOSPI", 50)
            fut_d = executor.submit(fetch_m_naver, "tradingValue", "KOSDAQ", 50)
            raw_items = fut_p.result() + fut_d.result()

        for item in raw_items:
            t = str(item.get("itemCode", "")).strip().zfill(6)
            if t and t != "000000":
                tv_val = parse_val(item.get("accumulatedTradingValue") or item.get("tradingValue") or 0)
                real_trading_val = int(tv_val * 1_000_000) if (0 < tv_val < 50_000_000) else int(tv_val)

                raw_list.append({
                    "ticker": t,
                    "name": str(item.get("stockName", "")),
                    "close": int(parse_val(item.get("closePrice"))),
                    "change_rate": round(parse_val(item.get("fluctuationsRatio")), 2),
                    "trading_value": real_trading_val,
                    "market_cap": int(parse_val(item.get("marketValue", 0)))
                })
    except Exception:
        pass

    if not raw_list:
        df = get_fallback_krx_df()
        if not df.empty:
            top_df = df.sort_values(by="trading_value", ascending=False).head(50)
            for _, row in top_df.iterrows():
                raw_list.append({
                    "ticker": str(row["ticker"]).strip().zfill(6),
                    "name": str(row["name"]),
                    "close": int(row["close"]),
                    "change_rate": round(float(row["change_rate"]), 2),
                    "trading_value": int(row["trading_value"]),
                    "market_cap": int(row["market_cap"])
                })

    top50 = sorted(raw_list, key=lambda x: x["trading_value"], reverse=True)[:50]

    def enrich_stock(stock_item):
        detail = get_stock_detail_naver(stock_item["ticker"], stock_item["close"])
        m_cap = stock_item["market_cap"] if stock_item["market_cap"] > 0 else detail["market_cap"]
        return {
            **stock_item,
            "market_cap": m_cap,
            "execution_strength": detail["execution_strength"],
            "foreign_net": detail["foreign_net"],
            "institution_net": detail["institution_net"],
            "individual_net": detail["individual_net"]
        }

    with ThreadPoolExecutor(max_workers=10) as executor:
        enriched_results = list(executor.map(enrich_stock, top50))

    return {
        "date": target_date,
        "status_label": status_label,
        "data": enriched_results
    }


def get_market_indicators_top10_data() -> Dict[str, Any]:
    target_date, status_label = get_market_status()
    gainers, losers, caps = [], [], []

    try:
        with ThreadPoolExecutor(max_workers=6) as executor:
            fut_up_p = executor.submit(fetch_m_naver, "rising", "KOSPI", 15)
            fut_up_d = executor.submit(fetch_m_naver, "rising", "KOSDAQ", 15)
            fut_dn_p = executor.submit(fetch_m_naver, "falling", "KOSPI", 15)
            fut_dn_d = executor.submit(fetch_m_naver, "falling", "KOSDAQ", 15)
            fut_cp_p = executor.submit(fetch_m_naver, "marketValue", "KOSPI", 10)
            fut_cp_d = executor.submit(fetch_m_naver, "marketValue", "KOSDAQ", 10)

            up_items = fut_up_p.result() + fut_up_d.result()
            dn_items = fut_dn_p.result() + fut_dn_d.result()
            cp_items = fut_cp_p.result() + fut_cp_d.result()

        for item in up_items:
            t = str(item.get("itemCode", "")).strip().zfill(6)
            if t and t != "000000":
                gainers.append({
                    "ticker": t,
                    "name": str(item.get("stockName", "")),
                    "close": int(parse_val(item.get("closePrice"))),
                    "change_rate": round(parse_val(item.get("fluctuationsRatio")), 2)
                })

        for item in dn_items:
            t = str(item.get("itemCode", "")).strip().zfill(6)
            if t and t != "000000":
                losers.append({
                    "ticker": t,
                    "name": str(item.get("stockName", "")),
                    "close": int(parse_val(item.get("closePrice"))),
                    "change_rate": round(parse_val(item.get("fluctuationsRatio")), 2)
                })

        for item in cp_items:
            t = str(item.get("itemCode", "")).strip().zfill(6)
            if t and t != "000000":
                caps.append({
                    "ticker": t,
                    "name": str(item.get("stockName", "")),
                    "market_cap": int(parse_val(item.get("marketValue", 0))),
                    "close": int(parse_val(item.get("closePrice")))
                })

        if gainers and losers and caps:
            gainers = sorted([g for g in gainers if g["change_rate"] > 0], key=lambda x: x["change_rate"], reverse=True)[:10]
            losers = sorted([l for l in losers if l["change_rate"] < 0], key=lambda x: x["change_rate"])[:10]
            caps = sorted(caps, key=lambda x: x["market_cap"], reverse=True)[:10]
            return {
                "date": target_date,
                "status_label": status_label,
                "gainers": gainers,
                "losers": losers,
                "caps": caps
            }
    except Exception:
        pass

    df = get_fallback_krx_df()
    if not df.empty:
        g_df = df[df['change_rate'] > 0].sort_values(by="change_rate", ascending=False).head(10)
        gainers = [{"ticker": str(r["ticker"]).zfill(6), "name": str(r["name"]), "close": int(r["close"]), "change_rate": round(float(r["change_rate"]), 2)} for _, r in g_df.iterrows()]
        l_df = df[df['change_rate'] < 0].sort_values(by="change_rate", ascending=True).head(10)
        losers = [{"ticker": str(r["ticker"]).zfill(6), "name": str(r["name"]), "close": int(r["close"]), "change_rate": round(float(r["change_rate"]), 2)} for _, r in l_df.iterrows()]
        c_df = df.sort_values(by="market_cap", ascending=False).head(10)
        caps = [{"ticker": str(r["ticker"]).zfill(6), "name": str(r["name"]), "market_cap": int(r["market_cap"]), "close": int(r["close"])} for _, r in c_df.iterrows()]

    return {"date": target_date, "status_label": status_label, "gainers": gainers, "losers": losers, "caps": caps}