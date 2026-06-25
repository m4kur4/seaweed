## 初期化手順
init.sql は MySQL コンテナの初回起動時（データディレクトリが空のとき）だけ実行されます。
以前から docker/db/data にデータがある場合、後から init.sql を追加しても 再実行されません。
疎通確認前に、次のいずれかが必要です。

```bash
# 方法A: 手動でテーブル作成
docker exec -i seaweed_db_1 mysql -useaweed_user -pseaweed_pass seaweed_db < docker/db/query/init.sql
# 方法B: DBデータを消して作り直す（既存データは消える）
docker-compose down
sudo rm -rf docker/db/data/*
docker-compose up -d
```