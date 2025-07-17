# scripts/update_data.py

import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

def get_top_gainers(limit=100):
    """Yahoo Finance에서 실시간 상승률 상위 티커 리스트 가져오기"""
    url = "https://finance.yahoo.com/gainers"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.select('table tbody tr')

    symbols = []
    for row in rows:
        try:
            symbol = row.select('td')[0].text.strip()
            symbols.append(symbol)
            if len(symbols) >= limit:
                break
        except:
            continue

    return symbols


def fetch_ticker_data(symbol):
    """각 티커에 대한 5분봉 가격 데이터 수집 및 계산"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d', interval='5m')

        if hist.empty or 'Close' not in hist.columns or 'Open' not in hist.columns:
            return None

        open_price = hist['Open'][0]
        close_price = hist['Close'][-1]
        percent_change = ((close_price - open_price) / open_price) * 100
        total_volume = hist['Volume'].sum()

        return {
            'symbol': symbol,
            'change': round(percent_change, 2),
            'volume': int(total_volume),
            'data': hist['Close'].tail(20).tolist(),  # 최근 20개 (약 100분)
            'timestamps': [t.strftime('%H:%M') for t in hist.index[-20:]]
        }

    except Exception as e:
        return None


def main():
    print("📡 Fetching top gainers...")
    tickers = get_top_gainers(limit=100)

    result = []
    for symbol in tickers:
        print(f"⏳ Fetching {symbol}...")
        data = fetch_ticker_data(symbol)
        if data:
            result.append(data)

    # 정렬: 실제로는 이미 상승률 순이지만, 안전하게 다시 한 번 정렬
    top100 = sorted(result, key=lambda x: x['change'], reverse=True)[:100]

    os.makedirs('data', exist_ok=True)
    with open('data/top100.json', 'w') as f:
        json.dump(top100, f, indent=2)

    print("✅ top100.json updated")


if __name__ == "__main__":
    main()
