FROM golang:1.21.3-alpine
# Установите рабочий каталог в /app
WORKDIR /app
COPY . .
# Соберите ваше приложение
RUN go build -o pgbench-api
EXPOSE 8080
# Запустите приложение при старте контейнера
CMD ["./pgbench-api"]