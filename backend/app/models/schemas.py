from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

class TradeData(BaseModel):
    """Model cho dữ liệu giao dịch"""
    symbol: str
    trade_date: date
    trade_timestamp: datetime
    price: float
    volume: int
    trade_conditions: Optional[List[str]] = []
    ingest_timestamp: datetime

class OHLCData(BaseModel):
    """Model cho dữ liệu OHLC"""
    symbol: str
    window_date: date
    window_start: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    trade_count: int
    vwap: float = Field(description="Volume Weighted Average Price")

class TechnicalIndicators(BaseModel):
    """Model cho chỉ báo kỹ thuật"""
    symbol: str
    window_date: date
    window_start: datetime
    sma_20: Optional[float] = Field(description="Simple Moving Average 20 periods")
    ema_12: Optional[float] = Field(description="Exponential Moving Average 12 periods")
    rsi_14: Optional[float] = Field(description="Relative Strength Index 14 periods")
    macd_line: Optional[float] = Field(description="MACD Line (EMA12 - EMA26)")
    bb_middle: Optional[float] = Field(description="Bollinger Band Middle (SMA20)")

class AggregateData(BaseModel):
    """Model cho dữ liệu tổng hợp"""
    symbol: str
    window_date: date
    window_start: datetime
    trade_count: int
    avg_price: float
    total_volume: int
    min_price: float
    max_price: float

class MarketSummary(BaseModel):
    """Model cho tổng quan thị trường"""
    symbol: str
    latest_price: float
    price_change: float
    price_change_percent: float
    volume_24h: int
    high_24h: float
    low_24h: float
    
class StockAnalysis(BaseModel):
    """Model kết hợp OHLC + Technical Indicators"""
    symbol: str
    timestamp: datetime
    ohlc: OHLCData
    indicators: TechnicalIndicators
    
class APIResponse(BaseModel):
    """Model chung cho API response"""
    success: bool = True
    message: str = "Success"
    data: Optional[dict] = None
    total_records: Optional[int] = None

class TimeSeriesQuery(BaseModel):
    """Model cho query parameters"""
    symbol: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = Field(default=100, le=1000)
    timeframe: Optional[str] = Field(default="1m", description="1m, 5m, 15m, 1h, 1d")

class RealtimePrice(BaseModel):
    """Model cho real-time price updates"""
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    change: float
    change_percent: float 