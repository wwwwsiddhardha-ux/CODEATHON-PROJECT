"""
Bright Data scraping service.
Uses Bright Data's Dataset API to collect live job listings from LinkedIn/Indeed,
then aggregates them into per-skill market signals (demand score, salary, job count).

Flow:
  1. trigger_scrape()  → POST  /datasets/v3/trigger  → returns snapshot_id
  2. poll_snapshot()   → GET   /datasets/v3/snapshot/{id}/status  → wait for "ready"
  3. fetch_snapshot()  → GET   /datasets/v3/snapshot/{id}         → raw job records
  4. parse_market_signals() → aggregate into {skill: {demand_score, avg_salary, job_count}}
"""
import os
import asyncio
import httpx
from typing import Dict, List

BRIGHT_DATA_BASE_URL = "https://api.brightdata.com/datasets/v3"

# Dataset IDs — override via .env if you have custom datasets
LINKEDIN_DATASET_ID = os.getenv("BRIGHT_DATA_LINKEDIN_DATASET_ID", "gd_lpfll7v5hcjmq1lht0")
INDEED_DATASET_ID   = os.getenv("BRIGHT_DATA_INDEED_DATASET_ID",   "gd_l4dx9j9sscpvs7no2")


def _headers() -> Dict[str, str]:
    """Build auth headers at call time so the key is always fresh from env."""
    return {
        "Authorization": f"Bearer {os.getenv('BRIGHT_DATA_API_KEY', '')}",
        "Content-Type": "application/json",
    }


async def trigger_scrape(keyword: str, location: str = "United States") -> str:
    """
    Trigger a Bright Data snapshot for a job search keyword.
    Returns snapshot_id (empty string on failure).
    """
    payload = [{"keyword": keyword, "location": location, "country": "US"}]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{BRIGHT_DATA_BASE_URL}/trigger",
            params={"dataset_id": LINKEDIN_DATASET_ID, "include_errors": "true"},
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json().get("snapshot_id", "")


async def poll_snapshot(snapshot_id: str, max_wait: int = 60) -> bool:
    """
    Poll until snapshot status is 'ready' or timeout.
    Returns True when ready, False on timeout/error.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        for _ in range(max_wait // 5):
            await asyncio.sleep(5)
            resp = await client.get(
                f"{BRIGHT_DATA_BASE_URL}/snapshot/{snapshot_id}/status",
                headers=_headers(),
            )
            if resp.status_code == 200:
                status = resp.json().get("status", "")
                if status == "ready":
                    return True
                if status in ("failed", "stopped"):
                    return False
    return False


async def fetch_snapshot(snapshot_id: str) -> List[Dict]:
    """Download completed snapshot records as JSON."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(
            f"{BRIGHT_DATA_BASE_URL}/snapshot/{snapshot_id}",
            params={"format": "json"},
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else []


def parse_market_signals(raw_jobs: List[Dict], requested_skills: List[str]) -> Dict[str, Dict]:
    """
    Aggregate raw job records into per-skill market signals.
    Matches requested skills against job titles and skill tags.
    Returns: { skill_name: { job_count, avg_salary, demand_score } }
    """
    skill_stats: Dict[str, Dict] = {s: {"job_count": 0, "total_salary": 0, "salary_count": 0}
                                     for s in requested_skills}

    for job in raw_jobs:
        title       = (job.get("job_title") or job.get("title") or "").lower()
        salary      = _extract_salary(job.get("salary") or job.get("salary_range") or "")
        job_skills  = [s.lower() for s in (job.get("skills") or [])]

        for skill in requested_skills:
            key = skill.lower()
            # Match if skill appears in job's skill tags OR in the job title
            if key in job_skills or key in title:
                skill_stats[skill]["job_count"] += 1
                if salary:
                    skill_stats[skill]["total_salary"] += salary
                    skill_stats[skill]["salary_count"] += 1

    max_jobs = max((v["job_count"] for v in skill_stats.values()), default=1) or 1
    result = {}
    for skill, stats in skill_stats.items():
        avg_salary = (
            stats["total_salary"] / stats["salary_count"]
            if stats["salary_count"] > 0 else 90000
        )
        result[skill] = {
            "job_count":    stats["job_count"],
            "avg_salary":   round(avg_salary, 2),
            "demand_score": round((stats["job_count"] / max_jobs) * 10, 2),
        }
    return result


async def get_market_data(skills: List[str]) -> Dict[str, Dict]:
    """
    Main entry point.
    Returns market data for a list of skills.
    Uses Bright Data live scraping when API key is set, otherwise mock data.
    """
    api_key = os.getenv("BRIGHT_DATA_API_KEY", "")
    if not api_key:
        print("[scraping_service] No BRIGHT_DATA_API_KEY — using mock data.")
        return get_mock_market_data(skills)

    try:
        all_jobs: List[Dict] = []
        # Scrape top 3 skills to stay within rate limits during hackathon
        for skill in skills[:3]:
            print(f"[scraping_service] Triggering scrape for: {skill}")
            snapshot_id = await trigger_scrape(skill)
            if not snapshot_id:
                continue
            ready = await poll_snapshot(snapshot_id)
            if ready:
                jobs = await fetch_snapshot(snapshot_id)
                all_jobs.extend(jobs)
                print(f"[scraping_service] Got {len(jobs)} jobs for '{skill}'")

        if all_jobs:
            return parse_market_signals(all_jobs, skills)

        print("[scraping_service] No jobs returned — falling back to mock data.")
        return get_mock_market_data(skills)

    except Exception as e:
        print(f"[scraping_service] Error: {e} — falling back to mock data.")
        return get_mock_market_data(skills)


def get_mock_market_data(skills: List[str]) -> Dict[str, Dict]:
    """
    Realistic mock market data for demo / local dev without API keys.
    """
    mock_base = {
        "python":           {"job_count": 9500, "avg_salary": 115000, "demand_score": 9.5},
        "react":            {"job_count": 8200, "avg_salary": 110000, "demand_score": 8.2},
        "docker":           {"job_count": 7800, "avg_salary": 118000, "demand_score": 7.8},
        "kubernetes":       {"job_count": 6900, "avg_salary": 125000, "demand_score": 6.9},
        "aws":              {"job_count": 9100, "avg_salary": 122000, "demand_score": 9.1},
        "machine learning": {"job_count": 7200, "avg_salary": 130000, "demand_score": 7.2},
        "sql":              {"job_count": 8800, "avg_salary": 95000,  "demand_score": 8.8},
        "typescript":       {"job_count": 7100, "avg_salary": 108000, "demand_score": 7.1},
        "fastapi":          {"job_count": 3200, "avg_salary": 112000, "demand_score": 3.2},
        "terraform":        {"job_count": 5400, "avg_salary": 128000, "demand_score": 5.4},
        "java":             {"job_count": 8600, "avg_salary": 105000, "demand_score": 8.6},
        "go":               {"job_count": 4800, "avg_salary": 120000, "demand_score": 4.8},
        "javascript":       {"job_count": 9000, "avg_salary": 105000, "demand_score": 9.0},
        "devops":           {"job_count": 6500, "avg_salary": 120000, "demand_score": 6.5},
        "linux":            {"job_count": 5800, "avg_salary": 108000, "demand_score": 5.8},
    }
    return {
        skill: mock_base.get(skill.lower(), {"job_count": 2000, "avg_salary": 90000, "demand_score": 4.0})
        for skill in skills
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_salary(salary_str: str) -> float:
    """Parse salary strings like '$120,000/yr' or '100k-140k' → float."""
    import re
    if not salary_str:
        return 0.0
    # Handle 'k' shorthand: 120k → 120000
    salary_str = re.sub(r"(\d+)k", lambda m: str(int(m.group(1)) * 1000), salary_str.lower())
    nums = re.findall(r"\d+", salary_str.replace(",", ""))
    if not nums:
        return 0.0
    values = [float(n) for n in nums if float(n) > 1000]
    return sum(values) / len(values) if values else 0.0
