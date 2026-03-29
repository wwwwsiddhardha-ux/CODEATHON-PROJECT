"""
Market router.
Exposes endpoints to fetch real-time market demand data for skills.
Delegates to scraping_service (Bright Data).
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.scraping_service import get_market_data

router = APIRouter()


class MarketRequest(BaseModel):
    skills: List[str]


@router.post("/demand")
async def get_demand(request: MarketRequest):
    """
    Fetch market demand signals for a list of skills.
    Returns demand_score, avg_salary, job_count per skill.
    """
    data = await get_market_data(request.skills)
    return {"market_data": data}
