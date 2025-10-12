"""
Portfolio API endpoints
Placeholder - To be implemented
"""

from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user, CurrentUser

router = APIRouter()

@router.get("/portfolio")
async def get_portfolio(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get user portfolio
    
    ✅ PUBLIC ENDPOINT - Coming soon
    """
    return {
        "status": "not_implemented",
        "message": "Portfolio endpoint coming soon",
        "user": current_user.user_id
    }

@router.post("/portfolio/transaction")
async def create_transaction(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create portfolio transaction
    
    ✅ PUBLIC ENDPOINT - Coming soon
    """
    return {
        "status": "not_implemented",
        "message": "Transaction endpoint coming soon"
    }
