from app.database import get_supabase_admin
from app.services.embedding import embed_text


async def retrieve_chunks(
    user_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """语义检索：向量化查询 → pgvector 相似度搜索"""
    query_embedding = await embed_text(query)
    db = get_supabase_admin()

    # 调用 Supabase RPC（PostgreSQL 函数）执行向量搜索
    result = db.rpc(
        "match_note_chunks",
        {
            "query_embedding": query_embedding,
            "match_user_id": user_id,
            "match_count": top_k,
            "match_threshold": 0.5,
        },
    ).execute()

    return result.data or []


async def keyword_search(
    user_id: str,
    query: str,
    limit: int = 20,
) -> list[dict]:
    """关键词全文搜索"""
    db = get_supabase_admin()
    result = (
        db.table("notes")
        .select("id, title, content_text, source_type, created_at, updated_at")
        .eq("user_id", user_id)
        .or_(f"title.ilike.%{query}%,content_text.ilike.%{query}%")
        .limit(limit)
        .execute()
    )
    return result.data or []


async def hybrid_search(
    user_id: str,
    query: str,
    top_k: int = 10,
) -> list[dict]:
    """混合搜索：语义 + 关键词，结果去重合并"""
    semantic, keyword = await _gather_searches(user_id, query, top_k)

    seen_ids = set()
    merged = []

    # 语义结果优先
    for item in semantic:
        note_id = item.get("note_id")
        if note_id not in seen_ids:
            seen_ids.add(note_id)
            merged.append({**item, "search_type": "semantic"})

    # 补充关键词结果
    for item in keyword:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            merged.append({
                "note_id": item["id"],
                "note_title": item["title"],
                "chunk_text": item["content_text"][:300],
                "score": 0.0,
                "search_type": "keyword",
            })

    return merged[:top_k]


async def _gather_searches(user_id, query, top_k):
    import asyncio
    return await asyncio.gather(
        retrieve_chunks(user_id, query, top_k),
        keyword_search(user_id, query, top_k),
    )
