## Dockerfileでnpm ci

`docker/frontend/Dockerfile`

```Dockerfile
COPY ./src/frontend/package.json ./src/frontend/package-lock.json ./
RUN npm ci
```

* node_modulesを作る目的
* package.jsonをコンテナへ常時置くのが目的ではなく、コンテナのビルド時に最新のpackage-lock.jsonでnpm ciするための記述

## vite.config.jsについて

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
  },
})
```
* defineConfig … Vite の設定を書くためのヘルパー。型補完や設定の補助が効き
* @vitejs/plugin-react … React 用の Vite プラグイン。JSX の変換や Fast Refresh（ホットリロード）を有効にする

* plugins: [react()]
  React プロジェクトとして Vite を動かすための設定
  -  .jsx / .tsx を正しく処理する
  - コード変更時にブラウザを自動更新する（HMR）
  - これがないと、React アプリとして正常に動かない

* server ブロック
  - host: '0.0.0.0'
    - コンテナ内の すべてのネットワークインターフェース で待ち受ける
    - デフォルトの localhost だけだと、Docker コンテナの外（ホストのブラウザ）から http://localhost:5173 でアクセスできないことがある
    - 0.0.0.0 にすることで、ポートマッピング 5173:5173 経由でホストからアクセスできるようになる

* watch: { usePolling: true }
  - ファイル変更の監視方法指定
  - 通常、Vite は OS のファイル監視機能で変更を検知する  
    Docker のバインドマウント（ホスト ↔ コンテナ）では、この監視がうまく動かないことがある（WSL2 でも起きやすい）
  - usePolling: true にすると、一定間隔でファイルをポーリングして変更を検知 するため、コンテナ内でもホットリロードが安定しやすくなる  
    代わりに CPU 使用量は少し増えることがある