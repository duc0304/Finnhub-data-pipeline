CREATE KEYSPACE IF NOT EXISTS finnhub 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE finnhub;

CREATE TABLE IF NOT EXISTS trades (
    symbol text,
    trade_timestamp timestamp,
    price double,
    volume int,
    trade_conditions list<text>,
    ingest_timestamp timestamp,
    PRIMARY KEY (symbol, trade_timestamp)
);

CREATE TABLE IF NOT EXISTS aggregates (
    symbol text,
    window_start timestamp,
    trade_count bigint,
    avg_price double,
    total_volume bigint,
    PRIMARY KEY ((symbol), window_start)
); 