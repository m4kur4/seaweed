# frontendコンテナのフォルダで実行
docker-compose exec frontend npm create vite@latest . -- --template react
docker-compose exec frontend npm install

# 開発サーバー起動
docker-compose exec -d frontend npm run dev -- --host

# 上記をrootユーザーでやってしまっていた場合、WSLの普段使いユーザーへ権限設定(WSLから編集できなくなるため)
cd /home/m4kur4/development/seaweed
sudo chown -R $USER:$USER src/frontend