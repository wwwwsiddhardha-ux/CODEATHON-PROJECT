"""
Scoring Engine.
Computes Risk Score, Reward Score, and portfolio allocation % for each skill
based on user proficiency + market demand signals.
"""
from typing import List, Dict

# Static learning difficulty map (1–10). Higher = harder to learn.
DIFFICULTY_MAP = {
    "python": 3, "javascript": 3, "typescript": 4, "react": 4,
    "sql": 3, "java": 5, "go": 5, "rust": 8, "c++": 8,
    "docker": 4, "kubernetes": 7, "terraform": 6, "aws": 5,
    "machine learning": 7, "deep learning": 8, "fastapi": 3,
    "graphql": 5, "redis": 4, "kafka": 7, "spark": 7,
}
DEFAULT_DIFFICULTY = 5


def get_difficulty(skill_name: str) -> float:
    """Return learning difficulty score (1–10) for a skill."""
    return DIFFICULTY_MAP.get(skill_name.lower(), DEFAULT_DIFFICULTY)


def compute_growth_potential(proficiency: int, demand_score: float) -> float:
    """
    Growth potential = how much room to grow × market pull.
    Low proficiency + high demand = high growth potential.
    """
    room_to_grow = (10 - proficiency) / 10  # 0.0 – 1.0
    return round(room_to_grow * demand_score, 2)


def compute_risk_score(difficulty: float, demand_score: float) -> float:
    """
    Risk = learning difficulty + competition (inverse of demand).
    High difficulty + low demand = high risk.
    """
    competition = 10 - demand_score  # high demand = low competition risk
    return round((difficulty + competition) / 2, 2)


def compute_reward_score(demand_score: float, avg_salary: float) -> float:
    """
    Reward = market demand + salary attractiveness (normalized to 0–10).
    """
    salary_score = min(avg_salary / 15000, 10)  # normalize: $150k → 10
    return round((demand_score + salary_score) / 2, 2)


def compute_allocation(scored_skills: List[Dict]) -> List[Dict]:
    """
    Compute portfolio allocation % for each skill.
    Allocation is proportional to (reward_score / risk_score).
    Skills with higher reward-to-risk ratio get more time investment.
    """
    ratios = []
    for skill in scored_skills:
        risk = max(skill["risk_score"], 0.1)  # avoid division by zero
        ratios.append(skill["reward_score"] / risk)

    total = sum(ratios) or 1
    for i, skill in enumerate(scored_skills):
        skill["allocation_percent"] = round((ratios[i] / total) * 100, 1)

    return scored_skills


def score_skills(user_skills: List[Dict], market_data: Dict[str, Dict]) -> List[Dict]:
    """
    Main scoring function.
    Takes user skills + market data, returns fully scored skill list.

    Args:
        user_skills: [{"name": str, "proficiency": int}]
        market_data: {skill_name: {"demand_score": float, "avg_salary": float}}

    Returns:
        List of scored skill dicts with all computed fields.
    """
    scored = []
    for skill in user_skills:
        name = skill["name"]
        proficiency = skill["proficiency"]
        market = market_data.get(name, market_data.get(name.lower(), {}))

        demand_score = market.get("demand_score", 4.0)
        avg_salary = market.get("avg_salary", 90000)
        difficulty = get_difficulty(name)

        growth_potential = compute_growth_potential(proficiency, demand_score)
        risk_score = compute_risk_score(difficulty, demand_score)
        reward_score = compute_reward_score(demand_score, avg_salary)

        scored.append({
            "name": name,
            "proficiency": proficiency,
            "demand_score": demand_score,
            "growth_potential": growth_potential,
            "learning_difficulty": difficulty,
            "risk_score": risk_score,
            "reward_score": reward_score,
            "allocation_percent": 0.0,  # filled by compute_allocation
        })

    return compute_allocation(scored)
