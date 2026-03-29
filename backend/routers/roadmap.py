"""
Roadmap router.
Generates a weekly learning plan based on user profile + AI recommendations.
"""
from fastapi import APIRouter
from models.schemas import UserProfile, RoadmapResponse, WeeklyPlan
from services.scraping_service import get_market_data
from services.scoring_engine import score_skills
from services.ai_service import get_skill_recommendations

router = APIRouter()


@router.post("/", response_model=RoadmapResponse)
async def generate_roadmap(profile: UserProfile):
    """
    Generate a weekly learning roadmap.
    Returns hour-by-hour skill allocation for the week.
    """
    skill_names = [s.name for s in profile.skills]
    user_skills = [s.model_dump() for s in profile.skills]

    market_data = await get_market_data(skill_names)
    scored = score_skills(user_skills, market_data)

    ai_result = await get_skill_recommendations(
        career_goal=profile.career_goal,
        scored_skills=scored,
        hours_per_week=profile.hours_per_week,
    )

    weekly_plan = [
        WeeklyPlan(
            skill=item["skill"],
            hours=item["hours"],
            reason=item["reason"],
        )
        for item in ai_result.get("weekly_plan", [])
    ]

    return RoadmapResponse(
        weekly_plan=weekly_plan,
        total_hours=sum(p.hours for p in weekly_plan),
    )
