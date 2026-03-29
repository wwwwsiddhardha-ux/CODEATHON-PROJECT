"""
Main FastAPI application entry point.
"""
from dotenv import load_dotenv
load_dotenv()  # must be first — loads .env before any service reads os.getenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import profile, market, recommendations, roadmap

app = FastAPI(title="Skill Investment Portfolio Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["Roadmap"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Skill Investment Portfolio Engine running"}
