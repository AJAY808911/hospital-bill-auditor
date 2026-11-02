"""
AI Router - Query AI configuration status and request category suggestions.
"""
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["AI"])

class SuggestRequest(BaseModel):
    descriptions: List[str]

@router.get("/status")
def get_ai_status():
    """Returns AI configuration status and whether external LLM or local heuristic is active."""
    return AIService.get_provider_status()

@router.post("/suggest-categories")
async def suggest_categories(req: SuggestRequest):
    """Categorizes bill item descriptions using AI if configured, or deterministic heuristics."""
    return await AIService.suggest_categories(req.descriptions)

