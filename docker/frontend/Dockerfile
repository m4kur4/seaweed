FROM node:20-slim

WORKDIR /app

COPY ./src/frontend/package.json ./src/frontend/package-lock.json ./
RUN npm ci

# 開発サーバー起動
CMD ["npm", "run", "dev"]
