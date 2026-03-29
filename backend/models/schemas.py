"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel
from typing import List, Optional

class Skill(BaseModel):
    name: str
    proficiency: int  # 1-10

class UserProfile(BaseModel):
    name: str
    skills: List[Skill]
    interests: List[str]
    career_goal: str
    hours_per_week: int

class ScoredSkill(BaseModel):
    name: str
    proficiency: int
    demand_score: float
    growth_potential: float
    learning_difficulty: float
    risk_score: float
    reward_score: float
    allocation_percent: float

class RecommendationResponse(BaseModel):
    invest_more: List[str]
    reduce_focus: List[str]
    scored_skills: List[ScoredSkill]
    summary: str

class WeeklyPlan(BaseModel):
    skill: str
    hours: float
    reason: str

class RoadmapResponse(BaseModel):
    weekly_plan: List[WeeklyPlan]
    total_hours: float
