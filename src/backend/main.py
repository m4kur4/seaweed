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
    # DBから日付順(昇順)で全件取得
    transactions = db.query(models.Transaction).order_by(models.Transaction.transaction_date.asc()).all()
    response_data = []
    current_balance = 0 # 累積残高

    # 過去のデータから順にループを回し、その時点の残高(基準額)を計算する
    for t in transactions:
        # 当日の処理が始まる前の時点の残高が「基準額 (0:00時点の貯金額)となｒ
        baseline_amount = current_balance
        if t.transaction_type == "income":
            current_balance += t.transaction_amount
        else:
            current_balance -= t.transaction_amount

        response_data.append({
            "transaction_date": t.transaction_date,
            "transaction_amount": t.transaction_amount,
            "transaction_type": t.transaction_type,
            "description": t.description,
            "baseline_amount": baseline_amount,
            "current_balance": current_balance
        })
    # 最新のデータが上に来るように、最終的には日付の降順にひっくり返してフロントへ返す
    response_data.reverse()

    return {
        "status": "success",
        "data_count": len(transactions),
        "transactions": response_data
    }

# データ登録用のエンドポイント
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