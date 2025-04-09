from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("Starting Spark application...")
    
    # Master URL lấy từ biến môi trường hoặc mặc định
    master_url = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
    print(f"Connecting to Spark Master at: {master_url}")
    
    # Cassandra connection info
    cassandra_host = os.getenv("CASSANDRA_HOST", "cassandra")
    cassandra_user = os.getenv("CASSANDRA_USERNAME", "cassandra")
    cassandra_pass = os.getenv("CASSANDRA_PASSWORD", "cassandra")
    print(f"Using Cassandra host: {cassandra_host}")
    
    # Tạo Spark session với Cassandra connector
    spark = SparkSession.builder \
        .appName("FinnhubStreamProcessor") \
        .master(master_url) \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,com.datastax.spark:spark-cassandra-connector_2.12:3.4.0") \
        .config("spark.cassandra.connection.host", cassandra_host) \
        .config("spark.cassandra.connection.port", "9042") \
        .config("spark.cassandra.auth.username", cassandra_user) \
        .config("spark.cassandra.auth.password", cassandra_pass) \
        .config("spark.cassandra.connection.keepAliveMS", "60000") \
        .config("spark.cassandra.output.consistency.level", "LOCAL_ONE") \
        .config("spark.sql.extensions", "com.datastax.spark.connector.CassandraSparkExtensions") \
        .config("spark.sql.catalog.cassandra", "com.datastax.spark.connector.datasource.CassandraCatalog") \
        .getOrCreate()

    print("Spark session created successfully")
    print(f"Spark Application UI URL: http://localhost:4040")
    print(f"Spark Master UI URL: http://localhost:8080")
    print(f"Spark Worker UI URL: http://localhost:8081")
    print(f"Cassandra configured at: {cassandra_host}")

    # Test Cassandra Connection
    try:
        test_df = spark.createDataFrame([("test_key", "test_value")], ["key", "value"])
        print("Testing Cassandra connection...")
        
        # Try to write to a test table
        test_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", "finnhub") \
            .option("table", "test_connection") \
            .option("confirm.truncate", "true") \
            .option("createTableOptions", "WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}") \
            .option("schema.autoCreateTable", "true") \
            .save()
        print("Successfully connected to Cassandra!")
    except Exception as e:
        print(f"Warning: Could not test connection to Cassandra: {e}")
        print("Will continue and try to process data anyway...")

    # Define schema for Kafka data
    schema = StructType([
        StructField("data", ArrayType(StructType([
            StructField("c", ArrayType(StringType()), True),
            StructField("p", DoubleType(), True),
            StructField("s", StringType(), True),
            StructField("t", LongType(), True),
            StructField("v", IntegerType(), True)
        ]))),
        StructField("type", StringType(), True)
    ])

    # Connect to Kafka
    print("Connecting to Kafka...")
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    kafka_topic = os.getenv("KAFKA_TOPIC_NAME", "finnhub_trades")
    print(f"Kafka Bootstrap Servers: {kafka_bootstrap_servers}")
    print(f"Kafka Topic: {kafka_topic}")

    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    print("Successfully connected to Kafka")

    # Parse JSON and explode data array
    df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select(
        explode("data.data").alias("trade")
    ).select(
        "trade.*"
    )

    # Rename columns and add timestamp
    df = df \
        .withColumnRenamed("c", "trade_conditions") \
        .withColumnRenamed("p", "price") \
        .withColumnRenamed("s", "symbol") \
        .withColumnRenamed("t", "trade_timestamp") \
        .withColumnRenamed("v", "volume") \
        .withColumn("trade_timestamp", (col("trade_timestamp") / 1000).cast("timestamp")) \
        .withColumn("ingest_timestamp", current_timestamp())

    # Define Cassandra save function for raw trades
    def save_to_cassandra_trades(batch_df, batch_id):
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
            # Continue processing even if this batch fails
            # raise e  # Uncomment to stop processing on error

    # Write trades to Cassandra and console
    print("Starting trade stream to Cassandra...")
    query = df.writeStream \
        .foreachBatch(save_to_cassandra_trades) \
        .outputMode("append") \
        .start()

    # Create summary dataframe
    summary_df = df \
        .withWatermark("trade_timestamp", "15 seconds") \
        .withColumn("price_volume_multiply", col("price") * col("volume")) \
        .groupBy(
            window("trade_timestamp", "1 minute"),
            "symbol"
        ) \
        .agg(
            count("*").alias("trade_count"),
            avg("price").alias("avg_price"),
            sum("volume").alias("total_volume")
        ) \
        .select(
            "symbol",
            col("window.start").alias("window_start"),
            "trade_count",
            "avg_price",
            "total_volume"
        )

    # Define Cassandra save function for aggregates
    def save_to_cassandra_aggregates(batch_df, batch_id):
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
            # Continue processing even if this batch fails
            # raise e  # Uncomment to stop processing on error

    # Write aggregates to Cassandra and console
    print("Starting aggregation stream to Cassandra...")
    summary_query = summary_df.writeStream \
        .foreachBatch(save_to_cassandra_aggregates) \
        .outputMode("update") \
        .trigger(processingTime="5 seconds") \
        .start()

    print("All streaming queries started successfully!")
    print("Processing data... Check the console output for results.")
    
    # Monitor streaming queries
    try:
        spark.streams.awaitAnyTermination()
    except Exception as e:
        print(f"Error in streaming process: {e}")
        # Try to stop gracefully
        for q in spark.streams.active:
            try:
                q.stop()
            except:
                pass

if __name__ == "__main__":
    main() 