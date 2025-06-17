import os
import json
import websocket
import time
import logging
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('finnhub-producer')

# Load environment variables
load_dotenv()

class FinnhubProducer:
    def __init__(self):
        # Kafka connection setup
        self.topic_name = os.getenv('KAFKA_TOPIC_NAME', 'finnhub_trades')
        bootstrap_servers = self._get_kafka_servers()
        
        logger.info(f"Connecting to Kafka brokers: {bootstrap_servers}")
        
        # Setup topic if not exists
        self._setup_topic(bootstrap_servers)
        
        # Initialize Kafka producer với ULTRA LOW LATENCY settings
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # LATENCY OPTIMIZED SETTINGS
            acks=1,                 # Chỉ chờ leader ack (thay vì all replicas)
            retries=1,              # Giảm retries để tránh delay
            compression_type=None,   # Tắt compression để giảm CPU overhead
            # MINIMAL BATCHING cho real-time
            batch_size=1024,        # 1KB batch size (nhỏ hơn)
            linger_ms=0,            # KHÔNG chờ batch - gửi ngay lập tức
            buffer_memory=16777216, # 16MB buffer (đủ dùng)
            max_in_flight_requests_per_connection=1,  # Tránh reordering
            # SOCKET OPTIMIZATIONS
            send_buffer_bytes=131072,    # 128KB socket send buffer
            receive_buffer_bytes=65536,  # 64KB socket receive buffer
            request_timeout_ms=5000,     # 5s timeout
            # Partitioner strategy
            partitioner=None,       # Use default hash-based partitioner
        )
        
        # Get tickers from environment
        self.tickers = json.loads(os.getenv('FINNHUB_STOCKS_TICKERS'))
        logger.info(f"Producer initialized with {len(self.tickers)} tickers")
        
        # Initialize websocket
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            f'wss://ws.finnhub.io?token={os.getenv("FINNHUB_API_TOKEN")}',
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open

    def _get_kafka_servers(self):
        """Lấy danh sách Kafka servers"""
        kafka_server = os.getenv('KAFKA_SERVER', 'kafka1')
        kafka_port = os.getenv('KAFKA_PORT', '29092')
        
        if ',' in kafka_server:
            return kafka_server
        else:
            if kafka_server == 'kafka1':
                return f"{kafka_server}:{kafka_port},kafka2:29093,kafka3:29094"
            return f"{kafka_server}:{kafka_port}"

    def _setup_topic(self, bootstrap_servers):
        """Setup Kafka topic"""
        num_partitions = int(os.getenv('KAFKA_NUM_PARTITIONS', '6'))
        replication_factor = int(os.getenv('KAFKA_REPLICATION_FACTOR', '3'))
        
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            
            topics = admin_client.list_topics()
            if self.topic_name not in topics:
                logger.info(f"Creating topic {self.topic_name}")
                topic = NewTopic(
                    name=self.topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                    topic_configs={'cleanup.policy': 'delete', 'retention.ms': '604800000'}
                )
                admin_client.create_topics([topic])
            else:
                logger.info(f"Topic {self.topic_name} already exists")
            
            admin_client.close()
        except Exception as e:
            logger.error(f"Error setting up topic: {e}")

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            
            # Đảm bảo data là một từ điển
            if not isinstance(data, dict):
                data = {"raw_data": str(data), "timestamp": int(time.time() * 1000)}
            
            # Thêm HIGH PRECISION timestamp cho latency measurement
            current_time_ms = time.time() * 1000
            data['ingest_timestamp'] = int(current_time_ms)
            data['producer_timestamp'] = current_time_ms  # Float precision
            data['finnhub_receive_time'] = int(time.time() * 1000)
            
            # Improved partition strategy để phân phối đều load
            message_key = None
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                trade_data = data['data'][0]
                if 's' in trade_data and 't' in trade_data:
                    symbol = trade_data['s']
                    timestamp = trade_data['t']
                    # Combine symbol + timestamp để tạo key unique hơn
                    # Điều này giúp phân phối trades của cùng symbol ra multiple partitions
                    message_key = f"{symbol}_{timestamp % 1000}"  # Modulo 1000 để tạo variation
                elif 's' in trade_data:
                    message_key = trade_data['s']
            
            # Gửi message tới Kafka với IMMEDIATE FLUSH cho low latency
            start_time = time.time() * 1000
            
            if message_key:
                future = self.producer.send(self.topic_name, value=data, key=message_key)
                logger.debug(f"Sent message with key: {message_key}")
            else:
                # Fallback: no key = round-robin partition assignment
                future = self.producer.send(self.topic_name, value=data)
                logger.debug("Sent message without key (round-robin)")
            
            # FORCE IMMEDIATE SEND - không chờ batch
            self.producer.flush()
            
            # Log latency cho debugging
            send_time = (time.time() * 1000) - start_time
            if send_time > 50:  # Log nếu > 50ms
                logger.warning(f"High Kafka send latency: {send_time:.1f}ms")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.info(f"WebSocket connection closed with status {close_status_code}: {close_msg}")
        # Thử kết nối lại sau 5 giây
        time.sleep(5)
        self.ws.run_forever()

    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        
        # Đăng ký các ticker
        for ticker in self.tickers:
            self.ws.send(json.dumps({"type": "subscribe", "symbol": ticker}))
            logger.info(f"Subscribed to {ticker}")

    def run(self):
        logger.info("Starting Finnhub WebSocket producer")
        self.ws.run_forever()

if __name__ == "__main__":
    producer = FinnhubProducer()
    
    # Logic tái kết nối
    while True:
        try:
            producer.run()
        except Exception as e:
            logger.error(f"Producer crashed: {e}")
            logger.info("Reconnecting in 5 seconds...")
            time.sleep(5) 