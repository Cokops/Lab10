FROM golang:1.22-alpine

WORKDIR /app

# Копируем go.mod и go.sum
COPY go.mod go.sum ./
RUN go mod download

# Копируем все файлы (включая папку proto)
COPY . .

# Собираем приложение
RUN go build -o main .

EXPOSE 50051

CMD ["./main"]