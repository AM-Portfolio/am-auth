"""
Trades API endpoints
Placeholder - To be implemented
"""

from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user, CurrentUser

router = APIRouter()

@router.get("/trades")
async def get_trades(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get user trades
    
    ✅ PUBLIC ENDPOINT - Coming soon
    """
    return {
        "status": "not_implemented",
        "message": "Trades endpoint coming soon",
        "user": current_user.user_id
    }

@router.post("/trades/execute")
async def execute_trade(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Execute trade
    
    ✅ PUBLIC ENDPOINT - Coming soon
    """
    return {
        "status": "not_implemented",
        "message": "Trade execution endpoint coming soon"
    }
