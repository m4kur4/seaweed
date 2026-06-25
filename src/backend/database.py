import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# .env ファイルから環境変数を読み込む
# Docker 実行時は docker-compose が注入した環境変数が優先される
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "seaweed_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "seaweed_pass")
DB_NAME = os.getenv("DB_NAME", "seaweed_db")
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset={DB_CHARSET}"
)

# DBエンジンの作成
# NOTE: MySQLは8時間無操作の接続を自動切断するので、1時間おきに接続をリフレッシュして防止
engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600 # MySQLが8時間で切断される問題を防ぐ設定
)

# DBとのセッション構築クラス
# autocommit=False: 自動commit防止(明示的にcommitするまで確定反映しない)
# autoflush=False: 自動flush防止(明示的にflushするまで確定反映しない)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 各テーブルのモデルのベースを作るクラス (モデル作成時はこれを継承)
Base = declarative_base()

# APIごとにデータベースの接続セッションを管理するための関数 (DI用)
# ここで一元化することで接続閉じ忘れ防止などする
def get_db():
    db = SessionLocal()
    try:
        yield db #yield: dbを呼び出し元に返却(return)はするが処理自体は終わらない(finallyするため)
    finally:
        db.close()
