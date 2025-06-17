#!/usr/bin/env python3
"""
Simple WebSocket Server để hiển thị Kafka trades lên frontend
Chạy: python websocket_server.py
"""

import asyncio
import websockets
import json
import logging
from kafka import KafkaConsumer
import threading
from datetime import datetime
import time

# Config
KAFKA_SERVERS = ['localhost:9092', 'localhost:9093', 'localhost:9094']
KAFKA_TOPIC = 'finnhub_trades'
WEBSOCKET_HOST = 'localhost'
WEBSOCKET_PORT = 8080

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWebSocketServer:
    def __init__(self):
        self.connected_clients = set()
        self.kafka_consumer = None
        
    def start_kafka_consumer(self):
        """Start Kafka consumer trong thread riêng"""
        def consume_messages():
            try:
                self.kafka_consumer = KafkaConsumer(
                    KAFKA_TOPIC,
                    bootstrap_servers=KAFKA_SERVERS,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    group_id='websocket-display-group'
                )
                
                logger.info(f"🎯 Kafka consumer started - listening to: {KAFKA_TOPIC}")
                
                for message in self.kafka_consumer:
                    try:
                        trade_data = message.value
                        
                        # Add WebSocket server timing for latency measurement
                        websocket_timestamp = int(time.time() * 1000)
                        
                        # Enhanced message with timing metadata
                        enhanced_message = {
                            'type': 'trade',
                            'data': trade_data,
                            'timing': {
                                'kafka_timestamp': trade_data.get('ingest_timestamp', websocket_timestamp),
                                'websocket_timestamp': websocket_timestamp,
                                'server_processing_time': time.time() * 1000
                            },
                            'metadata': {
                                'server_id': 'ws-server-1',
                                'message_size': len(json.dumps(trade_data)),
                                'client_count': len(self.connected_clients)
                            }
                        }
                        
                        # Broadcast đến tất cả clients
                        if self.connected_clients:
                            asyncio.run_coroutine_threadsafe(
                                self.broadcast_trade(enhanced_message),
                                self.event_loop
                            )
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
            except Exception as e:
                logger.error(f"Kafka consumer error: {e}")
        
        thread = threading.Thread(target=consume_messages, daemon=True)
        thread.start()
    
    async def broadcast_trade(self, enhanced_message):
        """Broadcast trade data đến tất cả connected clients"""
        if not self.connected_clients:
            return
            
        # Add final broadcast timestamp
        enhanced_message['timing']['broadcast_timestamp'] = int(time.time() * 1000)
        
        message = json.dumps(enhanced_message)
        
        # Send đến tất cả clients
        disconnected = []
        for client in self.connected_clients:
            try:
                await client.send(message)
            except:
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.connected_clients.discard(client)
    
    async def handle_client(self, websocket):
        """Xử lý client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"📱 New client connected: {client_id}")
        
        self.connected_clients.add(websocket)
        
        try:
            # Send welcome message với server info
            await websocket.send(json.dumps({
                'type': 'connected',
                'message': 'Connected to Finnhub trades stream',
                'timestamp': datetime.now().isoformat(),
                'server_info': {
                    'server_time': int(time.time() * 1000),
                    'client_id': client_id,
                    'total_clients': len(self.connected_clients),
                    'kafka_topic': KAFKA_TOPIC
                }
            }))
            
            # Handle incoming messages từ client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'latency_ping':
                        # Respond to latency ping immediately
                        response = {
                            'type': 'latency_pong',
                            'client_timestamp': data.get('timestamp'),
                            'server_timestamp': int(time.time() * 1000),
                            'ping_id': data.get('ping_id')
                        }
                        await websocket.send(json.dumps(response))
                except:
                    pass  # Ignore invalid messages
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"📱 Client disconnected: {client_id}")
        finally:
            self.connected_clients.discard(websocket)
    
    async def start_server(self):
        """Start WebSocket server"""
        self.event_loop = asyncio.get_running_loop()
        
        # Start Kafka consumer
        self.start_kafka_consumer()
        
        # Start WebSocket server
        logger.info(f"🚀 Starting WebSocket server on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        
        async with websockets.serve(self.handle_client, WEBSOCKET_HOST, WEBSOCKET_PORT):
            logger.info("✅ WebSocket server started! Open latency_dashboard.html in browser")
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    server = SimpleWebSocketServer()
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("�� Server stopped") 