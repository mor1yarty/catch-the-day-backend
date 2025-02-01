# -*- coding:utf-8 -*-
import requests
from datetime import datetime, timedelta

# 明日の日付をMMDD形式で取得
tomorrow = datetime.now() + timedelta(days=1)
date_str = tomorrow.strftime("%Y-%m-%d")

def get_weather_info(selected_area):
    # 長野県の気象庁データの取得
    jma_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/200000.json"
    response = requests.get(jma_url)
    # HTTPエラーがあれば例外を発生させる
    response.raise_for_status()
    # ３日間の天気予報を取得
    response_daily = response.json()[0]["timeSeries"]
    
    # 翌日の降水確率を計算する関数
    def rain_func(area_index):
        rain_probability_list = []
        for i, time_index in enumerate(response_daily[1]["timeDefines"]):
            if time_index.split("T")[0] != date_str:
                continue
            rain_probability_list.append(int(response_daily[1]["areas"][area_index]["pops"][i]))
        rain_probability_results = f"{sum(rain_probability_list) / len(rain_probability_list)} %" if len(rain_probability_list) > 0 else "No Data."
        return rain_probability_results
    
    # 翌日の最高気温と最低気温を取得する関数
    def temp_func(area_index_list):
        temp_dict = {}
        for area_index in area_index_list:
            temp_list = []
            for i, time_index in enumerate(response_daily[2]["timeDefines"]):
                if time_index.split("T")[0] != date_str:
                    continue
                temp_list.append(response_daily[2]["areas"][area_index]["temps"][i])
            max_temp = f"{max(temp_list)} ℃" if len(temp_list) > 0 else "No Data."
            min_temp = f"{min(temp_list)} ℃" if len(temp_list) > 0 else "No Data."
            temp_dict[response_daily[2]["areas"][area_index]["area"]["name"]] = {
                "最高気温": max_temp,
                "最低気温": min_temp
            }
        return temp_dict
    
    # 集計結果を格納する辞書
    weather_dict = {
        "北部":{
            "天気": response_daily[0]["areas"][0]["weathers"][1].replace("　", " "),
            "降水確率": rain_func(0),
            "気温": temp_func([0])
        },
        "中部":{
            "天気": response_daily[0]["areas"][1]["weathers"][1].replace("　", " "),
            "降水確率": rain_func(1),
            "気温": temp_func([1, 2, 4])
        },
        "南部":{
            "天気": response_daily[0]["areas"][2]["weathers"][1].replace("　", " "),
            "降水確率": rain_func(2),
            "気温": temp_func([3])
        },
    }
    return weather_dict[selected_area]

if __name__ == "__main__":
    selected_area = "中部"
    results = get_weather_info(selected_area)
    print(results)