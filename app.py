from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from getWeatherInfo.jma_opendata_snowamount import get_local_amount
from getWeatherInfo.jma_api_weatherforcast import get_weather_info
import base64

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
    "白馬":{"group":"北部", "locacion_id":48141},
    "志賀高原":{"group":"北部", "locacion_id":48066},
    "野沢温泉":{"group":"北部", "locacion_id":48031},
    "斑尾・妙高":{"group":"北部", "locacion_id":48061},
    "菅平":{"group":"中部", "locacion_id":48216},
    "木曽":{"group":"南部", "locacion_id":48531},
}

# 画像をBase64に変換
image_path = "src/the_day.jpg"
with open(image_path, "rb") as img_file:
    base64_image = base64.b64encode(img_file.read()).decode("utf-8")

# キャッシュデータ
cached_area = None

@app.get("/")
def hello():
    return {"message": "FastAPI hello!"}

@app.get("/api/hello")
def hello_world():
    response_data = {
        "image": base64_image,  # Base64エンコードした画像データ
        "message": "天気は雲ひとつない快晴で、雪面はふかふかのパウダースノー。\n一見すると相反するこのコンディションとは、シーズンを通しても片手で数えるほどしか出会えない。\nそんな最高の1日をスノーボーダーは「THE DAY.」と表現する。"
    }
    return response_data

@app.get("/api/multiply/{id}")
def multiply(id: int):
    print("multiply")
    doubled_value = id * 2
    return {"doubled_value": doubled_value}

@app.post("/api/echo")
def echo(message: EchoMessage):
    print("echo")
    if not message:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    echo_message = message.message if message.message else "No message provided"
    weather_forcast = get_weather_info(area_dict[echo_message]["group"])
    snow_amount = get_local_amount(area_dict[echo_message]["locacion_id"])
    return {"snow_amount": snow_amount, "weather_forcast": weather_forcast}