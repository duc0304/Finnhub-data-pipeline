from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_spark_session():
    """Tạo và configure Spark session với Cassandra connector"""
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
    
    return spark

def test_cassandra_connection(spark):
    """Test kết nối Cassandra"""
    try:
        test_df = spark.createDataFrame([("test_keyHEHEHE", "test_valueHEHEHE")], ["key", "value"])
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
        return True
    except Exception as e:
        print(f"Warning: Could not test connection to Cassandra: {e}")
        print("Will continue and try to process data anyway...")
        return False

def get_kafka_dataframe(spark):
    """Tạo Kafka streaming DataFrame hỗ trợ cả STOCK và CRYPTO data"""
    # Define flexible schema cho cả stock và crypto data
    schema = StructType([
        StructField("data", ArrayType(StructType([
            StructField("c", ArrayType(StringType()), True),  # trade_conditions - chỉ có trong STOCK
            StructField("p", DoubleType(), True),              # price  
            StructField("s", StringType(), True),              # symbol
            StructField("t", LongType(), True),                # timestamp
            StructField("v", DoubleType(), True)               # volume (DOUBLE để hỗ trợ crypto fractional volume)
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
        from_json(col("value").cast("string"), schema).alias("parsed_data")
    ).select(
        explode("parsed_data.data").alias("trade")
    ).select(
        "trade.*"
    )

    # Rename columns và xác định asset type
    df = df \
        .withColumnRenamed("c", "trade_conditions") \
        .withColumnRenamed("p", "price") \
        .withColumnRenamed("s", "symbol") \
        .withColumnRenamed("t", "trade_timestamp") \
        .withColumnRenamed("v", "volume") \
        .withColumn("trade_timestamp", (col("trade_timestamp") / 1000).cast("timestamp")) \
        .withColumn("ingest_timestamp", current_timestamp()) \
        .withColumn("trade_date", to_date(col("trade_timestamp"))) \
        .withColumn("asset_type", 
            when(col("symbol").contains("BINANCE:") | col("symbol").contains("CRYPTO:"), "CRYPTO")
            .when(col("symbol").rlike("^[A-Z]{1,5}$"), "STOCK")  # Typical stock symbols (1-5 uppercase letters)
            .otherwise("OTHER")
        ) \
        .withColumn("trade_conditions", 
            when(col("asset_type") == "CRYPTO", lit(None).cast("array<string>"))  # NULL for crypto
            .otherwise(col("trade_conditions"))  # Keep original for stocks
        )
    
    print("DataFrame processed with asset type detection")
    return df 