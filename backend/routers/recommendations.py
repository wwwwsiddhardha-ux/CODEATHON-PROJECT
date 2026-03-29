"""
Recommendations router.
Orchestrates the full pipeline:
  1. Fetch market data (Bright Data)
  2. Score skills (scoring_engine)
  3. Generate AI recommendations (Featherless AI)
"""
from fastapi import APIRouter
from models.schemas import UserProfile, RecommendationResponse
from services.scraping_service import get_market_data
from services.scoring_engine import score_skills
from services.ai_service import get_skill_recommendations

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(profile: UserProfile):
    """
    Full pipeline endpoint.
    Accepts a UserProfile and returns a complete skill investment recommendation.
    """
    skill_names = [s.name for s in profile.skills]
    user_skills = [s.model_dump() for s in profile.skills]

    # Step 1: Get market demand data
    market_data = await get_market_data(skill_names)

    # Step 2: Score each skill using the scoring engine
    scored = score_skills(user_skills, market_data)

    # Step 3: Get AI-generated recommendations from Featherless AI
    ai_result = await get_skill_recommendations(
        career_goal=profile.career_goal,
        scored_skills=scored,
        hours_per_week=profile.hours_per_week,
    )

    return RecommendationResponse(
        invest_more=ai_result.get("invest_more", []),
        reduce_focus=ai_result.get("reduce_focus", []),
        scored_skills=scored,
        summary=ai_result.get("summary", ""),
    )
