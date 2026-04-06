from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import uuid

from app.deps import get_current_user
from app.database import get_supabase_admin
from app.models.note import NoteCreate, NoteUpdate, NoteResponse, NotePublicToggle, NoteStarToggle
from app.services.embedding import split_text, embed_texts
from app.services.ai import generate_tags
from app.services.scraper import scrape_url
from app.services.pdf import parse_pdf

router = APIRouter(prefix="/notes", tags=["笔记"])


async def _index_note(note_id: str, content_text: str):
    """将笔记内容切块 → 向量化 → 存入 note_chunks"""
    db = get_supabase_admin()

    # 删除旧的 chunks
    db.table("note_chunks").delete().eq("note_id", note_id).execute()

    chunks = split_text(content_text)
    if not chunks:
        return

    embeddings = await embed_texts(chunks)
    rows = [
        {
            "note_id": note_id,
            "chunk_text": chunk,
            "embedding": embedding,
            "chunk_index": i,
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    db.table("note_chunks").insert(rows).execute()


@router.delete("/trash/empty")
async def empty_trash(user=Depends(get_current_user)):
    db = get_supabase_admin()
    result = (
        db.table("notes").select("id")
        .eq("user_id", user["id"])
        .eq("is_deleted", True)
        .execute()
    )
    ids = [r["id"] for r in result.data]
    for note_id in ids:
        db.table("note_chunks").delete().eq("note_id", note_id).execute()
        db.table("note_tags").delete().eq("note_id", note_id).execute()
    if ids:
        db.table("notes").delete().in_("id", ids).execute()
    return {"ok": True, "count": len(ids)}


@router.get("/", response_model=list[NoteResponse])
async def list_notes(
    tag_id: Optional[str] = None,
    starred: bool = False,
    deleted: bool = False,
    limit: int = 20,
    offset: int = 0,
    user=Depends(get_current_user),
):
    db = get_supabase_admin()
    query = (
        db.table("notes")
        .select("*, tags:note_tags(tag:tags(id,name,color))")
        .eq("user_id", user["id"])
        .eq("is_deleted", True if deleted else False)
        .order("updated_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if starred:
        query = query.eq("is_starred", True)
    if tag_id:
        note_ids_result = (
            db.table("note_tags").select("note_id").eq("tag_id", tag_id).execute()
        )
        ids = [r["note_id"] for r in note_ids_result.data]
        if not ids:
            return []
        query = query.in_("id", ids)

    result = query.execute()
    return _format_notes(result.data)


@router.post("/", response_model=NoteResponse)
async def create_note(body: NoteCreate, user=Depends(get_current_user)):
    db = get_supabase_admin()

    note_data = {
        "user_id": user["id"],
        "title": body.title,
        "content": body.content,
        "content_text": body.content_text,
        "source_type": body.source_type,
        "source_url": body.source_url,
        "is_public": False,
    }
    result = db.table("notes").insert(note_data).execute()
    note = result.data[0]

    # 绑定标签
    if body.tag_ids:
        _bind_tags(db, note["id"], body.tag_ids)

    # 异步向量化（不阻塞响应）
    import asyncio
    asyncio.create_task(_index_note(note["id"], body.content_text))

    return await _get_note(note["id"])


@router.post("/from-url", response_model=NoteResponse)
async def create_note_from_url(url: str, user=Depends(get_current_user)):
    scraped = await scrape_url(url)

    # AI 自动打标签
    tags_names = await generate_tags(scraped["content_text"][:1000])
    tag_ids = await _ensure_tags(user["id"], tags_names)

    db = get_supabase_admin()
    result = db.table("notes").insert({
        "user_id": user["id"],
        "title": scraped["title"],
        "content": scraped["content"],
        "content_text": scraped["content_text"],
        "source_type": "url",
        "source_url": url,
        "is_public": False,
    }).execute()
    note = result.data[0]

    if tag_ids:
        _bind_tags(db, note["id"], tag_ids)

    import asyncio
    asyncio.create_task(_index_note(note["id"], scraped["content_text"]))

    return await _get_note(note["id"])


@router.post("/from-pdf", response_model=NoteResponse)
async def create_note_from_pdf(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    file_bytes = await file.read()
    parsed = parse_pdf(file_bytes)

    # 上传文件到 Supabase Storage
    db = get_supabase_admin()
    file_path = f"{user['id']}/{uuid.uuid4()}.pdf"
    db.storage.from_("pdfs").upload(file_path, file_bytes, {"content-type": "application/pdf"})

    # AI 自动打标签
    tags_names = await generate_tags(parsed["content_text"][:1000])
    tag_ids = await _ensure_tags(user["id"], tags_names)

    result = db.table("notes").insert({
        "user_id": user["id"],
        "title": parsed["title"],
        "content": f"<p>{parsed['content_text'][:500]}...</p>",
        "content_text": parsed["content_text"],
        "source_type": "pdf",
        "file_path": file_path,
        "is_public": False,
    }).execute()
    note = result.data[0]

    if tag_ids:
        _bind_tags(db, note["id"], tag_ids)

    import asyncio
    asyncio.create_task(_index_note(note["id"], parsed["content_text"]))

    return await _get_note(note["id"])


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, user=Depends(get_current_user)):
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, body: NoteUpdate, user=Depends(get_current_user)):
    db = get_supabase_admin()
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")

    update_data = body.model_dump(exclude_none=True, exclude={"tag_ids"})
    if update_data:
        db.table("notes").update(update_data).eq("id", note_id).execute()

    if body.tag_ids is not None:
        db.table("note_tags").delete().eq("note_id", note_id).execute()
        _bind_tags(db, note_id, body.tag_ids)

    if body.content_text:
        import asyncio
        asyncio.create_task(_index_note(note_id, body.content_text))

    return await _get_note(note_id)


@router.delete("/{note_id}")
async def delete_note(note_id: str, user=Depends(get_current_user)):
    """软删除：移入回收站"""
    db = get_supabase_admin()
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")
    db.table("notes").update({"is_deleted": True}).eq("id", note_id).execute()
    return {"ok": True}


@router.patch("/{note_id}/star", response_model=NoteResponse)
async def toggle_star(note_id: str, body: NoteStarToggle, user=Depends(get_current_user)):
    db = get_supabase_admin()
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")
    db.table("notes").update({"is_starred": body.is_starred}).eq("id", note_id).execute()
    return await _get_note(note_id)


@router.post("/{note_id}/restore")
async def restore_note(note_id: str, user=Depends(get_current_user)):
    db = get_supabase_admin()
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")
    db.table("notes").update({"is_deleted": False}).eq("id", note_id).execute()
    return {"ok": True}


@router.delete("/{note_id}/permanent")
async def delete_note_permanent(note_id: str, user=Depends(get_current_user)):
    """永久删除，不可恢复"""
    db = get_supabase_admin()
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")
    db.table("note_chunks").delete().eq("note_id", note_id).execute()
    db.table("note_tags").delete().eq("note_id", note_id).execute()
    db.table("notes").delete().eq("id", note_id).execute()
    return {"ok": True}


@router.patch("/{note_id}/public", response_model=NoteResponse)
async def toggle_public(note_id: str, body: NotePublicToggle, user=Depends(get_current_user)):
    db = get_supabase_admin()
    note = await _get_note(note_id)
    if note["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")

    update = {"is_public": body.is_public}
    if body.is_public and not note.get("public_slug"):
        update["public_slug"] = uuid.uuid4().hex[:10]

    db.table("notes").update(update).eq("id", note_id).execute()
    return await _get_note(note_id)


@router.get("/public/{slug}", response_model=NoteResponse)
async def get_public_note(slug: str):
    db = get_supabase_admin()
    result = (
        db.table("notes")
        .select("*, tags:note_tags(tag:tags(id,name,color))")
        .eq("public_slug", slug)
        .eq("is_public", True)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return _format_notes(result.data)[0]


# ── 内部工具函数 ──────────────────────────────────────────

async def _get_note(note_id: str) -> dict:
    db = get_supabase_admin()
    result = (
        db.table("notes")
        .select("*, tags:note_tags(tag:tags(id,name,color))")
        .eq("id", note_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return _format_notes(result.data)[0]


def _format_notes(data: list) -> list:
    for note in data:
        # 展平嵌套标签结构
        raw_tags = note.pop("tags", []) or []
        note["tags"] = [
            r["tag"] for r in raw_tags if r.get("tag")
        ]
    return data


def _bind_tags(db, note_id: str, tag_ids: list[str]):
    rows = [{"note_id": note_id, "tag_id": tid} for tid in tag_ids]
    db.table("note_tags").insert(rows).execute()


async def _ensure_tags(user_id: str, tag_names: list[str]) -> list[str]:
    """确保标签存在，返回 tag_id 列表"""
    db = get_supabase_admin()
    tag_ids = []
    for name in tag_names:
        existing = (
            db.table("tags").select("id").eq("user_id", user_id).eq("name", name).execute()
        )
        if existing.data:
            tag_ids.append(existing.data[0]["id"])
        else:
            result = db.table("tags").insert({"user_id": user_id, "name": name}).execute()
            tag_ids.append(result.data[0]["id"])
    return tag_ids
