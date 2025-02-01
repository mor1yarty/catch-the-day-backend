from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from getWeatherInfo.jma_opendata_snowamount import get_local_amount
from getWeatherInfo.jma_api_weatherforcast import get_weather_info

app = FastAPI()

# CORSの設定 フロントエンドからの接続を許可する部分
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

# キャッシュデータ
cached_area = None

@app.get("/")
def hello():
    return {"message": "FastAPI hello!"}

@app.get("/api/hello")
def hello_world():
    return {"message": "Hello World by FastAPI"}

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
    wheather_forcast = get_weather_info(area_dict[echo_message]["group"])
    snow_amount = get_local_amount(area_dict[echo_message]["locacion_id"])
    return {"message": f"積雪量: {snow_amount} 天気予報: {wheather_forcast}"}