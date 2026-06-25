from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
import models

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

# DB接続テスト用のエンドポイント
@app.get("/api/transactions")
def get_transactions(db: Session = Depends(get_db)):
    # models.Transactionクラスを使ってMySQLのtransactionsテーブルから全件取得
    transactions = db.query(models.Transaction).all()

    return {
        "status": "success",
        "data_count": len(transactions),
        "transactions": transactions
    }