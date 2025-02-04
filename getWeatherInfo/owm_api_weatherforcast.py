# -*- coding:utf-8 -*-
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
if os.environ.get("APP_ENV", "development") == "development":
    load_dotenv()
OWM_API_KEY = os.environ.get("OWM_API_KEY")

# 明日の日付をMMDD形式で取得
tomorrow = datetime.now() + timedelta(days=1)
date_str = tomorrow.strftime("%Y-%m-%d")

weather_jpn = {
    "Snow": "雪",
    "Rain": "雨",
    "Clear": "晴れ",
    "Clouds": "曇り",
    "Thunderstorm": "雷雨",
    "Drizzle": "霧雨",
    "Mist": "霧",
    "Fog": "霧",
    "Haze": "霧",
    "Dust": "砂ぼこり",
    "Sand": "砂",
    "Ash": "火山灰",
    "Squall": "スコール",
    "Tornado": "竜巻"
}
def get_weather_info(lat, lon):
    # 指定した緯度経度の直近の気象予報データの取得
    jma_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&APPID={OWM_API_KEY}"
    response = requests.get(jma_url)
    # HTTPエラーがあれば例外を発生させる
    response.raise_for_status()
    weather_tomorrow_json = {}
    # 取得したデータから明日の日付のデータのみを抽出
    for weather in response.json()["list"]:
        if weather["dt_txt"].split(" ")[0] == date_str:
            weather_tomorrow_json[f'{weather["dt_txt"].split(" ")[1][:5]}'] = {
                "weather": weather_jpn[weather["weather"][0]["main"]],
                "temp": f'{round(weather["main"]["temp"] - 273.15, 1)}℃',
                "snow": weather["snow"]["3h"] if "snow" in weather else 0,
                "icon": weather["weather"][0]["icon"]
            }
    del weather_tomorrow_json["00:00"], weather_tomorrow_json["03:00"]
    return weather_tomorrow_json

if __name__ == "__main__":
    weahter_info = get_weather_info(36, 138)
    print(weahter_info)