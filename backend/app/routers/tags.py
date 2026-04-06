from fastapi import APIRouter, HTTPException, Depends
from app.deps import get_current_user
from app.database import get_supabase_admin
from app.models.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("/", response_model=list[TagResponse])
async def list_tags(user=Depends(get_current_user)):
    db = get_supabase_admin()
    result = db.table("tags").select("*").eq("user_id", user["id"]).order("name").execute()

    tags = result.data or []
    # 统计每个标签下的笔记数
    for tag in tags:
        count_result = (
            db.table("note_tags").select("note_id", count="exact").eq("tag_id", tag["id"]).execute()
        )
        tag["note_count"] = count_result.count or 0

    return tags


@router.post("/", response_model=TagResponse)
async def create_tag(body: TagCreate, user=Depends(get_current_user)):
    db = get_supabase_admin()

    existing = (
        db.table("tags").select("id").eq("user_id", user["id"]).eq("name", body.name).execute()
    )
    if existing.data:
        raise HTTPException(status_code=400, detail="标签名已存在")

    result = db.table("tags").insert({
        "user_id": user["id"],
        "name": body.name,
        "color": body.color,
    }).execute()

    tag = result.data[0]
    tag["note_count"] = 0
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: str, body: TagUpdate, user=Depends(get_current_user)):
    db = get_supabase_admin()
    _assert_owner(db, tag_id, user["id"])

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    result = db.table("tags").update(update_data).eq("id", tag_id).execute()
    tag = result.data[0]
    count_result = db.table("note_tags").select("note_id", count="exact").eq("tag_id", tag_id).execute()
    tag["note_count"] = count_result.count or 0
    return tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: str, user=Depends(get_current_user)):
    db = get_supabase_admin()
    _assert_owner(db, tag_id, user["id"])

    db.table("note_tags").delete().eq("tag_id", tag_id).execute()
    db.table("tags").delete().eq("id", tag_id).execute()
    return {"ok": True}


def _assert_owner(db, tag_id: str, user_id: str):
    result = db.table("tags").select("user_id").eq("id", tag_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="标签不存在")
    if result.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="无权操作")
