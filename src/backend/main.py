from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

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
        # "transactions": transactions
        "transactions": [
            schemas.TransactionRead.model_validate(t) for t in transactions
        ]
    }

# # データ登録用のエンドポイント
@app.post("/api/transactions", status_code=status.HTTP_201_CREATED)
def create_transactions(
    transaction_in: schemas.TransactionCreate,
    db: Session = Depends(get_db)
) -> dict:

    # 変動種別の簡易バリデーション
    if transaction_in.transaction_type not in ["income", "expense"]: # TODO: const
        raise HTTPException(
            status_code=400,
            detail="変動種別は 'income' または 'expense' で指定してください。"
        )

    # データベースのモデルに変換してレコードを作成
    db_transaction = models.Transaction(
        transaction_date=transaction_in.transaction_date,
        transaction_amount=transaction_in.transaction_amount,
        transaction_type=transaction_in.transaction_type,
        description=transaction_in.description,
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return {"status": "success", "message": "データを登録しました。"}