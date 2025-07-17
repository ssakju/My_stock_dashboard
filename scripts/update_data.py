# scripts/update_data.py

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os
import time
import requests
from io import StringIO

def get_all_us_stocks():
    """미국 전체 상장 종목 리스트 수집"""
    urls = {
        "nasdaq": "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
        "other": "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
    }

    dfs = []

    for name, url in urls.items():
        r = requests.get(url)
        text = r.text
        text = text.strip().split('\n')
        # 마지막 줄 제거 (파일정보)
        text = "\n".join(text[:-1])
        df = pd.read_csv(StringIO(text), sep='|')
        if 'Symbol' in df.columns:
            dfs.append(df[['Symbol']])
        elif 'ACT Symbol' in df.columns:
            dfs.append(df[['ACT Symbol']].rename(columns={'ACT Symbol': 'Symbol'}))

    all_symbols = pd.concat(dfs)['Symbol'].drop_duplicates().tolist()
    return [s for s in all_symbols if '^' not in s and '/' not in s]

# 전체 미국 티커 목록
ticker_list = get_all_us_stocks()

print(f"📦 종목 수집 완료: 총 {len(ticker_list)}개")

result = []

for i, symbol in enumerate(ticker_list):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d', interval='5m')

        if hist.empty or 'Open' not in hist.columns or 'Close' not in hist.columns:
            continue

        current_price = hist['Close'][-1]
        open_price = hist['Open'][0]

        if open_price == 0 or current_price == 0:
            continue

        percent_change = ((current_price - open_price) / open_price) * 100
        total_volume = hist['Volume'].sum()

        result.append({
            'symbol': symbol,
            'change': round(percent_change, 2),
            'volume': int(total_volume),
            'data': hist['Close'].tail(20).tolist(),
            'timestamps': [t.strftime('%H:%M') for t in hist.index[-20:]]
        })

        print(f"{i+1}/{len(ticker_list)} ✔ {symbol} {round(percent_change,2)}%")

        time.sleep(0.1)  # 요청 제한 우회용 (yfinance 10~12초당 5개 권장)

    except Exception as e:
        print(f"{i+1}/{len(ticker_list)} ⚠️ {symbol} 오류: {e}")
        continue

# 상승률 기준 정렬 후 상위 100
top100 = sorted(result, key=lambda x: x['change'], reverse=True)[:100]

# 저장
os.makedirs('data', exist_ok=True)
with open('data/top100.json', 'w') as f:
    json.dump(top100, f, indent=2)

print("✅ top100.json updated at", datetime.now())
