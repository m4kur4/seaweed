-- 既存DBのカラム名をリネームするマイグレーション（初回 init.sql 実行済みの環境向け）
USE seaweed_db;

ALTER TABLE transactions
    CHANGE COLUMN date transaction_date DATE NOT NULL,
    CHANGE COLUMN amount transaction_amount INT NOT NULL,
    CHANGE COLUMN type transaction_type VARCHAR(10) NOT NULL;

ALTER TABLE transactions
    DROP INDEX idx_transactions_date,
    ADD INDEX idx_transactions_date (transaction_date);
