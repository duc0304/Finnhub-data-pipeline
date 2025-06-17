from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.core.cassandra import get_cassandra_session
from datetime import datetime, date
import json
import asyncio
import logging
from typing import Set, Dict

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Quản lý WebSocket connections"""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # symbol -> set of websockets
        
    async def connect(self, websocket: WebSocket, symbol: str):
        """Kết nối một WebSocket cho symbol cụ thể"""
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        logger.info(f"Client connected to {symbol} stream. Total connections: {len(self.active_connections[symbol])}")
        
    def disconnect(self, websocket: WebSocket, symbol: str):
        """Ngắt kết nối WebSocket"""
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            if len(self.active_connections[symbol]) == 0:
                del self.active_connections[symbol]
        logger.info(f"Client disconnected from {symbol} stream")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Gửi message tới một WebSocket cụ thể"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            
    async def broadcast_to_symbol(self, message: str, symbol: str):
        """Broadcast message tới tất cả clients đang theo dõi symbol"""
        if symbol in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {symbol}: {e}")
                    disconnected.add(connection)
            
            # Xóa những connection bị lỗi
            for connection in disconnected:
                self.active_connections[symbol].discard(connection)

# Global connection manager
manager = ConnectionManager()

async def get_latest_price_data(symbol: str, session):
    """Lấy dữ liệu price mới nhất từ Cassandra"""
    try:
        # Lấy OHLC data mới nhất
        ohlc_query = """
        SELECT symbol, window_start, open_price, high_price, low_price, close_price, volume, vwap
        FROM ohlc_data 
        WHERE symbol = ? AND window_date = ?
        ORDER BY window_start DESC
        LIMIT 1
        """
        
        today = date.today()
        ohlc_result = session.execute(ohlc_query, [symbol.upper(), today])
        ohlc_row = ohlc_result.one() if ohlc_result else None
        
        # Lấy technical indicators mới nhất
        indicators_query = """
        SELECT sma_20, ema_12, rsi_14, macd_line, bb_middle
        FROM technical_indicators 
        WHERE symbol = ? AND window_date = ?
        ORDER BY window_start DESC
        LIMIT 1
        """
        
        indicators_result = session.execute(indicators_query, [symbol.upper(), today])
        indicators_row = indicators_result.one() if indicators_result else None
        
        # Tạo response data
        if ohlc_row:
            price_data = {
                "symbol": symbol.upper(),
                "timestamp": ohlc_row.window_start.isoformat(),
                "price": float(ohlc_row.close_price),
                "open": float(ohlc_row.open_price),
                "high": float(ohlc_row.high_price),
                "low": float(ohlc_row.low_price),
                "volume": ohlc_row.volume,
                "vwap": float(ohlc_row.vwap)
            }
            
            # Thêm technical indicators nếu có
            if indicators_row:
                price_data["indicators"] = {
                    "sma_20": float(indicators_row.sma_20) if indicators_row.sma_20 else None,
                    "ema_12": float(indicators_row.ema_12) if indicators_row.ema_12 else None,
                    "rsi_14": float(indicators_row.rsi_14) if indicators_row.rsi_14 else None,
                    "macd_line": float(indicators_row.macd_line) if indicators_row.macd_line 
                    else None
                }
            
            return price_data
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting latest price data for {symbol}: {e}")
        return None

async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint cho real-time price streaming"""
    session = None
    try:
        # Get Cassandra session
        from app.core.cassandra import cassandra_manager
        session = cassandra_manager.get_session()
        
        # Connect WebSocket
        await manager.connect(websocket, symbol.upper())
        
        # Gửi thông báo welcome
        welcome_msg = {
            "type": "connection",
            "symbol": symbol.upper(),
            "message": f"Connected to {symbol.upper()} real-time stream",
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # Stream data loop
        while True:
            # Lấy data mới nhất
            price_data = await get_latest_price_data(symbol, session)
            
            if price_data:
                # Tạo message
                message = {
                    "type": "price_update",
                    "data": price_data,
                    "server_timestamp": datetime.now().isoformat()
                }
                
                # Gửi tới client
                await manager.send_personal_message(json.dumps(message), websocket)
            else:
                # Gửi heartbeat nếu không có data
                heartbeat = {
                    "type": "heartbeat",
                    "symbol": symbol.upper(),
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(heartbeat), websocket)
            
            # Đợi 5 giây trước khi cập nhật tiếp
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol.upper())
        logger.info(f"WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
        manager.disconnect(websocket, symbol.upper())

async def broadcast_price_update(symbol: str, price_data: dict):
    """Broadcast price update tới tất cả connected clients cho symbol"""
    message = {
        "type": "price_update",
        "data": price_data,
        "server_timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_symbol(json.dumps(message), symbol.upper()) 