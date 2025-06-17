from spark_config import create_spark_session, test_cassandra_connection, get_kafka_dataframe
from streaming_processors import (
    save_to_cassandra_trades, save_to_cassandra_aggregates, save_to_cassandra_ohlc,
    calculate_technical_indicators, create_aggregated_dataframe, create_ohlc_dataframe
)
import time

def main():
    """Main orchestration function"""
    # Setup Spark session and connections
    spark = create_spark_session()
    test_cassandra_connection(spark)
    
    # Get streaming dataframe from Kafka
    df = get_kafka_dataframe(spark)

    # ================== RAW TRADES PROCESSING ==================
    print("Starting trade stream to Cassandra...")
    query = df.writeStream \
        .foreachBatch(save_to_cassandra_trades) \
        .outputMode("append") \
        .start()

    # ================== AGGREGATES PROCESSING ==================
    print("Starting aggregation stream to Cassandra...")
    summary_df = create_aggregated_dataframe(df)
    summary_query = summary_df.writeStream \
        .foreachBatch(save_to_cassandra_aggregates) \
        .outputMode("update") \
        .trigger(processingTime="5 seconds") \
        .start()

    # ================== OHLC DATA PROCESSING ==================
    print("Creating OHLC data stream...")
    ohlc_df = create_ohlc_dataframe(df)
    ohlc_query = ohlc_df.writeStream \
        .foreachBatch(save_to_cassandra_ohlc) \
        .outputMode("update") \
        .trigger(processingTime="5 seconds") \
        .start()

    # ================== TECHNICAL INDICATORS PROCESSING ==================
    print("Creating technical indicators stream...")
    
    # Wrapper function to pass spark instance to technical indicators
    def tech_indicators_wrapper(batch_df, batch_id):
        calculate_technical_indicators(spark, batch_df, batch_id)
    
    tech_query = ohlc_df.writeStream \
        .foreachBatch(tech_indicators_wrapper) \
        .outputMode("update") \
        .trigger(processingTime="10 seconds") \
        .start()

    print("All streaming queries started successfully!")
    print("Processing data... Check the console output for results.")
    print("Available streams:")
    print("  1. Raw trades -> Cassandra.trades")
    print("  2. Aggregated data -> Cassandra.aggregates") 
    print("  3. OHLC data -> Cassandra.ohlc_data")
    print("  4. Technical indicators -> Cassandra.technical_indicators")
    
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