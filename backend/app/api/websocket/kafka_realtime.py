from fastapi import WebSocket, WebSocketDisconnect
from kafka import KafkaConsumer
from datetime import datetime
import json
import asyncio
import logging
from typing import Set, Dict
import threading
from queue import Queue
import os

logger = logging.getLogger(__name__)

class KafkaWebSocketManager:
    """WebSocket manager với Kafka real-time streaming"""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.kafka_consumers: Dict[str, KafkaConsumer] = {}
        self.message_queues: Dict[str, Queue] = {}
        self.consumer_threads: Dict[str, threading.Thread] = {}
        
        # Kafka configuration
        self.kafka_config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka1:29092,kafka2:29093,kafka3:29094').split(','),
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'group_id': 'websocket_realtime_group',
            'value_deserializer': lambda x: json.loads(x.decode('utf-8')),
            'consumer_timeout_ms': 1000
        }
        
    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        
        symbol = symbol.upper()
        
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        
        if symbol not in self.kafka_consumers:
            await self._start_kafka_consumer(symbol)
        
        logger.info(f"WebSocket connected to REAL-TIME {symbol} stream")
        
    def disconnect(self, websocket: WebSocket, symbol: str):
        symbol = symbol.upper()
        
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            
            if len(self.active_connections[symbol]) == 0:
                self._stop_kafka_consumer(symbol)
                del self.active_connections[symbol]
        
        logger.info(f"WebSocket disconnected from {symbol} stream")
        
    async def _start_kafka_consumer(self, symbol: str):
        try:
            consumer = KafkaConsumer('finnhub_trades', **self.kafka_config)
            
            self.kafka_consumers[symbol] = consumer
            self.message_queues[symbol] = Queue()
            
            consumer_thread = threading.Thread(
                target=self._kafka_consumer_loop, 
                args=(symbol, consumer),
                daemon=True
            )
            consumer_thread.start()
            self.consumer_threads[symbol] = consumer_thread
            
            logger.info(f"Started Kafka consumer for {symbol}")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer for {symbol}: {e}")
            
    def _kafka_consumer_loop(self, symbol: str, consumer: KafkaConsumer):
        try:
            for message in consumer:
                try:
                    trade_data = message.value
                    
                    if self._extract_symbol_from_trade(trade_data) == symbol:
                        processed_data = self._process_trade_data(trade_data)
                        
                        if symbol in self.message_queues:
                            self.message_queues[symbol].put(processed_data)
                        
                except Exception as e:
                    logger.error(f"Error processing Kafka message for {symbol}: {e}")
                    
                if symbol not in self.kafka_consumers:
                    break
                    
        except Exception as e:
            logger.error(f"Kafka consumer loop error for {symbol}: {e}")
        finally:
            consumer.close()
            
    def _stop_kafka_consumer(self, symbol: str):
        if symbol in self.kafka_consumers:
            self.kafka_consumers[symbol].close()
            del self.kafka_consumers[symbol]
            
            if symbol in self.message_queues:
                del self.message_queues[symbol]
                
            if symbol in self.consumer_threads:
                del self.consumer_threads[symbol]
                
            logger.info(f"Stopped Kafka consumer for {symbol}")
    
    def _extract_symbol_from_trade(self, trade_data: dict) -> str:
        try:
            if 'data' in trade_data and isinstance(trade_data['data'], list):
                if len(trade_data['data']) > 0 and 's' in trade_data['data'][0]:
                    return trade_data['data'][0]['s'].upper()
            
            if 'symbol' in trade_data:
                return trade_data['symbol'].upper()
                
            return ""
        except:
            return ""
    
    def _process_trade_data(self, raw_trade_data: dict) -> dict:
        try:
            processed = {
                "type": "live_trade",
                "timestamp": datetime.now().isoformat(),
                "server_time": datetime.now().isoformat(),
                "raw_data": raw_trade_data
            }
            
            if 'data' in raw_trade_data and isinstance(raw_trade_data['data'], list):
                trades = raw_trade_data['data']
                if len(trades) > 0:
                    latest_trade = trades[-1]
                    
                    processed.update({
                        "symbol": latest_trade.get('s', ''),
                        "price": latest_trade.get('p', 0),
                        "volume": latest_trade.get('v', 0),
                        "trade_timestamp": latest_trade.get('t', 0),
                        "trade_conditions": latest_trade.get('c', [])
                    })
            
            if 'ingest_timestamp' in raw_trade_data:
                processed['ingest_timestamp'] = raw_trade_data['ingest_timestamp']
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing trade data: {e}")
            return {
                "type": "live_trade",
                "timestamp": datetime.now().isoformat(),
                "error": "Failed to process trade data",
                "raw_data": raw_trade_data
            }

# Global manager
kafka_websocket_manager = KafkaWebSocketManager()

async def kafka_realtime_websocket(websocket: WebSocket, symbol: str):
    """TRUE Real-time WebSocket endpoint listen trực tiếp từ Kafka"""
    symbol = symbol.upper()
    
    try:
        await kafka_websocket_manager.connect(websocket, symbol)
        
        welcome_msg = {
            "type": "connection",
            "symbol": symbol,
            "message": f"Connected to TRUE real-time {symbol} Kafka stream",
            "features": ["Zero-delay", "Live trades", "Kafka direct stream"],
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # Main loop - check message queue và send tới client
        while True:
            if symbol in kafka_websocket_manager.message_queues:
                message_queue = kafka_websocket_manager.message_queues[symbol]
                
                try:
                    if not message_queue.empty():
                        trade_message = message_queue.get_nowait()
                        await websocket.send_text(json.dumps(trade_message))
                except:
                    pass
            
            await asyncio.sleep(0.01)  # 10ms check interval
            
    except WebSocketDisconnect:
        kafka_websocket_manager.disconnect(websocket, symbol)
        logger.info(f"Kafka WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"Kafka WebSocket error for {symbol}: {e}")
        kafka_websocket_manager.disconnect(websocket, symbol)

async def kafka_multi_symbol_websocket(websocket: WebSocket, symbols: str):
    """
    Multi-symbol real-time WebSocket
    
    Args:
        symbols: Comma-separated symbols (e.g., "AAPL,MSFT,GOOGL")
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    try:
        # Connect to all symbols
        for symbol in symbol_list:
            await kafka_websocket_manager.connect(websocket, symbol)
        
        # Welcome message
        welcome_msg = {
            "type": "multi_connection",
            "symbols": symbol_list,
            "message": f"Connected to {len(symbol_list)} real-time streams",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # Main loop cho multiple symbols
        while True:
            for symbol in symbol_list:
                if symbol in kafka_websocket_manager.message_queues:
                    message_queue = kafka_websocket_manager.message_queues[symbol]
                    
                    try:
                        if not message_queue.empty():
                            trade_message = message_queue.get_nowait()
                            await websocket.send_text(json.dumps(trade_message))
                    except:
                        pass
            
            await asyncio.sleep(0.01)  # 10ms check
            
    except WebSocketDisconnect:
        # Disconnect from all symbols
        for symbol in symbol_list:
            kafka_websocket_manager.disconnect(websocket, symbol)
        logger.info(f"Multi-symbol Kafka WebSocket disconnected")
    except Exception as e:
        logger.error(f"Multi-symbol Kafka WebSocket error: {e}")
        for symbol in symbol_list:
            kafka_websocket_manager.disconnect(websocket, symbol) 