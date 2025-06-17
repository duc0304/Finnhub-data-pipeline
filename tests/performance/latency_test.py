#!/usr/bin/env python3
"""
End-to-End Latency Testing Script
Đo độ trễ từ Finnhub WebSocket → Frontend WebSocket
"""

import asyncio
import websockets
import json
import time
import statistics
import logging
from datetime import datetime
from typing import List, Dict
import uuid

# Configuration
FINNHUB_WS_URL = "wss://ws.finnhub.io"
FRONTEND_WS_URL = "ws://localhost:8080/ws"
FINNHUB_API_TOKEN = "your_token_here"
TEST_SYMBOLS = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT"]
TEST_DURATION = 300  # 5 minutes
SAMPLE_SIZE = 1000

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LatencyTester:
    def __init__(self):
        self.test_messages = {}
        self.latency_samples = []
        self.start_time = None
        
    async def generate_test_message(self, symbol: str) -> Dict:
        """Tạo test message với timestamp"""
        test_id = str(uuid.uuid4())
        timestamp = time.time() * 1000  # milliseconds
        
        message = {
            "type": "subscribe",
            "symbol": symbol,
            "test_id": test_id,
            "timestamp": timestamp
        }
        
        self.test_messages[test_id] = timestamp
        return message
    
    async def send_to_finnhub(self, websocket, symbol: str):
        """Gửi test message đến Finnhub"""
        try:
            # Subscribe to symbol
            subscribe_msg = {
                "type": "subscribe",
                "symbol": symbol
            }
            await websocket.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to {symbol}")
            
        except Exception as e:
            logger.error(f"Error sending to Finnhub: {e}")
    
    async def listen_frontend_ws(self):
        """Lắng nghe WebSocket từ Frontend"""
        try:
            async with websockets.connect(FRONTEND_WS_URL) as websocket:
                logger.info("Connected to Frontend WebSocket")
                
                async for message in websocket:
                    await self.process_frontend_message(message)
                    
        except Exception as e:
            logger.error(f"Frontend WebSocket error: {e}")
    
    async def process_frontend_message(self, message: str):
        """Xử lý message từ Frontend và tính latency"""
        try:
            data = json.loads(message)
            receive_time = time.time() * 1000
            
            # Tìm message gốc dựa trên symbol và timestamp gần nhất
            if 'symbol' in data and 'timestamp' in data:
                original_timestamp = data.get('original_timestamp')
                if original_timestamp:
                    latency = receive_time - original_timestamp
                    self.latency_samples.append(latency)
                    
                    logger.info(f"Latency: {latency:.2f}ms for {data['symbol']}")
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def run_latency_test(self):
        """Chạy test latency chính"""
        logger.info("Starting End-to-End Latency Test")
        self.start_time = time.time()
        
        # Kết nối đến Finnhub WebSocket
        finnhub_uri = f"{FINNHUB_WS_URL}?token={FINNHUB_API_TOKEN}"
        
        async with websockets.connect(finnhub_uri) as finnhub_ws:
            logger.info("Connected to Finnhub WebSocket")
            
            # Subscribe to test symbols
            for symbol in TEST_SYMBOLS:
                await self.send_to_finnhub(finnhub_ws, symbol)
            
            # Start listening to frontend
            frontend_task = asyncio.create_task(self.listen_frontend_ws())
            
            # Run test for specified duration
            await asyncio.sleep(TEST_DURATION)
            
            # Cancel frontend listener
            frontend_task.cancel()
        
        # Analyze results
        await self.analyze_results()
    
    async def analyze_results(self):
        """Phân tích kết quả test"""
        if not self.latency_samples:
            logger.error("No latency samples collected!")
            return
        
        # Calculate statistics
        mean_latency = statistics.mean(self.latency_samples)
        median_latency = statistics.median(self.latency_samples)
        p95_latency = self.percentile(self.latency_samples, 95)
        p99_latency = self.percentile(self.latency_samples, 99)
        min_latency = min(self.latency_samples)
        max_latency = max(self.latency_samples)
        
        # Print results
        print("\n" + "="*50)
        print("📊 LATENCY TEST RESULTS")
        print("="*50)
        print(f"📈 Total Samples: {len(self.latency_samples)}")
        print(f"⏱️  Mean Latency: {mean_latency:.2f}ms")
        print(f"📊 Median Latency: {median_latency:.2f}ms")
        print(f"🎯 P95 Latency: {p95_latency:.2f}ms")
        print(f"🚨 P99 Latency: {p99_latency:.2f}ms")
        print(f"⚡ Min Latency: {min_latency:.2f}ms")
        print(f"🔥 Max Latency: {max_latency:.2f}ms")
        print("="*50)
        
        # Pass/Fail criteria
        target_p95 = 100  # ms
        target_p99 = 200  # ms
        
        if p95_latency <= target_p95:
            print("✅ P95 LATENCY: PASS")
        else:
            print("❌ P95 LATENCY: FAIL")
            
        if p99_latency <= target_p99:
            print("✅ P99 LATENCY: PASS")
        else:
            print("❌ P99 LATENCY: FAIL")
        
        # Save results to file
        await self.save_results({
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(self.latency_samples),
            'mean_latency': mean_latency,
            'median_latency': median_latency,
            'p95_latency': p95_latency,
            'p99_latency': p99_latency,
            'min_latency': min_latency,
            'max_latency': max_latency,
            'raw_samples': self.latency_samples[:100]  # Save first 100 samples
        })
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def save_results(self, results: Dict):
        """Lưu kết quả test vào file"""
        filename = f"latency_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")

# Component-wise latency testing
class ComponentLatencyTester:
    """Test latency cho từng component riêng biệt"""
    
    async def test_kafka_latency(self):
        """Test Kafka produce-consume latency"""
        from kafka import KafkaProducer, KafkaConsumer
        import threading
        
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        consumer = KafkaConsumer(
            'test-latency',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        latencies = []
        
        def consume_messages():
            for message in consumer:
                receive_time = time.time() * 1000
                send_time = message.value.get('timestamp')
                if send_time:
                    latency = receive_time - send_time
                    latencies.append(latency)
                    print(f"Kafka latency: {latency:.2f}ms")
                
                if len(latencies) >= 100:
                    break
        
        # Start consumer in separate thread
        consumer_thread = threading.Thread(target=consume_messages)
        consumer_thread.start()
        
        # Send test messages
        for i in range(100):
            message = {
                'id': i,
                'timestamp': time.time() * 1000,
                'data': f'test_message_{i}'
            }
            producer.send('test-latency', message)
            await asyncio.sleep(0.1)  # 10 messages/second
        
        consumer_thread.join(timeout=30)
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            print(f"\n📊 Kafka Average Latency: {avg_latency:.2f}ms")
        
        producer.close()
        consumer.close()
    
    async def test_cassandra_latency(self):
        """Test Cassandra write/read latency"""
        from cassandra.cluster import Cluster
        
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect('finnhub')
        
        write_latencies = []
        read_latencies = []
        
        # Test writes
        for i in range(100):
            start_time = time.time() * 1000
            
            session.execute("""
                INSERT INTO trades (symbol, trade_timestamp, price, volume, ingest_timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ('TEST_SYMBOL', datetime.now(), 50000.0, 100, datetime.now()))
            
            end_time = time.time() * 1000
            write_latencies.append(end_time - start_time)
        
        # Test reads
        for i in range(100):
            start_time = time.time() * 1000
            
            session.execute("""
                SELECT * FROM trades WHERE symbol = 'TEST_SYMBOL' LIMIT 10
            """)
            
            end_time = time.time() * 1000
            read_latencies.append(end_time - start_time)
        
        avg_write = statistics.mean(write_latencies)
        avg_read = statistics.mean(read_latencies)
        
        print(f"\n📊 Cassandra Write Latency: {avg_write:.2f}ms")
        print(f"📊 Cassandra Read Latency: {avg_read:.2f}ms")
        
        cluster.shutdown()

async def main():
    """Main test runner"""
    print("🚀 Starting Latency Testing Suite")
    
    # End-to-end latency test
    e2e_tester = LatencyTester()
    await e2e_tester.run_latency_test()
    
    # Component latency tests
    component_tester = ComponentLatencyTester()
    
    print("\n🔧 Testing Kafka Latency...")
    await component_tester.test_kafka_latency()
    
    print("\n🔧 Testing Cassandra Latency...")
    await component_tester.test_cassandra_latency()
    
    print("\n✅ Latency Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main()) 