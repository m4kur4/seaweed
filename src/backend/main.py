from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORSの設定
# フロントエンド開発サーバーURLを許可
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 全てのHTTPメソッドを許可
    allow_headers=["*"], # 全てのヘッダを許可
)

@app.get("/")
def read_root():
    return {"message": "Hello, seaweed! FastAPI is running."}

# テスト用
@app.get("/api/wakame")
def get_wakame_status():
    return {
        "status": "乾燥ワカメ",
        "length_cm": 5,
        "message": "まだ水が足りません！"
    }