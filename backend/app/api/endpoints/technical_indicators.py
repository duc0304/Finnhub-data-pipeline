from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.core.cassandra import get_cassandra_session
from app.models.schemas import TechnicalIndicators, APIResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/indicators/{symbol}", response_model=APIResponse)
async def get_technical_indicators(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    session=Depends(get_cassandra_session)
):
    """
    Lấy chỉ báo kỹ thuật cho một symbol
    
    - **symbol**: Mã cổ phiếu (VD: AAPL, MSFT)
    - **start_date**: Ngày bắt đầu (tùy chọn)
    - **end_date**: Ngày kết thúc (tùy chọn)
    - **limit**: Số lượng records tối đa
    
    **Các chỉ báo kỹ thuật:**
    - SMA 20: Simple Moving Average 20 periods (Hướng trend)
    - EMA 12: Exponential Moving Average 12 periods (MA nhanh)
    - RSI 14: Relative Strength Index 14 periods (Quá mua/quá bán)
    - MACD Line: MACD Line (EMA12 - EMA26) (Momentum)
    - BB Middle: Bollinger Band Middle = SMA20 (Hỗ trợ/kháng cự)
    """
    try:
        # Default dates nếu không có
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=7)  # 7 ngày gần nhất
        
        # Build CQL query
        query = """
        SELECT symbol, window_date, window_start, sma_20, ema_12, rsi_14, macd_line, bb_middle
        FROM technical_indicators 
        WHERE symbol = ? AND window_date >= ? AND window_date <= ?
        ORDER BY window_start DESC
        LIMIT ?
        """
        
        # Execute query
        result = session.execute(query, [symbol.upper(), start_date, end_date, limit])
        
        # Convert to Pydantic models
        indicator_data = []
        for row in result:
            indicator_data.append(TechnicalIndicators(
                symbol=row.symbol,
                window_date=row.window_date,
                window_start=row.window_start,
                sma_20=float(row.sma_20) if row.sma_20 is not None else None,
                ema_12=float(row.ema_12) if row.ema_12 is not None else None,
                rsi_14=float(row.rsi_14) if row.rsi_14 is not None else None,
                macd_line=float(row.macd_line) if row.macd_line is not None else None,
                bb_middle=float(row.bb_middle) if row.bb_middle is not None else None
            ))
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(indicator_data)} technical indicator records for {symbol}",
            data={
                "symbol": symbol.upper(),
                "start_date": str(start_date),
                "end_date": str(end_date),
                "records": [item.dict() for item in indicator_data]
            },
            total_records=len(indicator_data)
        )
        
    except Exception as e:
        logger.error(f"Error getting technical indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/indicators/{symbol}/latest", response_model=APIResponse)
async def get_latest_indicators(
    symbol: str,
    session=Depends(get_cassandra_session)
):
    """
    Lấy chỉ báo kỹ thuật mới nhất cho một symbol
    """
    try:
        query = """
        SELECT symbol, window_date, window_start, sma_20, ema_12, rsi_14, macd_line, bb_middle
        FROM technical_indicators 
        WHERE symbol = ? AND window_date = ?
        ORDER BY window_start DESC
        LIMIT 1
        """
        
        today = date.today()
        result = session.execute(query, [symbol.upper(), today])
        
        row = result.one() if result else None
        if not row:
            raise HTTPException(status_code=404, detail=f"No technical indicators found for {symbol}")
        
        latest_indicators = TechnicalIndicators(
            symbol=row.symbol,
            window_date=row.window_date,
            window_start=row.window_start,
            sma_20=float(row.sma_20) if row.sma_20 is not None else None,
            ema_12=float(row.ema_12) if row.ema_12 is not None else None,
            rsi_14=float(row.rsi_14) if row.rsi_14 is not None else None,
            macd_line=float(row.macd_line) if row.macd_line is not None else None,
            bb_middle=float(row.bb_middle) if row.bb_middle is not None else None
        )
        
        return APIResponse(
            success=True,
            message=f"Latest technical indicators for {symbol}",
            data=latest_indicators.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/indicators/{symbol}/signals", response_model=APIResponse)
async def get_trading_signals(
    symbol: str,
    lookback_hours: int = Query(24, description="Hours to look back for signal analysis"),
    session=Depends(get_cassandra_session)
):
    """
    Phân tích tín hiệu giao dịch dựa trên technical indicators
    
    **Tín hiệu mua/bán:**
    - RSI < 30: Oversold (tín hiệu mua)
    - RSI > 70: Overbought (tín hiệu bán)
    - MACD Line > 0: Bullish momentum
    - MACD Line < 0: Bearish momentum
    - Price vs SMA20: Trend direction
    """
    try:
        # Tính toán khoảng thời gian
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        query = """
        SELECT symbol, window_start, sma_20, ema_12, rsi_14, macd_line, bb_middle
        FROM technical_indicators 
        WHERE symbol = ? AND window_start >= ? AND window_start <= ?
        ORDER BY window_start DESC
        LIMIT 50
        """
        
        result = session.execute(query, [symbol.upper(), start_time, end_time])
        rows = list(result)
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"No indicator data found for {symbol}")
        
        # Phân tích tín hiệu từ indicator mới nhất
        latest = rows[0]
        signals = []
        
        # RSI signals
        if latest.rsi_14 is not None:
            if latest.rsi_14 < 30:
                signals.append({
                    "type": "BUY",
                    "indicator": "RSI",
                    "value": float(latest.rsi_14),
                    "message": f"RSI {latest.rsi_14:.2f} - Oversold condition",
                    "strength": "STRONG" if latest.rsi_14 < 25 else "MODERATE"
                })
            elif latest.rsi_14 > 70:
                signals.append({
                    "type": "SELL",
                    "indicator": "RSI",
                    "value": float(latest.rsi_14),
                    "message": f"RSI {latest.rsi_14:.2f} - Overbought condition",
                    "strength": "STRONG" if latest.rsi_14 > 75 else "MODERATE"
                })
        
        # MACD signals
        if latest.macd_line is not None:
            if latest.macd_line > 0:
                signals.append({
                    "type": "BUY",
                    "indicator": "MACD",
                    "value": float(latest.macd_line),
                    "message": f"MACD {latest.macd_line:.4f} - Bullish momentum",
                    "strength": "MODERATE"
                })
            else:
                signals.append({
                    "type": "SELL",
                    "indicator": "MACD",
                    "value": float(latest.macd_line),
                    "message": f"MACD {latest.macd_line:.4f} - Bearish momentum",
                    "strength": "MODERATE"
                })
        
        # Tính toán tổng quan
        buy_signals = len([s for s in signals if s["type"] == "BUY"])
        sell_signals = len([s for s in signals if s["type"] == "SELL"])
        
        overall_signal = "NEUTRAL"
        if buy_signals > sell_signals:
            overall_signal = "BUY"
        elif sell_signals > buy_signals:
            overall_signal = "SELL"
        
        return APIResponse(
            success=True,
            message=f"Trading signals analysis for {symbol}",
            data={
                "symbol": symbol.upper(),
                "timestamp": str(latest.window_start),
                "overall_signal": overall_signal,
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "signals": signals,
                "indicators": {
                    "sma_20": float(latest.sma_20) if latest.sma_20 else None,
                    "ema_12": float(latest.ema_12) if latest.ema_12 else None,
                    "rsi_14": float(latest.rsi_14) if latest.rsi_14 else None,
                    "macd_line": float(latest.macd_line) if latest.macd_line else None,
                    "bb_middle": float(latest.bb_middle) if latest.bb_middle else None
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trading signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}") 