import requests
import pandas as pd
from datetime import datetime, timedelta
import io

def set_url(day_before):
    # 昨日の日付をMMDD形式で取得
    yesterday = datetime.now() - timedelta(days=day_before)
    date_str = yesterday.strftime("%m%d")
    # CSVのURLを設定
    total_amount_url = f"https://www.data.jma.go.jp/stats/data/mdrr/snc_rct/alltable/smsnd_sm{date_str}.csv"
    recent_amount_url = f"https://www.data.jma.go.jp/stats/data/mdrr/snc_rct/alltable/snd72h{date_str}.csv"
    return total_amount_url, recent_amount_url, date_str

# CSVデータを取得する関数
def fetch_csv(url):
    response = requests.get(url)
    # HTTPエラーがあれば例外を発生させる
    response.raise_for_status()
    # 取得したCSVデータを文字列に変換（shift_jisエンコーディング）
    content = response.content.decode('shift_jis')
    # 文字列からDataFrameに読み込む
    df = pd.read_csv(io.StringIO(content))
    df.fillna(0, inplace=True)
    return df

# 観測所番号を指定して降雪量を取得する関数
def get_local_amount(location_id):
    try:
        total_amount_url, recent_amount_url, date_str = set_url(1)
        total_amount_df = fetch_csv(total_amount_url)
        recent_amount_df = fetch_csv(recent_amount_url)
    except Exception:
        total_amount_url, recent_amount_url, date_str = set_url(2)
        total_amount_df = fetch_csv(total_amount_url)
        recent_amount_df = fetch_csv(recent_amount_url)
    local_total_amount = total_amount_df[total_amount_df["観測所番号"] == location_id]["累積降雪量（cm）"].values[0]
    local_recent_amount = recent_amount_df[recent_amount_df["観測所番号"] == location_id][f"{int(date_str[2:])}日の最大値(cm)"].values[0]
    local_omount_dict = {
        "total": f"{local_total_amount}cm",
        "recent": f"{local_recent_amount}cm"
    }
    return local_omount_dict

# テスト用のコード
if __name__ == "__main__":
    location_id = 48141
    local_amount = get_local_amount(location_id)
    print(local_amount)