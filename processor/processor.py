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
    
    # Tạo Spark session
    spark = SparkSession.builder \
        .appName("FinnhubStreamProcessor") \
        .master(master_url) \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
        .getOrCreate()

    print("Spark session created successfully")
    print(f"Spark Application UI URL: http://localhost:4040")
    print(f"Spark Master UI URL: http://localhost:8080")
    print(f"Spark Worker UI URL: http://localhost:8081")

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

    # Write trades to console
    print("Starting trade stream...")
    query = df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
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
            avg("price_volume_multiply").alias("avg_price_volume"),
            count("*").alias("trade_count"),
            avg("price").alias("avg_price"),
            sum("volume").alias("total_volume")
        )

    # Write aggregates to console
    print("Starting aggregation stream...")
    summary_query = summary_df.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .trigger(processingTime="5 seconds") \
        .start()

    print("All streaming queries started successfully!")
    print("Processing data... Check the console output for results.")
    
    # Wait for queries to terminate
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main() 