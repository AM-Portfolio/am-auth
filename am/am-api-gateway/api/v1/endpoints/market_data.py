"""
Market Data API endpoints
Placeholder - To be implemented
"""

from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user, CurrentUser

router = APIRouter()

@router.get("/market-data/stocks/{symbol}")
async def get_stock_data(
    symbol: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get stock market data
    
    ✅ PUBLIC ENDPOINT - Coming soon
    """
    return {
        "status": "not_implemented",
        "message": f"Market data for {symbol} coming soon",
        "user": current_user.user_id
    }

@router.get("/market-data/quotes")
async def get_quotes(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get market quotes
    
    ✅ PUBLIC ENDPOINT - Coming soon
    """
    return {
        "status": "not_implemented",
        "message": "Market quotes endpoint coming soon"
    }
