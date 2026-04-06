from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.services.rag import hybrid_search

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("/")
async def search(q: str, user=Depends(get_current_user)):
    if not q.strip():
        return []
    results = await hybrid_search(user["id"], q.strip(), top_k=10)
    return results
