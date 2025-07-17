# scripts/update_data.py

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os

# S&P500 리스트 (또는 임의의 대형주 리스트)
ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

result = []

for symbol in ticker_list[:200]:  # 상위 200개만 시도
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d', interval='5m')
        if hist.empty or 'Close' not in hist.columns:
            continue
        open_price = hist['Open'][0]
        close_price = hist['Close'][-1]
        percent_change = ((close_price - open_price) / open_price) * 100
        total_volume = hist['Volume'].sum()

        result.append({
            'symbol': symbol,
            'change': round(percent_change, 2),
            'volume': int(total_volume),
            'data': hist['Close'].tail(20).tolist(),  # 마지막 20개 점 (약 100분)
            'timestamps': [t.strftime('%H:%M') for t in hist.index[-20:]]
        })

    except Exception as e:
        continue

# 정렬
top100 = sorted(result, key=lambda x: x['change'], reverse=True)[:100]

# 디렉터리 생성
os.makedirs('data', exist_ok=True)

with open('data/top100.json', 'w') as f:
    json.dump(top100, f, indent=2)

print("✅ top100.json updated")
