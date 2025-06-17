from fastapi import WebSocket, WebSocketDisconnect
from app.core.cassandra import get_cassandra_session
from datetime import datetime, date, timedelta
import json
import asyncio
import logging
from typing import Set, Dict
import time

logger = logging.getLogger(__name__)

class EnhancedConnectionManager:
    """Enhanced WebSocket manager với multiple update frequencies"""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.subscription_settings: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket, symbol: str, update_interval: int = 2):
        """
        Kết nối WebSocket với custom update interval
        
        Args:
            websocket: WebSocket connection
            symbol: Stock symbol
            update_interval: Update interval in seconds (1-30)
        """
        await websocket.accept()
        
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        
        self.active_connections[symbol].add(websocket)
        
        # Lưu settings cho connection này
        self.subscription_settings[websocket] = {
            'symbol': symbol,
            'update_interval': max(1, min(30, update_interval)),  # 1-30 seconds
            'last_update': 0,
            'message_count': 0
        }
        
        logger.info(f"Enhanced client connected to {symbol} with {update_interval}s interval")
        
    def disconnect(self, websocket: WebSocket):
        """Ngắt kết nối WebSocket"""
        if websocket in self.subscription_settings:
            symbol = self.subscription_settings[websocket]['symbol']
            
            if symbol in self.active_connections:
                self.active_connections[symbol].discard(websocket)
                if len(self.active_connections[symbol]) == 0:
                    del self.active_connections[symbol]
            
            del self.subscription_settings[websocket]
            logger.info(f"Enhanced client disconnected from {symbol}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Gửi message tới một WebSocket cụ thể"""
        try:
            await websocket.send_text(message)
            
            # Update message count
            if websocket in self.subscription_settings:
                self.subscription_settings[websocket]['message_count'] += 1
                
        except Exception as e:
            logger.error(f"Error sending enhanced message: {e}")
            
    async def broadcast_to_symbol(self, message: str, symbol: str):
        """Broadcast message tới tất cả clients đang theo dõi symbol"""
        if symbol in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_text(message)
                    
                    # Update stats
                    if connection in self.subscription_settings:
                        self.subscription_settings[connection]['message_count'] += 1
                        
                except Exception as e:
                    logger.error(f"Error broadcasting to {symbol}: {e}")
                    disconnected.add(connection)
            
            # Xóa những connection bị lỗi
            for connection in disconnected:
                self.disconnect(connection)

# Global enhanced connection manager
enhanced_manager = EnhancedConnectionManager()

async def get_comprehensive_market_data(symbol: str, session):
    """Lấy dữ liệu market comprehensive từ Cassandra"""
    try:
        today = date.today()
        
        # 1. OHLC data mới nhất
        ohlc_query = """
        SELECT symbol, window_start, open_price, high_price, low_price, close_price, volume, vwap, trade_count
        FROM ohlc_data 
        WHERE symbol = ? AND window_date = ?
        ORDER BY window_start DESC
        LIMIT 2
        """
        
        ohlc_result = session.execute(ohlc_query, [symbol.upper(), today])
        ohlc_rows = list(ohlc_result)
        
        if not ohlc_rows:
            return None
            
        current_ohlc = ohlc_rows[0]
        previous_ohlc = ohlc_rows[1] if len(ohlc_rows) > 1 else current_ohlc
        
        # 2. Technical indicators mới nhất
        indicators_query = """
        SELECT sma_20, ema_12, rsi_14, macd_line, bb_middle
        FROM technical_indicators 
        WHERE symbol = ? AND window_date = ?
        ORDER BY window_start DESC
        LIMIT 1
        """
        
        indicators_result = session.execute(indicators_query, [symbol.upper(), today])
        indicators_row = indicators_result.one() if indicators_result else None
        
        # 3. Recent trades count (last 5 minutes)
        recent_time = datetime.now() - timedelta(minutes=5)
        
        trades_query = """
        SELECT COUNT(*) as trade_count
        FROM trades 
        WHERE symbol = ? AND trade_timestamp >= ?
        ALLOW FILTERING
        """
        
        try:
            trades_result = session.execute(trades_query, [symbol.upper(), recent_time])
            recent_trades = trades_result.one().trade_count if trades_result else 0
        except:
            recent_trades = 0  # Fallback if query fails
        
        # 4. Tính toán price change
        current_price = float(current_ohlc.close_price)
        previous_price = float(previous_ohlc.close_price)
        price_change = current_price - previous_price
        price_change_percent = (price_change / previous_price) * 100 if previous_price != 0 else 0
        
        # 5. Tạo comprehensive response
        market_data = {
            "symbol": symbol.upper(),
            "timestamp": current_ohlc.window_start.isoformat(),
            "server_time": datetime.now().isoformat(),
            
            # Current price info
            "price": current_price,
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            
            # OHLC data
            "ohlc": {
                "open": float(current_ohlc.open_price),
                "high": float(current_ohlc.high_price),
                "low": float(current_ohlc.low_price),
                "close": current_price,
                "volume": current_ohlc.volume,
                "vwap": float(current_ohlc.vwap),
                "trade_count": current_ohlc.trade_count
            },
            
            # Market activity
            "activity": {
                "recent_trades_5min": recent_trades,
                "volume_24h": current_ohlc.volume,  # Using current window volume as proxy
                "is_active": recent_trades > 0
            }
        }
        
        # Add technical indicators if available
        if indicators_row:
            market_data["indicators"] = {
                "sma_20": float(indicators_row.sma_20) if indicators_row.sma_20 else None,
                "ema_12": float(indicators_row.ema_12) if indicators_row.ema_12 else None,
                "rsi_14": float(indicators_row.rsi_14) if indicators_row.rsi_14 else None,
                "macd_line": float(indicators_row.macd_line) if indicators_row.macd_line else None,
                "bb_middle": float(indicators_row.bb_middle) if indicators_row.bb_middle else None
            }
            
            # Add trading signals based on indicators
            signals = []
            if indicators_row.rsi_14:
                rsi = float(indicators_row.rsi_14)
                if rsi < 30:
                    signals.append({"type": "BUY", "reason": "RSI Oversold", "strength": "STRONG" if rsi < 25 else "MODERATE"})
                elif rsi > 70:
                    signals.append({"type": "SELL", "reason": "RSI Overbought", "strength": "STRONG" if rsi > 75 else "MODERATE"})
            
            if indicators_row.macd_line:
                macd = float(indicators_row.macd_line)
                if macd > 0:
                    signals.append({"type": "BUY", "reason": "MACD Bullish", "strength": "MODERATE"})
                else:
                    signals.append({"type": "SELL", "reason": "MACD Bearish", "strength": "MODERATE"})
            
            market_data["signals"] = signals
        
        return market_data
        
    except Exception as e:
        logger.error(f"Error getting comprehensive market data for {symbol}: {e}")
        return None

async def enhanced_websocket_endpoint(websocket: WebSocket, symbol: str, update_interval: int = 2):
    """Enhanced WebSocket với customizable update interval"""
    session = None
    try:
        # Get Cassandra session
        from app.core.cassandra import cassandra_manager
        session = cassandra_manager.get_session()
        
        # Connect WebSocket
        await enhanced_manager.connect(websocket, symbol.upper(), update_interval)
        
        # Send welcome message với configuration
        welcome_msg = {
            "type": "connection",
            "symbol": symbol.upper(),
            "message": f"Connected to enhanced {symbol.upper()} stream",
            "config": {
                "update_interval": update_interval,
                "features": ["OHLC", "Technical Indicators", "Trading Signals", "Price Changes"]
            },
            "timestamp": datetime.now().isoformat()
        }
        await enhanced_manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # Main streaming loop với dynamic interval
        last_data_hash = None
        
        while True:
            current_time = time.time()
            
            # Check if it's time to send update based on custom interval
            settings = enhanced_manager.subscription_settings.get(websocket)
            if settings and (current_time - settings['last_update']) >= settings['update_interval']:
                
                # Get comprehensive market data
                market_data = await get_comprehensive_market_data(symbol, session)
                
                if market_data:
                    # Check if data actually changed (avoid sending duplicate data)
                    data_hash = hash(json.dumps(market_data, sort_keys=True))
                    
                    if data_hash != last_data_hash:
                        # Create message
                        message = {
                            "type": "market_update",
                            "data": market_data,
                            "meta": {
                                "message_id": settings['message_count'] + 1,
                                "update_interval": settings['update_interval'],
                                "data_changed": True
                            }
                        }
                        
                        # Send update
                        await enhanced_manager.send_personal_message(json.dumps(message), websocket)
                        last_data_hash = data_hash
                        settings['last_update'] = current_time
                    
                    else:
                        # Send light heartbeat indicating no change
                        heartbeat = {
                            "type": "heartbeat",
                            "symbol": symbol.upper(),
                            "timestamp": datetime.now().isoformat(),
                            "message": "No data change",
                            "next_update_in": settings['update_interval']
                        }
                        await enhanced_manager.send_personal_message(json.dumps(heartbeat), websocket)
                        settings['last_update'] = current_time
                        
                else:
                    # Send no-data heartbeat
                    heartbeat = {
                        "type": "heartbeat",
                        "symbol": symbol.upper(),
                        "timestamp": datetime.now().isoformat(),
                        "message": "No market data available"
                    }
                    await enhanced_manager.send_personal_message(json.dumps(heartbeat), websocket)
                    settings['last_update'] = current_time
            
            # Sleep for a short time to avoid busy waiting
            await asyncio.sleep(0.5)  # Check every 500ms but only send based on interval
            
    except WebSocketDisconnect:
        enhanced_manager.disconnect(websocket)
        logger.info(f"Enhanced WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"Enhanced WebSocket error for {symbol}: {e}")
        enhanced_manager.disconnect(websocket) 