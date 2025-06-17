from pyspark.sql.functions import *
from pyspark.sql.window import Window

def save_to_cassandra_crypto_trades(batch_df, batch_id):
    """Lưu CRYPTO trades vào bảng riêng crypto_trades"""
    try:
        if not batch_df.isEmpty():
            count = batch_df.count()
            print(f"Writing {count} CRYPTO records to Cassandra crypto_trades table (batch {batch_id})")
            batch_df.write \
                .format("org.apache.spark.sql.cassandra") \
                .mode("append") \
                .option("keyspace", "finnhub") \
                .option("table", "crypto_trades") \
                .save()
            print(f"Successfully wrote CRYPTO batch {batch_id} to Cassandra crypto_trades table")
            
            # Print first few records for debugging
            if count > 0:
                sample = batch_df.limit(2).collect()
                print(f"Sample CRYPTO trade data: {sample[0] if sample else 'No data'}")
                for row in sample:
                    print(f"  CRYPTO - Symbol: {row.symbol}, Price: ${row.price:.2f}, Volume: {row.volume}")
        else:
            print(f"CRYPTO Batch {batch_id} was empty, nothing to write")
    except Exception as e:
        print(f"Error saving CRYPTO batch {batch_id}: {e}")

def save_to_cassandra_trades(batch_df, batch_id):
    """Lưu raw trades vào Cassandra"""
    try:
        if not batch_df.isEmpty():
            count = batch_df.count()
            print(f"Writing {count} records to Cassandra trades table (batch {batch_id})")
            batch_df.write \
                .format("org.apache.spark.sql.cassandra") \
                .mode("append") \
                .option("keyspace", "finnhub") \
                .option("table", "trades") \
                .save()
            print(f"Successfully wrote batch {batch_id} to Cassandra trades table")
            
            # Print first few records for debugging
            if count > 0:
                sample = batch_df.limit(2).collect()
                print(f"Sample trade data: {sample[0] if sample else 'No data'}")
        else:
            print(f"Batch {batch_id} was empty, nothing to write to Cassandra trades table")
    except Exception as e:
        print(f"Error saving batch {batch_id} to Cassandra trades table: {e}")

def save_to_cassandra_aggregates(batch_df, batch_id):
    """Lưu aggregated data vào Cassandra"""
    try:
        if not batch_df.isEmpty():
            count = batch_df.count()
            print(f"Writing {count} aggregate records to Cassandra aggregates table (batch {batch_id})")
            batch_df.write \
                .format("org.apache.spark.sql.cassandra") \
                .mode("append") \
                .option("keyspace", "finnhub") \
                .option("table", "aggregates") \
                .save()
            print(f"Successfully wrote batch {batch_id} to Cassandra aggregates table")
            
            # Print sample for verification
            sample = batch_df.limit(2).collect()
            if sample:
                print("Sample of aggregated data:")
                for row in sample:
                    print(f"  Symbol: {row.symbol}, Window: {row.window_start}, Trades: {row.trade_count}, Avg Price: {row.avg_price}, Volume: {row.total_volume}")
        else:
            print(f"Batch {batch_id} was empty, nothing to write to Cassandra aggregates table")
    except Exception as e:
        print(f"Error saving batch {batch_id} to Cassandra aggregates table: {e}")

def save_to_cassandra_ohlc(batch_df, batch_id):
    """Lưu OHLC data vào Cassandra"""
    try:
        if not batch_df.isEmpty():
            count = batch_df.count()
            print(f"Writing {count} OHLC records to Cassandra (batch {batch_id})")
            batch_df.write \
                .format("org.apache.spark.sql.cassandra") \
                .mode("append") \
                .option("keyspace", "finnhub") \
                .option("table", "ohlc_data") \
                .save()
            print(f"Successfully wrote OHLC batch {batch_id}")
            
            # Print sample for verification
            sample = batch_df.limit(1).collect()
            if sample:
                row = sample[0]
                print(f"  OHLC Sample - {row.symbol}: O={row.open_price:.2f}, H={row.high_price:.2f}, L={row.low_price:.2f}, C={row.close_price:.2f}, V={row.volume}")
        else:
            print(f"OHLC Batch {batch_id} was empty")
    except Exception as e:
        print(f"Error saving OHLC batch {batch_id}: {e}")

def calculate_technical_indicators(spark, batch_df, batch_id):
    """Tính toán technical indicators"""
    try:
        if not batch_df.isEmpty():
            print(f"Calculating technical indicators for batch {batch_id}...")
            
            # Read existing OHLC data from Cassandra for calculations
            ohlc_historical_df = spark.read \
                .format("org.apache.spark.sql.cassandra") \
                .option("keyspace", "finnhub") \
                .option("table", "ohlc_data") \
                .load()
            
            # Union current batch with historical data
            if not ohlc_historical_df.isEmpty():
                combined_df = ohlc_historical_df.union(batch_df).distinct()
            else:
                combined_df = batch_df
            
            # Window specifications for different periods (partitioned by symbol AND asset_type)
            symbol_window = Window.partitionBy("symbol", "asset_type").orderBy("window_start")  
            symbol_window_20 = symbol_window.rowsBetween(-19, 0) # 20 periods for SMA20
            symbol_window_14 = symbol_window.rowsBetween(-13, 0) # 14 periods for RSI
            symbol_window_12 = symbol_window.rowsBetween(-11, 0) # 12 periods for EMA12
            symbol_window_26 = symbol_window.rowsBetween(-25, 0) # 26 periods for EMA26 (needed for MACD)
            
            # Calculate TOP 5 most valuable technical indicators
            tech_indicators_df = combined_df \
                .withColumn("sma_20", avg("close_price").over(symbol_window_20)) \
                .withColumn("bb_middle", avg("close_price").over(symbol_window_20)) \
                .withColumn("price_change", col("close_price") - lag("close_price", 1).over(symbol_window)) \
                .withColumn("gain", when(col("price_change") > 0, col("price_change")).otherwise(0)) \
                .withColumn("loss", when(col("price_change") < 0, -col("price_change")).otherwise(0)) \
                .withColumn("avg_gain", avg("gain").over(symbol_window_14)) \
                .withColumn("avg_loss", avg("loss").over(symbol_window_14)) \
                .withColumn("rs", col("avg_gain") / col("avg_loss")) \
                .withColumn("rsi_14", 100 - (100 / (1 + col("rs")))) \
                .withColumn("ema_12", 
                    when(row_number().over(symbol_window) == 1, col("close_price"))
                    .otherwise(col("close_price") * (2.0/13.0) + lag("close_price", 1).over(symbol_window) * (11.0/13.0))
                ) \
                .withColumn("ema_26",
                    when(row_number().over(symbol_window) == 1, col("close_price"))
                    .otherwise(col("close_price") * (2.0/27.0) + lag("close_price", 1).over(symbol_window) * (25.0/27.0))
                ) \
                .withColumn("macd_line", col("ema_12") - col("ema_26")) \
                .select(
                    "symbol",
                    "window_start",
                    to_date(col("window_start")).alias("window_date"),
                    "asset_type",
                    "sma_20",
                    "ema_12",
                    "rsi_14",
                    "macd_line",
                    "bb_middle"
                )
            
            # Filter only new records (from current batch)
            current_windows = batch_df.select("symbol", "window_start", "asset_type").distinct()
            tech_indicators_new = tech_indicators_df.join(current_windows, ["symbol", "window_start", "asset_type"], "inner")
            
            if not tech_indicators_new.isEmpty():
                count = tech_indicators_new.count()
                print(f"Writing {count} technical indicator records to Cassandra (batch {batch_id})")
                
                tech_indicators_new.write \
                    .format("org.apache.spark.sql.cassandra") \
                    .mode("append") \
                    .option("keyspace", "finnhub") \
                    .option("table", "technical_indicators") \
                    .save()
                
                print(f"Successfully wrote technical indicators batch {batch_id}")
                
                # Print sample
                sample = tech_indicators_new.limit(1).collect()
                if sample:
                    row = sample[0]
                    print(f"  Tech Sample - {row.symbol}: SMA20={row.sma_20:.2f}, EMA12={row.ema_12:.2f}, RSI={row.rsi_14:.2f}, MACD={row.macd_line:.2f}")
            else:
                print(f"No new technical indicators to write for batch {batch_id}")
        else:
            print(f"Technical indicators batch {batch_id} was empty")
            
    except Exception as e:
        print(f"Error calculating technical indicators for batch {batch_id}: {e}")

def create_aggregated_dataframe(df):
    """Tạo aggregated dataframe với hỗ trợ asset_type"""
    return df \
        .withWatermark("trade_timestamp", "15 seconds") \
        .withColumn("price_volume_multiply", col("price") * col("volume")) \
        .groupBy(
            window("trade_timestamp", "1 minute"),
            "symbol",
            "asset_type"
        ) \
        .agg(
            count("*").alias("trade_count"),
            avg("price").alias("avg_price"),
            sum("volume").alias("total_volume"),
            min("price").alias("min_price"),
            max("price").alias("max_price")
        ) \
        .select(
            "symbol",
            col("window.start").alias("window_start"),
            to_date(col("window.start")).alias("window_date"),
            "asset_type",
            "trade_count",
            "avg_price",
            "total_volume",
            "min_price",
            "max_price"
        )

def create_ohlc_dataframe(df):
    """Tạo OHLC dataframe với hỗ trợ asset_type"""
    return df \
        .withWatermark("trade_timestamp", "15 seconds") \
        .groupBy(
            window("trade_timestamp", "1 minute"),
            "symbol",
            "asset_type"
        ) \
        .agg(
            first("price").alias("open_price"),
            max("price").alias("high_price"),
            min("price").alias("low_price"),
            last("price").alias("close_price"),
            sum("volume").alias("volume"),
            count("*").alias("trade_count"),
            sum(col("price") * col("volume")).alias("price_volume_sum"),
            sum("volume").alias("total_volume")
        ) \
        .select(
            "symbol",
            col("window.start").alias("window_start"),
            to_date(col("window.start")).alias("window_date"),
            "asset_type",
            "open_price",
            "high_price", 
            "low_price",
            "close_price",
            "volume",
            "trade_count",
            (col("price_volume_sum") / col("total_volume")).alias("vwap")
        ) 