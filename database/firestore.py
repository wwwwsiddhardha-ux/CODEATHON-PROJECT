"""
Firestore database helper.
Handles persistence of user profiles and portfolio history.
Falls back gracefully if Google Cloud credentials are not configured.
"""
import os
from typing import Optional, Dict, List

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")


def _get_client():
    """Return a Firestore client, or None if not configured."""
    try:
        from google.cloud import firestore
        return firestore.Client(project=GOOGLE_CLOUD_PROJECT)
    except Exception as e:
        print(f"[db] Firestore not available: {e}")
        return None


def save_profile(user_name: str, profile_data: Dict) -> bool:
    """Save or update a user profile in Firestore."""
    db = _get_client()
    if not db:
        return False
    db.collection("profiles").document(user_name).set(profile_data)
    return True


def get_profile(user_name: str) -> Optional[Dict]:
    """Retrieve a user profile from Firestore."""
    db = _get_client()
    if not db:
        return None
    doc = db.collection("profiles").document(user_name).get()
    return doc.to_dict() if doc.exists else None


def save_portfolio_snapshot(user_name: str, snapshot: Dict) -> bool:
    """
    Save a portfolio snapshot for history tracking.
    Each snapshot is a timestamped record of scored skills.
    """
    import datetime
    db = _get_client()
    if not db:
        return False
    snapshot["timestamp"] = datetime.datetime.utcnow().isoformat()
    db.collection("portfolio_history").document(user_name).collection("snapshots").add(snapshot)
    return True


def get_portfolio_history(user_name: str) -> List[Dict]:
    """Retrieve all portfolio snapshots for a user (for growth comparison)."""
    db = _get_client()
    if not db:
        return []
    docs = (
        db.collection("portfolio_history")
        .document(user_name)
        .collection("snapshots")
        .order_by("timestamp")
        .stream()
    )
    return [doc.to_dict() for doc in docs]
