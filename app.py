from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from getWeatherInfo.jma_opendata_snowamount import get_local_amount
# from getWeatherInfo.jma_api_weatherforcast import get_weather_info
from getWeatherInfo.owm_api_weatherforcast import get_weather_info
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# CORSの設定 フロントエンドからの接続を許可する部分
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# JSONのスキーマ。'area'と'date'のフィールドを定義
class EchoMessage(BaseModel):
    area: str | None = None
    date: str | None = None

# 許容するエリアの値
area_dict = {
    "白馬":{"group":"北部", "locacion_id":48141, "lat":36.7, "lon":137.85},
    "志賀高原":{"group":"北部", "locacion_id":48066, "lat":36.7, "lon":138.4},
    "野沢温泉":{"group":"北部", "locacion_id":48031, "lat":36.9, "lon":138.4},
    "斑尾・妙高":{"group":"北部", "locacion_id":48061, "lat":36.9, "lon":138.2},
    "菅平":{"group":"中部", "locacion_id":48216, "lat":36.3, "lon":138.4},
    "木曽":{"group":"南部", "locacion_id":48531, "lat":35.9, "lon":137.7},
}

# 許容する日付の値
dates_dict = {
    "今日":0,
    "明日":1,
    "明後日":2,
    "3日後":3,
    "4日後":4,
    "5日後":5
}

# 天候データのキャッシュデータ取得
weatherinfo_cache = {
    "cache_date": None,
    "weatherinfo": {},
    "snow_amount": {}
}

# 'src'ディレクトリ内のファイルを '/static' パスで公開
app.mount("/static", StaticFiles(directory="src"), name="static")

@app.get("/")
def hello():
    return {"message": "FastAPI hello!"}

@app.get("/api/hello")
def hello_world():
    response_data = {
        "message": "天気は雲ひとつない快晴で、雪面はふかふかのパウダースノー。\n一見すると相反するこのコンディションとは、シーズンを通しても片手で数えるほどしか出会えない。\nそんな最高の1日をスノーボーダーは「THE DAY.」と表現する。"
    }
    return response_data

@app.post("/api/echo")
def echo(message: EchoMessage):
    # areaフィールドの存在チェック
    if not message.area:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON: 'area'フィールドに値を指定してください。"
        )
    # dateフィールドの存在チェック
    if not message.date:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON: 'date'フィールドに値を指定してください。"
        )

    # 前後の空白を除去
    area_value = message.area.strip()
    date_value = message.date.strip()

    # 入力されたエリアが許容リストに存在するかチェック
    if area_value not in area_dict:
        allowed = "、".join(area_dict.keys())
        raise HTTPException(
            status_code=400,
            detail=f"無効なエリアです。以下のいずれかを選んでください: {allowed}"
        )
    # 入力された日付が許容リストに存在するかチェック
    if date_value not in dates_dict:
        allowed_dates = "、".join(dates_dict.keys())
        raise HTTPException(
            status_code=400,
            detail=f"無効な日付です。以下のいずれかを選んでください: {allowed_dates}"
        )

    # 有効なエリアの場合、天気情報と雪量情報を取得する
    weather_forcast = get_weather_info(area_dict[message.area]["lat"], area_dict[message.area]["lon"], dates_dict[message.date])
    snow_amount = get_local_amount(area_dict[message.area]["locacion_id"])
    return {"snow_amount": snow_amount, "weather_forcast": weather_forcast}
