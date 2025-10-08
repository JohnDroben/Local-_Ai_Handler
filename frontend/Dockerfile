FROM node:20-slim
WORKDIR /app
COPY package.json /app/
# Устанавливаем зависимости (включая dev для сборки)
RUN npm install --include=dev --legacy-peer-deps
COPY . /app
# Собираем production bundle
RUN npm run build
# Устанавливаем простой static сервер и запускаем dist на порту 3000
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
