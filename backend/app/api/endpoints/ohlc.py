from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.core.cassandra import get_cassandra_session
from app.models.schemas import OHLCData, APIResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/ohlc/{symbol}", response_model=APIResponse)
async def get_ohlc_data(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    session=Depends(get_cassandra_session)
):
    """
    Lấy dữ liệu OHLC (candlestick) cho một symbol
    
    - **symbol**: Mã cổ phiếu (VD: AAPL, MSFT)
    - **start_date**: Ngày bắt đầu (tùy chọn)
    - **end_date**: Ngày kết thúc (tùy chọn)
    - **limit**: Số lượng records tối đa
    """
    try:
        # Default dates nếu không có
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=7)  # 7 ngày gần nhất
        
        # Build CQL query
        query = """
        SELECT symbol, window_date, window_start, open_price, high_price, 
               low_price, close_price, volume, trade_count, vwap
        FROM ohlc_data 
        WHERE symbol = ? AND window_date >= ? AND window_date <= ?
        ORDER BY window_start DESC
        LIMIT ?
        """
        
        # Execute query
        result = session.execute(query, [symbol.upper(), start_date, end_date, limit])
        
        # Convert to Pydantic models
        ohlc_data = []
        for row in result:
            ohlc_data.append(OHLCData(
                symbol=row.symbol,
                window_date=row.window_date,
                window_start=row.window_start,
                open_price=float(row.open_price),
                high_price=float(row.high_price),
                low_price=float(row.low_price),
                close_price=float(row.close_price),
                volume=row.volume,
                trade_count=row.trade_count,
                vwap=float(row.vwap)
            ))
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(ohlc_data)} OHLC records for {symbol}",
            data={
                "symbol": symbol.upper(),
                "start_date": str(start_date),
                "end_date": str(end_date),
                "records": [item.dict() for item in ohlc_data]
            },
            total_records=len(ohlc_data)
        )
        
    except Exception as e:
        logger.error(f"Error getting OHLC data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/ohlc/{symbol}/latest", response_model=APIResponse)
async def get_latest_ohlc(
    symbol: str,
    session=Depends(get_cassandra_session)
):
    """
    Lấy OHLC data mới nhất cho một symbol
    """
    try:
        query = """
        SELECT symbol, window_date, window_start, open_price, high_price, 
               low_price, close_price, volume, trade_count, vwap
        FROM ohlc_data 
        WHERE symbol = ? AND window_date = ?
        ORDER BY window_start DESC
        LIMIT 1
        """
        
        today = date.today()
        result = session.execute(query, [symbol.upper(), today])
        
        row = result.one() if result else None
        if not row:
            raise HTTPException(status_code=404, detail=f"No OHLC data found for {symbol}")
        
        latest_ohlc = OHLCData(
            symbol=row.symbol,
            window_date=row.window_date,
            window_start=row.window_start,
            open_price=float(row.open_price),
            high_price=float(row.high_price),
            low_price=float(row.low_price),
            close_price=float(row.close_price),
            volume=row.volume,
            trade_count=row.trade_count,
            vwap=float(row.vwap)
        )
        
        return APIResponse(
            success=True,
            message=f"Latest OHLC data for {symbol}",
            data=latest_ohlc.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest OHLC for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/ohlc/{symbol}/timeframe/{timeframe}", response_model=APIResponse)
async def get_ohlc_by_timeframe(
    symbol: str,
    timeframe: str = Query(..., description="Timeframe: 1m, 5m, 15m, 1h"),
    hours_back: int = Query(24, description="Hours to look back"),
    session=Depends(get_cassandra_session)
):
    """
    Lấy OHLC data theo timeframe cụ thể
    
    Note: Hiện tại system chỉ store 1m data, API này sẽ aggregate để tạo timeframe khác
    """
    try:
        # Tính toán khoảng thời gian
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Base query cho 1-minute data
        query = """
        SELECT symbol, window_date, window_start, open_price, high_price, 
               low_price, close_price, volume, trade_count, vwap
        FROM ohlc_data 
        WHERE symbol = ? AND window_start >= ? AND window_start <= ?
        ORDER BY window_start ASC
        """
        
        result = session.execute(query, [symbol.upper(), start_time, end_time])
        
        # TODO: Implement timeframe aggregation logic
        # Ví dụ: 5m = aggregate 5 records of 1m data
        raw_data = list(result)
        
        if not raw_data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Trả về raw 1m data (có thể implement aggregation sau)
        ohlc_data = []
        for row in raw_data:
            ohlc_data.append(OHLCData(
                symbol=row.symbol,
                window_date=row.window_date,
                window_start=row.window_start,
                open_price=float(row.open_price),
                high_price=float(row.high_price),
                low_price=float(row.low_price),
                close_price=float(row.close_price),
                volume=row.volume,
                trade_count=row.trade_count,
                vwap=float(row.vwap)
            ))
        
        return APIResponse(
            success=True,
            message=f"OHLC data for {symbol} ({timeframe} timeframe)",
            data={
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "start_time": str(start_time),
                "end_time": str(end_time),
                "records": [item.dict() for item in ohlc_data]
            },
            total_records=len(ohlc_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OHLC timeframe data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 