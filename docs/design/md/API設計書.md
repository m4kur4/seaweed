# seaweed API設計書

No.4 ／ 版 1.1 ／ 2026-08-30 ／ 入力: 要件定義書 1.3、システム構成〜画面 1.1 ／ 推敲: 認証・処理仕様との整合

ベース URL は同一オリジンの `/api/v1`。待受・コンテキストパスはシステム構成設計書。外部システム IF は無い。

## 目次

1. [共通規約](#1-共通規約)
2. [エラー](#2-エラー)
3. [コード値（JSON）](#3-コード値json)
4. [エンドポイント一覧](#4-エンドポイント一覧)
5. [生存確認・認証](#5-生存確認認証)
6. [家計簿](#6-家計簿)
7. [サブスク](#7-サブスク)
8. [投資記録](#8-投資記録)
9. [定期収入](#9-定期収入)
10. [設定](#10-設定)
11. [ダッシュボード](#11-ダッシュボード)
12. [後続への委譲](#12-後続への委譲)
13. [設計判断一覧](#13-設計判断一覧)

## 1. 共通規約

| 項目 | 値 |
| --- | --- |
| スキーム | 本番 `http://seaweed`、ローカル Vite 経由 `/api` プロキシ |
| Content-Type | リクエスト・レスポンスとも `application/json; charset=UTF-8`。DELETE 成功は本文なし |
| フィールド名 | camelCase |
| 未知フィールド | 無視しない。JSON に定義外キーがあれば 400 `VALIDATION_ERROR` |
| 日付 | 文字列 `YYYY-MM-DD`。実在する暦日（JST の日付として解釈）。時刻は返さない |
| 年月 | 目標の到達希望のみ `YYYY-MM-01`（その月の 1 日） |
| 金額・単価・数量 | JSON number。サーバは DECIMAL。`null` は目標額など許可された項目のみ |
| 認証 | Cookie セッション。ブラウザは同一オリジンで Cookie を送る。ヘッダ `Authorization` は使わない |
| CSRF トークン | v1 では付けない（同一オリジン＋閉域） |
| Cookie 名・有効期間・Secure | `SEAWEED_SESSION`、14 日、Secure=false（認証セキュリティ設計書）。本 API は「ログイン成功で Set-Cookie、ログアウトで削除」を契約する |
| ページング | なし。クエリ `page` は未知フィールドとして 400 |

成功ステータスは機能設計どおり: GET 一覧/1件 200、POST 201、PUT 200、DELETE 204。

`id` は JSON 整数。パス `{id}` が整数でない（`abc`）ときは 400。存在しない id は 404。

文字列は UTF-8。前後空白はサーバで trim する。trim 後空なら必須違反。

## 2. エラー

すべての 4xx/5xx（health 以外）は次の形。

```json
{
  "code": "VALIDATION_ERROR",
  "message": "クレジットカードは引落日（資金決済日）が必要です",
  "fields": {
    "settledOn": "必須です"
  }
}
```

| フィールド | 規則 |
| --- | --- |
| `code` | 下表 |
| `message` | 人が読む 1 文。画面はこれを優先表示 |
| `fields` | 項目エラーがあるときのみ。キーは JSON フィールド名。無ければ省略または `{}` |

| HTTP | code | とき |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 型・必須・範囲・コード不一致・from>to・片方だけ指定 |
| 400 | `LIMIT_EXCEEDED` | 家計 500 件超、他マスタ 200 件超。`message` は「件数が上限を超えました。期間を狭めてください」（マスタは「件数が上限を超えました」） |
| 401 | `UNAUTHORIZED` | 未ログイン、セッション切れ、ログイン失敗 |
| 404 | `NOT_FOUND` | 資源なし。`message` は「対象が見つかりません」 |
| 405 | （任意） | 未定義メソッド。Spring 既定でよい |
| 500 | `INTERNAL` | 想定外。`message` は「サーバエラーです」。スタックは返さない |

ログイン失敗も 401 `UNAUTHORIZED`、`message` は「ユーザー名またはパスワードが正しくありません」。ユーザーの有無は区別しない。

業務 API の未認証は 401。SPA が `/login` へ飛ばす。HTML のログイン画面 GET は本 API の対象外。

## 3. コード値（JSON）

格納値はコード定義書と**同じ文字列**にする。API は次以外を 400 とする。

**kind（収支）**

| JSON | 画面 |
| --- | --- |
| `expense` | 支出 |
| `income` | 収入 |

**paymentMethod**

| JSON | 画面 |
| --- | --- |
| `cash` | 現金 |
| `bank` | 銀行口座 |
| `credit_card` | クレジットカード |
| `e_money` | 電子マネー・QR |
| `other` | その他 |

**category（kind=expense）**

`housing` `food` `daily` `utilities` `telecom` `transport` `medical` `education` `clothing` `leisure` `investment_transfer` `other`

**category（kind=income）**

`extra` `other_income`

kind と category の組み合わせが上以外なら 400。`fields.category`。

**cycle**

| JSON | 画面 |
| --- | --- |
| `monthly` | 月額 |
| `yearly` | 年額 |

**dateField（クエリ）**

`occurred`（発生日） / `settled`（資金決済日）

## 4. エンドポイント一覧

| メソッド | パス | 認証 |
| --- | --- | --- |
| GET | `/api/v1/health` | 不要 |
| POST | `/api/v1/auth/login` | 不要 |
| POST | `/api/v1/auth/logout` | 必要 |
| GET | `/api/v1/auth/me` | 必要 |
| GET POST | `/api/v1/ledger-entries` | 必要 |
| GET PUT DELETE | `/api/v1/ledger-entries/{id}` | 必要 |
| GET POST | `/api/v1/subscriptions` | 必要 |
| GET PUT DELETE | `/api/v1/subscriptions/{id}` | 必要 |
| GET POST | `/api/v1/investments` | 必要 |
| GET PUT DELETE | `/api/v1/investments/{id}` | 必要 |
| GET POST | `/api/v1/incomes` | 必要 |
| GET PUT DELETE | `/api/v1/incomes/{id}` | 必要 |
| GET PUT | `/api/v1/settings/balance` | 必要 |
| GET PUT | `/api/v1/settings/goal` | 必要 |
| GET | `/api/v1/dashboard` | 必要 |

上記以外の `/api/v1/**` は 404。

## 5. 生存確認・認証

### GET `/api/v1/health`

認証なし。DB に接続しない。常に 200。

```json
{ "status": "ok" }
```

### POST `/api/v1/auth/login`

```json
{ "username": "me", "password": "secret" }
```

成功 200。`Set-Cookie`。本文:

```json
{ "username": "me" }
```

失敗 401（2 章）。パスワード変更 API は無い。

### POST `/api/v1/auth/logout`

ボディなし。成功 204。Cookie 削除。未認証 401。

### GET `/api/v1/auth/me`

```json
{ "username": "me" }
```

## 6. 家計簿

### オブジェクト

```json
{
  "id": 12,
  "kind": "expense",
  "amount": 3200,
  "occurredOn": "2026-08-15",
  "settledOn": "2026-09-27",
  "paymentMethod": "credit_card",
  "category": "food",
  "description": "スーパー"
}
```

POST/PUT のボディに `id` を含めない。含めれば未知フィールドとして 400。

| フィールド | 制約 |
| --- | --- |
| amount | 正の数。0・負は 400 |
| occurredOn, settledOn | 必須の暦日。`credit_card` 以外でもサーバは `settledOn` 必須（画面がコピーする） |
| paymentMethod=`credit_card` | `settledOn` 欠落・null は 400。`message` は「クレジットカードは引落日（資金決済日）が必要です」 |
| description | 1〜200 文字（trim 後） |
| occurredOn と settledOn の前後 | 問わない（先払いも可） |

### GET `/api/v1/ledger-entries`

クエリ必須: `from`, `to`, `dateField`。例:

`GET /api/v1/ledger-entries?from=2026-08-01&to=2026-08-31&dateField=settled`

| 規則 | 内容 |
| --- | --- |
| 欠落 | 400。サーバ既定は持たない |
| from > to | 400 |
| フィルタ | `dateField=occurred` なら `occurredOn`、`settled` なら `settledOn` が `[from, to]` 閉区間 |
| 件数 | 501 件以上ヒットなら 400 `LIMIT_EXCEEDED`（1 件も返さない） |
| 並び | フィルタ対象日の降順、同日は `id` 降順 |

```json
{ "items": [ { "id": 12, "...": "..." } ] }
```

空なら `"items": []`。

### POST `/api/v1/ledger-entries`

ボディはオブジェクトから `id` を除いたもの。201。本文は採番済みオブジェクト。

### GET `/api/v1/ledger-entries/{id}`

200 でオブジェクト。無ければ 404。

### PUT `/api/v1/ledger-entries/{id}`

POST と同じボディ。200 で更新後オブジェクト。

### DELETE `/api/v1/ledger-entries/{id}`

204。無ければ 404。

## 7. サブスク

### オブジェクト

```json
{
  "id": 1,
  "name": "動画配信",
  "amount": 1490,
  "cycle": "monthly",
  "billingMonth": null,
  "billingDay": 10,
  "monthlyEquivalent": 1490
}
```

年額例: `"cycle": "yearly", "billingMonth": 3, "billingDay": 1, "monthlyEquivalent": 124.17`（1490÷12 を処理仕様の HALF_UP・小数 2 桁。API は計算結果の number を返す）。

`monthlyEquivalent` は応答のみ。POST/PUT に含めたら 400。

| cycle | billingMonth | billingDay |
| --- | --- | --- |
| monthly | null 必須 | 1〜28 必須 |
| yearly | 1〜12 必須 | 1〜28 必須 |

name 1〜100 文字。amount 正の数。

### 一覧 GET `/api/v1/subscriptions`

クエリなし。名称昇順、同名は id 昇順。上限 200。

```json
{ "items": [] }
```

POST 201 / GET id / PUT / DELETE は家計簿と同じパターン。

## 8. 投資記録

### オブジェクト

```json
{
  "id": 3,
  "investedOn": "2026-08-01",
  "name": "架空商事",
  "code": "9999",
  "reason": "長期保有",
  "unitPrice": 1234.5,
  "quantity": 100,
  "investedAmount": 123450
}
```

| フィールド | 制約 |
| --- | --- |
| name | 1〜100 |
| code | 省略可。null または 1〜20。空文字は null に正規化 |
| reason | 1〜500 |
| unitPrice, quantity | 正の数 |
| investedAmount | 応答のみ。`unitPrice * quantity`。POST/PUT に含めたら 400 |

### GET `/api/v1/investments`

クエリなし。`investedOn` 降順、同日 `id` 降順。上限 200。`{ "items": [] }`。

CRUD のステータスは家計簿と同じ。

## 9. 定期収入

```json
{
  "id": 1,
  "name": "給与",
  "amount": 300000,
  "cycle": "monthly",
  "monthlyEquivalent": 300000
}
```

支払日フィールドは無い。`monthlyEquivalent` は応答のみ。name 1〜100、amount 正、cycle は 3 章。

一覧: 名称昇順。上限 200。CRUD パターンはサブスクと同じ。

## 10. 設定

### GET/PUT `/api/v1/settings/balance`

```json
{
  "amount": 500000,
  "updatedOn": "2026-08-30"
}
```

PUT ボディは `{ "amount": 500000 }` のみ。`updatedOn` を送ると 400。

| 項目 | 規則 |
| --- | --- |
| amount | 0 以上。負は 400 |
| updatedOn | PUT 成功時、サーバが JST の今日を入れる。未 PUT の初期行は `updatedOn`: **null**（画面は「未登録」） |

GET は常に 200（行は DDL で 1 件ある）。

### GET/PUT `/api/v1/settings/goal`

```json
{
  "targetAmount": 1000000,
  "targetOn": "2027-03-01"
}
```

PUT ボディは両キー必須（値は null 可）。

| 項目 | 規則 |
| --- | --- |
| targetAmount | number（正）または null。0・負は 400。null は未設定 |
| targetOn | `YYYY-MM-01` または null。日が 01 以外は 400。月として不正なら 400 |

目標 null でも `targetOn` は保存する（画面どおり）。ダッシュボードが希望日を使うかは処理仕様書（目標なしなら到達・逆算を出さない）。

## 11. ダッシュボード

### GET `/api/v1/dashboard`

| クエリ | 規則 |
| --- | --- |
| なし | `from`=`当月1日`、`to`=`当月末`（サーバ JST） |
| 両方 | 閉区間、資金決済日で実績を切る。`from` > `to` は 400 |
| 片方のみ | 400 |

予測ブロックは `from`/`to` に依存しない。

### 応答（キー固定）

```json
{
  "balance": {
    "amount": 500000,
    "updatedOn": "2026-08-30"
  },
  "periodSummary": {
    "from": "2026-08-01",
    "to": "2026-08-31",
    "incomeTotal": 0,
    "expenseTotal": 80000,
    "net": -80000
  },
  "incomeMonthlyTotal": 300000,
  "subscriptionMonthlyTotal": 1490,
  "investmentSummary": {
    "count": 2,
    "investedTotal": 123450
  },
  "expenseBreakdown": [
    { "category": "food", "amount": 50000 }
  ],
  "forecast": {
    "available": true,
    "monthlySavings": 50000,
    "variableExpenseMissing": false,
    "points": [
      { "yearMonth": "2026-08", "amount": 500000 },
      { "yearMonth": "2026-09", "amount": 550000 }
    ]
  },
  "goalProjection": {
    "hasGoal": true,
    "reachStatus": "reachable",
    "reachYearMonth": "2027-04",
    "hasTargetDate": true,
    "cutStatus": "needed",
    "cutAmount": 12000
  }
}
```

| キー | 規則 |
| --- | --- |
| balance.updatedOn | null なら未登録。`forecast.available` は false |
| periodSummary.net | incomeTotal − expenseTotal。支出・収入は家計簿の期間合計のみ |
| expenseBreakdown | 金額 0 の費目は載せない。順は金額降順（画面の横棒用） |
| forecast.available | false のとき `points` は `[]`。月次貯金額は出してもよい（処理仕様）。画面はチャートを隠す |
| variableExpenseMissing | 完了月 0 なら true |
| points[].yearMonth | `YYYY-MM` |
| goalProjection.hasGoal | targetAmount が非 null |
| reachStatus | `none` / `reachable` / `unreachable` / `achieved`。hasGoal=false なら `none`、reachYearMonth は null |
| hasTargetDate | targetOn 非 null かつ hasGoal |
| cutStatus | `none`（逆算しない）/ `needed` / `already_ok`。hasTargetDate=false なら `none`、cutAmount は null |
| cutAmount | 削減すべき正の金額。already_ok のとき 0 または null（**0 を返す**） |

数値の求め方は処理仕様書。本書類はキーと null 規則だけを正とする。

書き込みメソッドは定義しない。

## 12. 後続への委譲

| 文書 | 内容 |
| --- | --- |
| コード定義書 | 3 章と同じ文字列を DB に持つ |
| テーブル定義書 | 列と DECIMAL 桁。JSON number との対応 |
| 処理仕様書 | 月額換算の丸め、チャート点、available、逆算 |
| 認証セキュリティ設計書 | Cookie・ハッシュは確定。連続失敗のロックはしない |

OpenAPI YAML は本版では出さない。実装時に本書類から生成してよい。

## 13. 設計判断一覧

| ID | 判断 | 理由 |
| --- | --- | --- |
| D-API-01 | camelCase、日付は文字列 | JS と Jackson の既定に近い |
| D-API-02 | 未知キーは 400 | 画面の typo を早期に落とす |
| D-API-03 | 一覧は `{ items: [] }` で包む | 後からメタを足せる |
| D-API-04 | 月額換算・投入額は応答専用 | 改ざん面と要件（手入力禁止） |
| D-API-05 | 目標の希望日は `YYYY-MM-01` | 画面の `month` と一対一 |
| D-API-06 | ダッシュボード内訳は API 側で降順 | 画面実装を薄くする |
| D-API-07 | エラーに `code` + `message` + `fields` | 画面の汎用バナーと項目エラーを分ける |
| D-API-08 | CSRF トークンなし | 同一オリジン・閉域。認証セキュリティ D-SEC-06 で確定（追加しない） |
| D-API-09 | JSON の enum を本書類で固定 | コード定義書と実装が割れないようにする |
