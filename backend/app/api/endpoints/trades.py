from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.core.cassandra import get_cassandra_session
from app.models.schemas import TradeData, APIResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/trades/{symbol}", response_model=APIResponse)
async def get_trades(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    session=Depends(get_cassandra_session)
):
    """
    Lấy dữ liệu giao dịch thô cho một symbol
    
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
            start_date = end_date - timedelta(days=1)  # 1 ngày gần nhất
        
        # Build CQL query
        query = """
        SELECT symbol, trade_date, trade_timestamp, price, volume, trade_conditions, ingest_timestamp
        FROM trades 
        WHERE symbol = ? AND trade_date >= ? AND trade_date <= ?
        ORDER BY trade_timestamp DESC
        LIMIT ?
        """
        
        # Execute query
        result = session.execute(query, [symbol.upper(), start_date, end_date, limit])
        
        # Convert to Pydantic models
        trade_data = []
        for row in result:
            trade_data.append(TradeData(
                symbol=row.symbol,
                trade_date=row.trade_date,
                trade_timestamp=row.trade_timestamp,
                price=float(row.price),
                volume=row.volume,
                trade_conditions=row.trade_conditions if row.trade_conditions else [],
                ingest_timestamp=row.ingest_timestamp
            ))
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(trade_data)} trade records for {symbol}",
            data={
                "symbol": symbol.upper(),
                "start_date": str(start_date),
                "end_date": str(end_date),
                "records": [item.dict() for item in trade_data]
            },
            total_records=len(trade_data)
        )
        
    except Exception as e:
        logger.error(f"Error getting trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/trades/{symbol}/latest", response_model=APIResponse)
async def get_latest_trades(
    symbol: str,
    count: int = Query(10, le=100, description="Number of latest trades"),
    session=Depends(get_cassandra_session)
):
    """
    Lấy giao dịch mới nhất cho một symbol
    """
    try:
        query = """
        SELECT symbol, trade_date, trade_timestamp, price, volume, trade_conditions, ingest_timestamp
        FROM trades 
        WHERE symbol = ? AND trade_date = ?
        ORDER BY trade_timestamp DESC
        LIMIT ?
        """
        
        today = date.today()
        result = session.execute(query, [symbol.upper(), today, count])
        
        trades = []
        for row in result:
            trades.append(TradeData(
                symbol=row.symbol,
                trade_date=row.trade_date,
                trade_timestamp=row.trade_timestamp,
                price=float(row.price),
                volume=row.volume,
                trade_conditions=row.trade_conditions if row.trade_conditions else [],
                ingest_timestamp=row.ingest_timestamp
            ))
        
        if not trades:
            raise HTTPException(status_code=404, detail=f"No recent trades found for {symbol}")
        
        return APIResponse(
            success=True,
            message=f"Latest {len(trades)} trades for {symbol}",
            data={
                "symbol": symbol.upper(),
                "trades": [item.dict() for item in trades]
            },
            total_records=len(trades)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 