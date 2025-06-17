from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Import core modules
from app.core.cassandra import init_cassandra, close_cassandra

# Import API endpoints
from app.api.endpoints import ohlc, technical_indicators, trades

# Import WebSocket
from app.api.websocket.realtime import websocket_endpoint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events cho FastAPI app"""
    # Startup
    logger.info("Starting FastAPI Financial Data API")
    
    # Initialize Cassandra connection
    if not init_cassandra():
        logger.error("Failed to initialize Cassandra connection")
        raise Exception("Cannot connect to Cassandra")
    
    logger.info("Cassandra connection initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI Financial Data API")
    close_cassandra()
    logger.info("Cassandra connection closed")

# Create FastAPI app
app = FastAPI(
    title="Financial Data API",
    description="FastAPI Backend cho Hệ thống Dữ liệu Tài chính",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ohlc.router, prefix="/api/v1", tags=["OHLC Data"])
app.include_router(technical_indicators.router, prefix="/api/v1", tags=["Technical Indicators"])
app.include_router(trades.router, prefix="/api/v1", tags=["Trades"])

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 Financial Data API v1.0.0",
        "description": "FastAPI backend cho hệ thống dữ liệu tài chính",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "websocket": "/ws/{symbol}"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        from app.core.cassandra import cassandra_manager
        session = cassandra_manager.get_session()
        
        # Test Cassandra connection
        result = session.execute("SELECT key FROM system.local LIMIT 1")
        cassandra_status = "connected" if result else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "cassandra": cassandra_status,
                "api": "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.websocket("/ws/{symbol}")
async def websocket_realtime(websocket: WebSocket, symbol: str):
    """WebSocket endpoint cho real-time price streaming"""
    await websocket_endpoint(websocket, symbol)

@app.websocket("/ws/enhanced/{symbol}")
async def websocket_enhanced(
    websocket: WebSocket, 
    symbol: str,
    update_interval: int = 2
):
    """Enhanced WebSocket với customizable update interval (1-30 seconds)"""
    from app.api.websocket.enhanced_realtime import enhanced_websocket_endpoint
    await enhanced_websocket_endpoint(websocket, symbol, update_interval)

@app.websocket("/ws/live/{symbol}")
async def websocket_kafka_realtime(websocket: WebSocket, symbol: str):
    """
    TRUE Real-time WebSocket - Listen trực tiếp từ Kafka stream
    
    ⚡ ZERO DELAY - Nhận data ngay khi có trade mới
    🚀 KAFKA DIRECT - Không query database
    📡 INSTANT PUSH - Millisecond latency
    """
    from app.api.websocket.kafka_realtime import kafka_realtime_websocket
    await kafka_realtime_websocket(websocket, symbol)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 