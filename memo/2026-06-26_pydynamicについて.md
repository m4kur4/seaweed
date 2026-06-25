修正を反映しました。DB は `healthy` になってから backend が起動するようになっています。

---

## 実装した内容

### 1. MySQL の起動待ち（healthcheck）

`docker-compose.yml` の `db` に healthcheck を追加し、backend は `service_healthy` になるまで待つようにしました。

```yaml
depends_on:
  db:
    condition: service_healthy
```

```
db コンテナ起動
    ↓ mysqladmin ping が成功するまで待つ（最大30秒 + リトライ）
db が healthy になる
    ↓
backend コンテナ起動
```

### 2. 環境変数化（PHP の `.env` と同じ考え方）

| ファイル | 役割 | Git |
|---|---|---|
| `.env` | 実際の認証情報 | コミットしない（`.gitignore` に追加済み） |
| `.env.example` | 雛形（値の例） | コミットする |

**PHP との対応:**

| PHP | Python（今回） |
|---|---|
| `.env` ファイル | `.env` ファイル |
| `vlucas/phpdotenv` | `python-dotenv`（`load_dotenv()`） |
| `$_ENV['DB_HOST']` | `os.getenv("DB_HOST")` |
| `.env.example` を配布 | 同じ |

**読み込みの流れ:**

```
.env ファイル
    ↓ docker-compose の env_file でコンテナに注入
    ↓ database.py の os.getenv() で取得
DATABASE_URL を組み立てて MySQL に接続
```

初回セットアップ時は `.env.example` をコピーして使います。

```bash
cp .env.example .env
```

---

## ORM と Pydantic の説明（なぜ JSON 返却でエラーになるか）

### まず「API が返すものは JSON」

ブラウザや `fetch` が受け取れるのは **JSON というテキスト形式** だけです。

```json
{"id": 1, "amount": 1000, "type": "income"}
```

PHP でいうと、最終的に `json_encode()` した文字列を返すイメージです。

---

### SQLAlchemy の「モデル」= DB の1行を表す Python オブジェクト

`models.py` の `Transaction` は、MySQL の `transactions` テーブルと対応する **Python クラス** です。

```python
transactions = db.query(models.Transaction).all()
# → [Transaction(id=1, amount=1000, ...), Transaction(id=2, ...)]
```

PHP でのたとえ:

| Python (SQLAlchemy) | PHP |
|---|---|
| `models.Transaction` | Eloquent の `Transaction` モデル |
| `db.query(...).all()` | `Transaction::all()` |
| 返ってくるオブジェクト | `$transaction` インスタンス |

これは **メモリ上の Python オブジェクト** であり、JSON ではありません。

```python
transaction = Transaction(id=1, amount=1000, type="income")
type(transaction)  # → <class 'models.Transaction'>（普通のクラスのインスタンス）
```

`json.dumps(transaction)` はそのままでは失敗します。PHP で `json_encode($eloquentModel)` を素でやるのと同様です。

---

### 現在のコードで起きること

```python
return {
    "status": "success",
    "transactions": transactions  # ← Python オブジェクトのリスト
}
```

FastAPI はレスポンスを JSON に変換しようとしますが、`Transaction` オブジェクトは **JSON に変換する方法を知らない** ため、500 エラーになります。

```
Python オブジェクト（Transaction インスタンス）
        ↓  JSON に変換したい
        ✗  変換ルールがない → エラー
```

---

### Pydantic スキーマ = 「JSON 用の型定義」

**Pydantic** は FastAPI に標準で入っているバリデーション・変換ライブラリです。  
「API レスポンスはこの形の JSON にする」という **設計図（スキーマ）** を書くためのものです。

PHP でのたとえ:

| Pydantic | PHP |
|---|---|
| `TransactionResponse` スキーマ | API Resource / DTO クラス |
| `from_attributes=True` | Eloquent モデルから配列/DTOへ変換 |
| 型チェック（`amount: int`） | バリデーション |

```python
# schemas.py（イメージ）
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ORMオブジェクトから変換OK

    id: int
    date: date
    amount: int
    type: str
    description: str | None
    created_at: datetime
    updated_at: datetime
```

`from_attributes=True` は「SQLAlchemy の `Transaction` オブジェクトから、このスキーマに値をコピーしていい」という意味です。

---

### 変換の流れ（全体像）

```
MySQL (transactions テーブル)
    ↓ SQLAlchemy が SELECT
Python オブジェクト (Transaction インスタンス)  ← ORM の領域
    ↓ Pydantic が変換
JSON 用の dict / スキーマオブジェクト          ← API の領域
    ↓ FastAPI が json_encode
HTTP レスポンス (JSON 文字列)
    ↓ fetch
ブラウザ / フロントエンド
```

PHP で書くとこういうイメージです。

```php
// 1. DB から取得（ORM）
$transactions = Transaction::all();

// 2. API 用に変換（Resource / DTO）
return TransactionResource::collection($transactions);

// 3. Laravel が JSON にして返す
```

Python では 2 の役割を Pydantic が担います。

---

### レイヤーの整理

| レイヤー | ファイル | 役割 |
|---|---|---|
| DB テーブル定義 | `init.sql` | MySQL の物理構造 |
| ORM モデル | `models.py` | Python から DB を操作する |
| レスポンススキーマ | `schemas.py`（未作成） | API が返す JSON の形を定義 |
| API エンドポイント | `main.py` | リクエストを受けてレスポンスを返す |

`models.py` と `schemas.py` は似ていますが目的が違います。

- **models.py** … DB とのやりとり用（内部）
- **schemas.py** … クライアントへの返却用（外部）

同じ `Transaction` でも、DB 用と API 用で分けるのが一般的です（例: パスワードは DB にあっても API には返さない、など）。

---

### 修正するとこうなる（イメージ）

```python
from schemas import TransactionResponse

@app.get("/api/transactions")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()
    return {
        "status": "success",
        "data_count": len(transactions),
        "transactions": [
            TransactionResponse.model_validate(t) for t in transactions
        ],
    }
```

`model_validate(t)` が「ORM オブジェクト → Pydantic スキーマ」への変換です。  
FastAPI は Pydantic オブジェクトを JSON に変換できるので、500 エラーが解消されます。

---

Pydantic スキーマの実装（`schemas.py` 作成と `main.py` 修正）も進めますか？