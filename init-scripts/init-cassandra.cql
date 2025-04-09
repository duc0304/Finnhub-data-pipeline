-- Tạo keyspace cho dữ liệu Finnhub
CREATE KEYSPACE IF NOT EXISTS finnhub
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Chuyển đến keyspace Finnhub
USE finnhub;

-- Tạo bảng lưu trữ giao dịch gốc
CREATE TABLE IF NOT EXISTS trades (
    symbol TEXT,
    trade_timestamp TIMESTAMP,
    price DOUBLE,
    volume BIGINT,
    trade_conditions LIST<TEXT>,
    ingest_timestamp TIMESTAMP,
    PRIMARY KEY ((symbol), trade_timestamp)
) WITH CLUSTERING ORDER BY (trade_timestamp DESC);

-- Tạo bảng lưu trữ dữ liệu tổng hợp
CREATE TABLE IF NOT EXISTS aggregates (
    symbol TEXT, 
    window_start TIMESTAMP,
    trade_count BIGINT,
    avg_price DOUBLE,
    total_volume BIGINT,
    PRIMARY KEY ((symbol), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC);

-- Tạo index để tìm kiếm hiệu quả
CREATE INDEX IF NOT EXISTS trades_timestamp_idx ON trades (trade_timestamp);
CREATE INDEX IF NOT EXISTS agg_timestamp_idx ON aggregates (window_start);

-- Xóa lệnh SELECT có vấn đề và thay thế bằng một comment đơn giản
-- Cassandra initialization completed successfully! 