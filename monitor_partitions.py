#!/usr/bin/env python3
"""
Monitor Kafka partition distribution để kiểm tra load balancing
"""

import time
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.structs import TopicPartition
import json
from collections import defaultdict, Counter

def check_partition_distribution():
    """Kiểm tra phân phối message trên các partitions"""
    
    topic_name = "finnhub_trades"
    bootstrap_servers = ["localhost:9092", "localhost:9093", "localhost:9094"]
    
    print("=== KAFKA PARTITION DISTRIBUTION MONITOR ===")
    print(f"Topic: {topic_name}")
    print(f"Brokers: {bootstrap_servers}")
    
    # Get topic metadata
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    
    try:
        # Check topic configuration
        metadata = admin_client.describe_topics([topic_name])
        topic_metadata = metadata[topic_name]
        
        print(f"\n📊 Topic Configuration:")
        print(f"   Partitions: {len(topic_metadata.partitions)}")
        print(f"   Replication Factor: {len(topic_metadata.partitions[0].replicas)}")
        
        # Show partition info
        print(f"\n📋 Partition Details:")
        for partition in topic_metadata.partitions:
            leader = partition.leader
            replicas = [r.id for r in partition.replicas]
            print(f"   Partition {partition.partition}: Leader=Broker{leader}, Replicas={replicas}")
            
    except Exception as e:
        print(f"❌ Error getting topic metadata: {e}")
        return
    
    # Monitor message distribution
    print(f"\n🔄 Monitoring message distribution (30 seconds)...")
    
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
        auto_offset_reset='latest',  # Only new messages
        enable_auto_commit=True,
        group_id='partition_monitor'
    )
    
    partition_counts = Counter()
    symbol_partition_mapping = defaultdict(set)
    total_messages = 0
    
    start_time = time.time()
    monitor_duration = 30  # seconds
    
    try:
        for message in consumer:
            if time.time() - start_time > monitor_duration:
                break
                
            partition = message.partition
            key = message.key
            value = message.value
            
            partition_counts[partition] += 1
            total_messages += 1
            
            # Track symbol-to-partition mapping
            if 'data' in value and isinstance(value['data'], list):
                for trade in value['data']:
                    if 's' in trade:
                        symbol = trade['s']
                        symbol_partition_mapping[symbol].add(partition)
            
            # Print progress every 50 messages
            if total_messages % 50 == 0:
                print(f"   📈 Messages processed: {total_messages}")
                
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
    finally:
        consumer.close()
    
    # Print results
    print(f"\n📊 DISTRIBUTION RESULTS (Last {monitor_duration}s):")
    print(f"   Total Messages: {total_messages}")
    
    if total_messages > 0:
        print(f"\n📈 Partition Distribution:")
        for partition in sorted(partition_counts.keys()):
            count = partition_counts[partition]
            percentage = (count / total_messages) * 100
            bar = "█" * int(percentage / 2)  # Visual bar
            print(f"   Partition {partition}: {count:4d} messages ({percentage:5.1f}%) {bar}")
        
        print(f"\n🎯 Symbol-to-Partition Mapping:")
        for symbol, partitions in symbol_partition_mapping.items():
            partitions_list = sorted(list(partitions))
            print(f"   {symbol:20s}: Partitions {partitions_list}")
        
        # Analysis
        unique_partitions_used = len(partition_counts)
        max_partition_load = max(partition_counts.values()) if partition_counts else 0
        min_partition_load = min(partition_counts.values()) if partition_counts else 0
        load_imbalance = max_partition_load - min_partition_load
        
        print(f"\n🔍 Analysis:")
        print(f"   Partitions Used: {unique_partitions_used}/6")
        print(f"   Load Imbalance: {load_imbalance} messages (Max: {max_partition_load}, Min: {min_partition_load})")
        
        if unique_partitions_used == 6 and load_imbalance < total_messages * 0.3:
            print("   ✅ GOOD: Well-distributed across partitions")
        elif unique_partitions_used < 6:
            print("   ⚠️  WARNING: Not all partitions are being used")
        else:
            print("   ❌ ISSUE: High load imbalance detected")
    else:
        print("   ❌ No messages received during monitoring period")

def main():
    """Main function"""
    try:
        check_partition_distribution()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 