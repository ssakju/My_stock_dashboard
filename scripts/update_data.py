import os
import json
from datetime import datetime
from korea_investment_api import KoreaInvestmentAPI

# ⛳ 환경변수 또는 직접 입력
APP_KEY = os.getenv("KIS_APP_KEY") or "발급받은_APP_KEY"
APP_SECRET = os.getenv("KIS_APP_SECRET") or "발급받은_APP_SECRET"
ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO") or "12345678-01"

# ✅ API 초기화 (모의투자: virtual=True)
api = KoreaInvestmentAPI(APP_KEY, APP_SECRET, virtual=True)

def fetch_top_us_stocks(limit=100):
    """
    상승률 기준 상위 미국 주식 티커를 가져옵니다.
    """
    print("📡 미국 주식 상승률 상위 티커 조회 중...")
    market_data = api.get_us_price_all()  # 전체 미국 종목 시세
    sorted_by_change = sorted(
        market_data, key=lambda x: float(x['fluctuation_rate']), reverse=True
    )
    return sorted_by_change[:limit]

def fetch_price_history(symbol):
    """
    5분봉 가격 이력을 받아옵니다.
    """
    try:
        df = api.get_us_minute_chart(symbol=symbol, interval="5")  # 5분봉
        if df.empty:
            return None

        open_price = float(df.iloc[0]["open"])
        close_price = float(df.iloc[-1]["close"])
        percent_change = ((close_price - open_price) / open_price) * 100
        volume = df["volume"].astype(float).sum()

        return {
            "symbol": symbol,
            "change": round(percent_change, 2),
            "volume": int(volume),
            "data": df["close"].astype(float).tolist(),
            "timestamps": df["date"].tolist()
        }

    except Exception as e:
        print(f"⚠️ {symbol} 오류: {e}")
        return None

def main():
    print("🚀 미국 실시간 상승률 상위 종목 분석 시작")
    top_symbols = fetch_top_us_stocks(limit=100)

    results = []
    for item in top_symbols:
        symbol = item["symbol"]
        print(f"📈 {symbol} 데이터 수집 중...")
        data = fetch_price_history(symbol)
        if data:
            results.append(data)

    os.makedirs("data", exist_ok=True)
    with open("data/top100.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✅ top100.json 파일 업데이트 완료")

if __name__ == "__main__":
    main()