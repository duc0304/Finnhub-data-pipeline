-- Tạo keyspace cho dữ liệu Finnhub với NetworkTopologyStrategy
CREATE KEYSPACE IF NOT EXISTS finnhub
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3};

-- Chuyển đến keyspace Finnhub
USE finnhub;

-- Tạo bảng lưu trữ giao dịch gốc với partition key tối ưu (hỗ trợ đa asset type)
CREATE TABLE IF NOT EXISTS trades (
    symbol TEXT,
    trade_date DATE,        -- Thêm date để phân tán partition
    trade_timestamp TIMESTAMP,
    price DOUBLE,
    volume DOUBLE,          -- Thay đổi từ BIGINT sang DOUBLE để hỗ trợ crypto volume nhỏ
    asset_type TEXT,        -- 'STOCK', 'CRYPTO', 'FOREX' etc.
    trade_conditions LIST<TEXT>,  -- Nullable - chỉ có với STOCK data
    ingest_timestamp TIMESTAMP,
    PRIMARY KEY ((symbol, trade_date), trade_timestamp)
) WITH CLUSTERING ORDER BY (trade_timestamp DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS'};

-- Tạo bảng lưu trữ dữ liệu tổng hợp (hỗ trợ đa asset type)
CREATE TABLE IF NOT EXISTS aggregates (
    symbol TEXT, 
    window_date DATE,       -- Thêm date để phân tán partition
    window_start TIMESTAMP,
    asset_type TEXT,        -- Thêm asset type để phân biệt
    trade_count BIGINT,
    avg_price DOUBLE,
    total_volume DOUBLE,    -- Thay đổi từ BIGINT sang DOUBLE để hỗ trợ crypto
    min_price DOUBLE,
    max_price DOUBLE,
    PRIMARY KEY ((symbol, window_date), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS'};

-- Materialized views đã bị xóa vì Cassandra disable MVs by default
-- Query trực tiếp từ main table trades với proper filtering

-- Materialized view cho aggregates đã bị xóa
-- Query trực tiếp từ main table aggregates

-- Tạo bảng để kiểm tra kết nối
CREATE TABLE IF NOT EXISTS finnhub.test_connection (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Tạo bảng OHLC data cho từng phút với partition key tối ưu (hỗ trợ đa asset type)
CREATE TABLE IF NOT EXISTS ohlc_data (
    symbol TEXT,
    window_date DATE,       -- Thêm date để phân tán partition
    window_start TIMESTAMP,
    asset_type TEXT,        -- Thêm asset type để phân biệt
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,          -- Thay đổi từ BIGINT sang DOUBLE để hỗ trợ crypto
    trade_count BIGINT,
    vwap DOUBLE,  -- Volume Weighted Average Price
    PRIMARY KEY ((symbol, window_date), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS'};

-- Tạo bảng technical indicators với partition key tối ưu (hỗ trợ đa asset type)
CREATE TABLE IF NOT EXISTS technical_indicators (
    symbol TEXT,
    window_date DATE,       -- Thêm date để phân tán partition
    window_start TIMESTAMP,
    asset_type TEXT,        -- Thêm asset type để phân biệt
    sma_20 DOUBLE,      -- Simple Moving Average 20 periods (Trend direction)
    ema_12 DOUBLE,      -- Exponential Moving Average 12 periods (Fast MA)
    rsi_14 DOUBLE,      -- Relative Strength Index 14 periods (Overbought/Oversold)
    macd_line DOUBLE,   -- MACD Line (EMA12 - EMA26) (Momentum)
    bb_middle DOUBLE,   -- Bollinger Band Middle = SMA20 (Support/Resistance)
    PRIMARY KEY ((symbol, window_date), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS'};

-- Materialized views cho OHLC và technical indicators đã bị xóa
-- Query trực tiếp từ main tables: ohlc_data và technical_indicators

-- Tạo bảng riêng cho CRYPTO data (đơn giản để test)
CREATE TABLE IF NOT EXISTS crypto_trades (
    symbol TEXT,
    trade_date DATE,
    trade_timestamp TIMESTAMP,
    price DOUBLE,
    volume DOUBLE,
    ingest_timestamp TIMESTAMP,
    PRIMARY KEY ((symbol, trade_date), trade_timestamp)
) WITH CLUSTERING ORDER BY (trade_timestamp DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': '1', 'compaction_window_unit': 'DAYS'};

-- Cassandra initialization completed successfully! 