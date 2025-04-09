# Simple Finnhub Streaming Data Pipeline

Một phiên bản đơn giản của Finnhub Streaming Data Pipeline sử dụng Docker Compose.

## Các thành phần

- **Finnhub Producer**: Lấy dữ liệu từ Finnhub websocket và gửi vào Kafka
- **Kafka**: Message broker để truyền dữ liệu
- **Spark Stream Processor**: Xử lý dữ liệu từ Kafka và ghi vào Cassandra
- **Cassandra**: Lưu trữ dữ liệu
- **Grafana**: Hiển thị dữ liệu từ Cassandra

## Yêu cầu

- Docker
- Docker Compose
- Finnhub API Token

## Cài đặt

1. Clone repository:

```bash
git clone <repository-url>
cd simple
```

2. Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

3. Cập nhật `FINNHUB_API_TOKEN` trong file `.env` với token của bạn

4. Chạy các container:

```bash
docker-compose up --build
```

## Cấu trúc thư mục

```
simple/
├── producer/           # Finnhub Producer
│   ├── Dockerfile
│   ├── producer.py
│   └── requirements.txt
├── processor/          # Spark Stream Processor
│   ├── Dockerfile
│   ├── processor.py
│   └── requirements.txt
├── docker-compose.yml  # Docker Compose configuration
└── .env               # Environment variables
```

## Truy cập các service

- **Grafana**: http://localhost:3000

  - Username: admin
  - Password: admin

- **Cassandra**: localhost:9042

- **Kafka**: localhost:9092

## Cấu hình Cassandra

Sau khi các container đã chạy, tạo keyspace và tables trong Cassandra:

```sql
CREATE KEYSPACE finnhub WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE finnhub.trades (
    symbol text,
    trade_timestamp timestamp,
    price double,
    volume int,
    trade_conditions list<text>,
    ingest_timestamp timestamp,
    PRIMARY KEY (symbol, trade_timestamp)
);

CREATE TABLE finnhub.aggregates (
    symbol text,
    avg_price_volume double,
    PRIMARY KEY (symbol)
);
```

## Giới hạn bộ nhớ

Các container được cấu hình với giới hạn bộ nhớ để chạy trên máy có 6GB RAM:

- Zookeeper: 512MB
- Kafka: 1GB
- Cassandra: 1GB
- Finnhub Producer: 512MB
- Spark Stream Processor: 1GB
- Grafana: 512MB
