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

# データのスキーマを定義するためのクラス
class EchoMessage(BaseModel):
    message: str | None = None

area_dict = {
    "白馬":{"group":"北部", "locacion_id":48141, "lat":36.7, "lon":137.85},
    "志賀高原":{"group":"北部", "locacion_id":48066, "lat":36.7, "lon":138.4},
    "野沢温泉":{"group":"北部", "locacion_id":48031, "lat":36.9, "lon":138.4},
    "斑尾・妙高":{"group":"北部", "locacion_id":48061, "lat":36.9, "lon":138.2},
    "菅平":{"group":"中部", "locacion_id":48216, "lat":36.3, "lon":138.4},
    "木曽":{"group":"南部", "locacion_id":48531, "lat":35.9, "lon":137.7},
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
    # messageフィールドが空の場合のチェック
    if not message.message:
        raise HTTPException(status_code=400, detail="Invalid JSON: 'message'フィールドに値を指定してください。")

    # 前後の空白を除去
    echo_message = message.message.strip()

    # 入力がarea_dictに存在するかチェック
    if echo_message not in area_dict:
        allowed = "、".join(area_dict.keys())
        raise HTTPException(
            status_code=400,
            detail=f"無効なエリアです。以下のいずれかを選んでください: {allowed}"
        )

    # 有効なエリアの場合、天気情報と雪量情報を取得する
    weather_forcast = get_weather_info(area_dict[echo_message]["lat"], area_dict[echo_message]["lon"])
    snow_amount = get_local_amount(area_dict[echo_message]["locacion_id"])
    return {"snow_amount": snow_amount, "weather_forcast": weather_forcast}
