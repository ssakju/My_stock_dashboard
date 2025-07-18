# scripts/update_data.py
import os, json, requests
from datetime import datetime

# 환경변수로 저장하거나 직접 입력 가능합니다.
APP_KEY = os.getenv("KIS_APP_KEY", "PSbF6pKypYw2g5ua17ncklCuBCOkIMRZOjEt")
APP_SECRET = os.getenv("KIS_APP_SECRET", "n+hYBO/M48toc7cKLqUgMZIlAftvv/HuSggc8hlDhBKlbqHMORoCvpBd9YJc2jaNxMNkuqFrGDHRd3sRvBvXwVrusyjajq0rxOYqaA8Icwkdq/5U78yVk+DULSnPK6eKX40fAPIllXYS2qGYslb0f1y9o3MuIoge9wa0Rr93uR2YzSy7uNU=")

def get_token():
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    data = {"grant_type":"client_credentials","appkey":APP_KEY,"appsecret":APP_SECRET}
    res = requests.post(url, json=data)
    res.raise_for_status()
    return res.json()["access_token"]

# 예: 해외주식 상승률 순위 상위 100개
def fetch_top_fluctuation(token, limit=100):
    url = "https://openapi.koreainvestment.com:9443/uapi/overseas-stock/v1/ranking/fluctuation"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "Content-Type": "application/json"
    }
    params = {"fid_cond_mrkt_div_code": "US", "fid_input_iscd": "", "fid_output_iscd": "", "fid_trdvol": "", "fid_commdiv": "", "fid_contpage": "1", "fid_perent": limit}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res.json()["output"]

def main():
    token = get_token()
    top_list = fetch_top_fluctuation(token)

    os.makedirs("data", exist_ok=True)
    with open("data/top100.json", "w") as f:
        json.dump(top_list, f, indent=2, ensure_ascii=False)
    print("✅ top100.json updated at", datetime.now())

if __name__ == "__main__":
    main()