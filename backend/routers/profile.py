"""
Profile router.
Handles user profile creation and retrieval.
In production, persists to Firestore. Uses in-memory store for demo.
"""
from fastapi import APIRouter, HTTPException
from models.schemas import UserProfile

router = APIRouter()

# In-memory store (replace with Firestore in production)
_profiles: dict = {}


@router.post("/")
def create_profile(profile: UserProfile):
    """Save a user profile keyed by name."""
    _profiles[profile.name] = profile.model_dump()
    return {"message": "Profile saved", "name": profile.name}


@router.get("/{name}")
def get_profile(name: str):
    """Retrieve a saved user profile by name."""
    if name not in _profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profiles[name]


@router.get("/")
def list_profiles():
    """List all saved profile names."""
    return {"profiles": list(_profiles.keys())}
