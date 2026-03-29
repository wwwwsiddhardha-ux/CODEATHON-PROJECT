"""
Featherless AI service.
Calls the Featherless AI API (OpenAI-compatible) with Llama 3.1 8B to generate
intelligent skill portfolio recommendations and weekly learning plans.

Featherless docs: https://featherless.ai/docs
API base: https://api.featherless.ai/v1
"""
import os
import re
import json
import httpx
from typing import List, Dict

FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
# Llama 3.1 8B — fast, instruction-tuned, available on Featherless free tier
MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"

SYSTEM_PROMPT = (
    "You are a career investment advisor AI. "
    "You analyze skill portfolios exactly like a financial advisor analyzes investment portfolios. "
    "You ALWAYS respond with valid JSON only — no markdown, no explanation outside the JSON."
)


async def get_skill_recommendations(
    career_goal: str,
    scored_skills: List[Dict],
    hours_per_week: int,
) -> Dict:
    """
    Call Featherless AI to generate portfolio recommendations.
    Returns dict with keys: invest_more, reduce_focus, summary, weekly_plan.
    Falls back to deterministic mock if API key is missing or call fails.
    """
    api_key = os.getenv("FEATHERLESS_API_KEY", "")
    if not api_key:
        print("[ai_service] No FEATHERLESS_API_KEY — using mock recommendations.")
        return _mock_recommendations(scored_skills, hours_per_week)

    prompt = _build_prompt(career_goal, scored_skills, hours_per_week)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{FEATHERLESS_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1200,
                },
            )
            resp.raise_for_status()
            raw_content = resp.json()["choices"][0]["message"]["content"]
            print(f"[ai_service] Raw response: {raw_content[:200]}")
            return _parse_json_response(raw_content, scored_skills, hours_per_week)

    except httpx.HTTPStatusError as e:
        print(f"[ai_service] HTTP error {e.response.status_code}: {e.response.text[:200]}")
        return _mock_recommendations(scored_skills, hours_per_week)
    except Exception as e:
        print(f"[ai_service] Error: {e} — using mock recommendations.")
        return _mock_recommendations(scored_skills, hours_per_week)


def _build_prompt(career_goal: str, scored_skills: List[Dict], hours_per_week: int) -> str:
    """Build a tight, structured prompt for Featherless AI."""
    skills_text = "\n".join([
        f"  - {s['name']}: proficiency={s['proficiency']}/10, "
        f"demand={s['demand_score']}/10, risk={s['risk_score']:.1f}, reward={s['reward_score']:.1f}"
        for s in scored_skills
    ])

    skill_names = [s["name"] for s in scored_skills]

    return f"""Career Goal: {career_goal}
Hours available per week: {hours_per_week}

Skill Portfolio:
{skills_text}

Respond with ONLY this JSON (no markdown, no extra text):
{{
  "invest_more": ["skill1", "skill2", "skill3"],
  "reduce_focus": ["skill1", "skill2"],
  "summary": "2-3 sentences of plain-English portfolio advice",
  "weekly_plan": [
    {{"skill": "skill_name", "hours": 5.0, "reason": "one sentence why"}},
    {{"skill": "skill_name", "hours": 3.0, "reason": "one sentence why"}}
  ]
}}

Rules:
- Only use skill names from this list: {skill_names}
- weekly_plan hours must sum to exactly {hours_per_week}
- invest_more = highest reward/risk ratio skills for the career goal
- reduce_focus = lowest ROI skills"""


def _parse_json_response(content: str, scored_skills: List[Dict], hours_per_week: int) -> Dict:
    """
    Safely extract JSON from the AI response.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Strip markdown code fences if present
    content = re.sub(r"```(?:json)?", "", content).strip()

    # Try direct parse first
    try:
        result = json.loads(content)
        if _is_valid_response(result):
            return result
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object from within the text
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if _is_valid_response(result):
                return result
        except json.JSONDecodeError:
            pass

    print("[ai_service] Could not parse AI JSON — using mock.")
    return _mock_recommendations(scored_skills, hours_per_week)


def _is_valid_response(data: Dict) -> bool:
    """Check that the AI response has all required keys."""
    return all(k in data for k in ("invest_more", "reduce_focus", "summary", "weekly_plan"))


def _mock_recommendations(scored_skills: List[Dict], hours_per_week: int) -> Dict:
    """
    Deterministic fallback when Featherless AI is unavailable.
    Ranks by reward_score and distributes hours proportionally.
    """
    sorted_skills = sorted(scored_skills, key=lambda x: x["reward_score"], reverse=True)
    invest_more  = [s["name"] for s in sorted_skills[:4]]
    reduce_focus = [s["name"] for s in sorted_skills[-2:]]

    total_reward = sum(s["reward_score"] for s in sorted_skills) or 1
    weekly_plan = []
    allocated = 0.0
    for i, skill in enumerate(sorted_skills):
        if i == len(sorted_skills) - 1:
            # Give remaining hours to last skill to ensure exact total
            hours = round(hours_per_week - allocated, 1)
        else:
            hours = round((skill["reward_score"] / total_reward) * hours_per_week, 1)
        allocated += hours
        if hours > 0:
            weekly_plan.append({
                "skill":  skill["name"],
                "hours":  hours,
                "reason": f"Reward score {skill['reward_score']:.1f} — strong ROI for your career goal.",
            })

    return {
        "invest_more":  invest_more,
        "reduce_focus": reduce_focus,
        "summary": (
            f"Prioritize {', '.join(invest_more[:2])} — they offer the highest market demand "
            f"and salary potential for your goal. "
            f"Reduce time on {', '.join(reduce_focus)} which have lower ROI right now."
        ),
        "weekly_plan": weekly_plan,
    }
