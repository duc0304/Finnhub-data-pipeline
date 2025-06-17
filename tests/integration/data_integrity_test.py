#!/usr/bin/env python3
"""
Data Integrity Testing Script
Kiểm tra tính toàn vẹn dữ liệu từ Finnhub → Cassandra
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set
import hashlib
import uuid
from cassandra.cluster import Cluster
from kafka import KafkaProducer, KafkaConsumer
import websockets

# Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'finnhub-trades'
CASSANDRA_HOSTS = ['127.0.0.1']
CASSANDRA_KEYSPACE = 'finnhub'
TEST_DURATION = 600  # 10 minutes
EXPECTED_MESSAGE_COUNT = 1000

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIntegrityTester:
    def __init__(self):
        self.sent_messages = {}  # message_id -> message_data
        self.received_messages = {}  # message_id -> message_data
        self.cassandra_messages = {}  # message_id -> message_data
        self.missing_messages = set()
        self.duplicate_messages = set()
        self.corrupted_messages = set()
        
    def generate_test_message(self, symbol: str) -> Dict:
        """Tạo test message với checksum để verify integrity"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        message = {
            'id': message_id,
            'symbol': symbol,
            'timestamp': timestamp.isoformat(),
            'price': 50000.0 + (hash(message_id) % 10000),  # Random but deterministic
            'volume': 100 + (hash(message_id) % 1000),
            'trade_conditions': ['test'],
            'test_marker': True  # Đánh dấu đây là test message
        }
        
        # Tạo checksum để verify integrity
        message_str = json.dumps(message, sort_keys=True)
        message['checksum'] = hashlib.md5(message_str.encode()).hexdigest()
        
        return message
    
    async def send_test_messages(self, count: int = EXPECTED_MESSAGE_COUNT):
        """Gửi test messages vào Kafka"""
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None
        )
        
        symbols = ['BINANCE:BTCUSDT', 'BINANCE:ETHUSDT', 'BINANCE:SOLUSDT']
        
        logger.info(f"Sending {count} test messages...")
        
        for i in range(count):
            symbol = symbols[i % len(symbols)]
            message = self.generate_test_message(symbol)
            
            # Store sent message for verification
            self.sent_messages[message['id']] = message
            
            # Send to Kafka
            producer.send(
                KAFKA_TOPIC,
                key=message['id'],
                value=message
            )
            
            if i % 100 == 0:
                logger.info(f"Sent {i} messages...")
            
            await asyncio.sleep(0.01)  # 100 messages/second
        
        producer.flush()
        producer.close()
        logger.info(f"Finished sending {count} test messages")
    
    async def consume_kafka_messages(self, timeout: int = 60):
        """Consume messages từ Kafka để verify"""
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=timeout * 1000,
            auto_offset_reset='earliest'
        )
        
        logger.info("Consuming messages from Kafka...")
        
        for message in consumer:
            try:
                data = message.value
                
                # Only process test messages
                if not data.get('test_marker'):
                    continue
                
                message_id = data.get('id')
                if message_id:
                    # Check for duplicates
                    if message_id in self.received_messages:
                        self.duplicate_messages.add(message_id)
                        logger.warning(f"Duplicate message detected: {message_id}")
                    
                    self.received_messages[message_id] = data
                    
                    # Verify checksum
                    original_checksum = data.pop('checksum', None)
                    if original_checksum:
                        message_str = json.dumps(data, sort_keys=True)
                        calculated_checksum = hashlib.md5(message_str.encode()).hexdigest()
                        
                        if original_checksum != calculated_checksum:
                            self.corrupted_messages.add(message_id)
                            logger.error(f"Corrupted message detected: {message_id}")
            
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")
        
        consumer.close()
        logger.info(f"Consumed {len(self.received_messages)} messages from Kafka")
    
    async def verify_cassandra_data(self):
        """Verify data trong Cassandra"""
        cluster = Cluster(CASSANDRA_HOSTS)
        session = cluster.connect(CASSANDRA_KEYSPACE)
        
        logger.info("Verifying data in Cassandra...")
        
        # Query all test messages
        rows = session.execute("""
            SELECT * FROM trades 
            WHERE symbol IN ('BINANCE:BTCUSDT', 'BINANCE:ETHUSDT', 'BINANCE:SOLUSDT')
            AND ingest_timestamp > ?
        """, [datetime.now() - timedelta(hours=1)])
        
        for row in rows:
            # Reconstruct message for comparison
            message_data = {
                'symbol': row.symbol,
                'timestamp': row.trade_timestamp.isoformat(),
                'price': row.price,
                'volume': row.volume,
                'trade_conditions': row.trade_conditions
            }
            
            # Try to match with sent messages
            # (This is simplified - in real scenario, you'd need better matching logic)
            for msg_id, sent_msg in self.sent_messages.items():
                if (sent_msg['symbol'] == message_data['symbol'] and 
                    abs(sent_msg['price'] - message_data['price']) < 0.01):
                    self.cassandra_messages[msg_id] = message_data
                    break
        
        cluster.shutdown()
        logger.info(f"Found {len(self.cassandra_messages)} messages in Cassandra")
    
    async def analyze_data_integrity(self):
        """Phân tích tính toàn vẹn dữ liệu"""
        
        # Find missing messages
        sent_ids = set(self.sent_messages.keys())
        received_ids = set(self.received_messages.keys())
        cassandra_ids = set(self.cassandra_messages.keys())
        
        self.missing_messages = sent_ids - received_ids
        missing_in_cassandra = sent_ids - cassandra_ids
        
        # Calculate statistics
        total_sent = len(self.sent_messages)
        total_received = len(self.received_messages)
        total_in_cassandra = len(self.cassandra_messages)
        total_missing = len(self.missing_messages)
        total_duplicates = len(self.duplicate_messages)
        total_corrupted = len(self.corrupted_messages)
        missing_cassandra = len(missing_in_cassandra)
        
        # Calculate percentages
        delivery_rate = (total_received / total_sent * 100) if total_sent > 0 else 0
        cassandra_rate = (total_in_cassandra / total_sent * 100) if total_sent > 0 else 0
        corruption_rate = (total_corrupted / total_received * 100) if total_received > 0 else 0
        duplicate_rate = (total_duplicates / total_received * 100) if total_received > 0 else 0
        
        # Print results
        print("\n" + "="*60)
        print("🔍 DATA INTEGRITY TEST RESULTS")
        print("="*60)
        print(f"📤 Total Messages Sent: {total_sent}")
        print(f"📥 Total Messages Received: {total_received}")
        print(f"🗄️  Total Messages in Cassandra: {total_in_cassandra}")
        print(f"❌ Missing Messages: {total_missing}")
        print(f"📊 Delivery Rate: {delivery_rate:.2f}%")
        print(f"🗄️  Cassandra Persistence Rate: {cassandra_rate:.2f}%")
        print("-" * 60)
        print(f"🔄 Duplicate Messages: {total_duplicates}")
        print(f"📊 Duplicate Rate: {duplicate_rate:.2f}%")
        print(f"💥 Corrupted Messages: {total_corrupted}")
        print(f"📊 Corruption Rate: {corruption_rate:.2f}%")
        print(f"🗄️  Missing in Cassandra: {missing_cassandra}")
        print("="*60)
        
        # Pass/Fail criteria
        target_delivery_rate = 99.9  # %
        target_corruption_rate = 0.1  # %
        target_duplicate_rate = 0.1  # %
        
        results = {
            'delivery_pass': delivery_rate >= target_delivery_rate,
            'corruption_pass': corruption_rate <= target_corruption_rate,
            'duplicate_pass': duplicate_rate <= target_duplicate_rate,
            'cassandra_pass': cassandra_rate >= target_delivery_rate
        }
        
        print("🎯 PASS/FAIL RESULTS:")
        print(f"✅ Delivery Rate: {'PASS' if results['delivery_pass'] else 'FAIL'}")
        print(f"✅ Corruption Rate: {'PASS' if results['corruption_pass'] else 'FAIL'}")
        print(f"✅ Duplicate Rate: {'PASS' if results['duplicate_pass'] else 'FAIL'}")
        print(f"✅ Cassandra Persistence: {'PASS' if results['cassandra_pass'] else 'FAIL'}")
        
        overall_pass = all(results.values())
        print(f"\n🏆 OVERALL RESULT: {'PASS' if overall_pass else 'FAIL'}")
        
        # Save detailed results
        await self.save_integrity_results({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_sent': total_sent,
                'total_received': total_received,
                'total_in_cassandra': total_in_cassandra,
                'delivery_rate': delivery_rate,
                'cassandra_rate': cassandra_rate,
                'corruption_rate': corruption_rate,
                'duplicate_rate': duplicate_rate
            },
            'issues': {
                'missing_messages': list(self.missing_messages)[:100],  # First 100
                'duplicate_messages': list(self.duplicate_messages),
                'corrupted_messages': list(self.corrupted_messages),
                'missing_in_cassandra': list(missing_in_cassandra)[:100]
            },
            'pass_fail': results,
            'overall_pass': overall_pass
        })
    
    async def save_integrity_results(self, results: Dict):
        """Lưu kết quả test"""
        filename = f"data_integrity_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {filename}")

class SchemaValidationTester:
    """Test schema validation với Avro"""
    
    def __init__(self):
        self.schema_violations = []
    
    async def test_avro_schema_compliance(self):
        """Test Avro schema compliance"""
        # This would require the actual Avro schema file
        # For now, we'll simulate basic schema validation
        
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=30000,
            auto_offset_reset='latest'
        )
        
        required_fields = ['symbol', 'price', 'volume', 'timestamp']
        
        logger.info("Testing schema compliance...")
        
        for message in consumer:
            try:
                data = message.value
                
                # Check required fields
                for field in required_fields:
                    if field not in data:
                        self.schema_violations.append({
                            'type': 'missing_field',
                            'field': field,
                            'message': data
                        })
                
                # Check data types
                if 'price' in data and not isinstance(data['price'], (int, float)):
                    self.schema_violations.append({
                        'type': 'invalid_type',
                        'field': 'price',
                        'expected': 'number',
                        'actual': type(data['price']).__name__
                    })
                
                if 'volume' in data and not isinstance(data['volume'], int):
                    self.schema_violations.append({
                        'type': 'invalid_type',
                        'field': 'volume',
                        'expected': 'int',
                        'actual': type(data['volume']).__name__
                    })
            
            except Exception as e:
                self.schema_violations.append({
                    'type': 'parse_error',
                    'error': str(e)
                })
        
        consumer.close()
        
        violation_count = len(self.schema_violations)
        print(f"\n📋 Schema Validation Results:")
        print(f"❌ Schema Violations: {violation_count}")
        
        if violation_count == 0:
            print("✅ SCHEMA VALIDATION: PASS")
        else:
            print("❌ SCHEMA VALIDATION: FAIL")
            print("First 5 violations:")
            for violation in self.schema_violations[:5]:
                print(f"  - {violation}")

async def main():
    """Main test runner"""
    print("🔍 Starting Data Integrity Testing Suite")
    
    # Data integrity test
    integrity_tester = DataIntegrityTester()
    
    print("\n📤 Sending test messages...")
    await integrity_tester.send_test_messages()
    
    print("\n⏱️ Waiting for processing...")
    await asyncio.sleep(30)  # Wait for messages to be processed
    
    print("\n📥 Consuming messages from Kafka...")
    await integrity_tester.consume_kafka_messages()
    
    print("\n🗄️ Verifying Cassandra data...")
    await integrity_tester.verify_cassandra_data()
    
    print("\n📊 Analyzing results...")
    await integrity_tester.analyze_data_integrity()
    
    # Schema validation test
    print("\n📋 Testing schema validation...")
    schema_tester = SchemaValidationTester()
    await schema_tester.test_avro_schema_compliance()
    
    print("\n✅ Data Integrity Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main()) 