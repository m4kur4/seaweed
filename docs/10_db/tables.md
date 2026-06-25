# テーブル定義書

## 共通設定

### データベース名
seaweed_db
### エンジン
InnoDB
### 文字コード
utf8mb4　※MySQL推奨設定

---

## 取引・変動履歴テーブル (`transactions`)

### 概要

日々の資産の変動（収入・支出）を記録する

### 定義

 No | 論理名 | 物理名 | データ型 | 桁数 | PK | FK | Not Null | Default | 備考 |
 --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
 1 | ID | `id` | BIGINT | - | ○ | - | ○ | 自動連番 | 一意識別子 (Auto Increment) |
 2 | 変動日 | `date` | DATE | - | - | - | ○ | - | 変動が発生した日付 |
 3 | 変動額 | `amount` | INT | - | - | - | ○ | - | 符号なし整数 (常に正の数) |
 4 | 変動種別 | `type` | VARCHAR | 10 | - | - | ○ | - | `'income'`: 収入 / `'expense'`: 支出 |
 5 | 備考 | `description` | TEXT | - | - | - | - | NULL | 変動の理由やメモ |
 6 | 作成日時 | `created_at` | TIMESTAMP | - | - | - | ○ | `CURRENT_TIMESTAMP` | レコード作成時のシステム日時 |
 7 | 更新日時 | `updated_at` | TIMESTAMP | - | - | - | ○ | `CURRENT_TIMESTAMP` | レコード更新時のシステム日時（自動更新） |

### インデックス
* `idx_transactions_date`: `date` カラム（日付順の並び替え・日付範囲検索の高速化のため）
