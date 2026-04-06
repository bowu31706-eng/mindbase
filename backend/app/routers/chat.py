from fastapi import APIRouter, HTTPException, Depends
from app.deps import get_current_user
from app.database import get_supabase_admin
from app.models.chat import ChatRequest, ChatResponse, ConversationResponse
from app.services.rag import retrieve_chunks
from app.services.ai import chat_with_context, generate_conversation_title

router = APIRouter(prefix="/chat", tags=["问答"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(user=Depends(get_current_user)):
    db = get_supabase_admin()
    result = (
        db.table("conversations")
        .select("*, messages(content)")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    convs = []
    for c in result.data or []:
        msgs = c.pop("messages", []) or []
        last_msg = msgs[-1]["content"] if msgs else None
        convs.append({**c, "last_message": last_msg})
    return convs


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, user=Depends(get_current_user)):
    db = get_supabase_admin()
    conv = db.table("conversations").select("user_id").eq("id", conv_id).execute()
    if not conv.data or conv.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")

    result = (
        db.table("messages")
        .select("*")
        .eq("conversation_id", conv_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


@router.post("/", response_model=ChatResponse)
async def chat(body: ChatRequest, user=Depends(get_current_user)):
    db = get_supabase_admin()

    # 获取或创建对话
    if body.conversation_id:
        conv = db.table("conversations").select("*").eq("id", body.conversation_id).execute()
        if not conv.data or conv.data[0]["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="无权访问")
        conversation_id = body.conversation_id
    else:
        title = await generate_conversation_title(body.message)
        new_conv = db.table("conversations").insert({
            "user_id": user["id"],
            "title": title,
        }).execute()
        conversation_id = new_conv.data[0]["id"]

    # 获取历史消息（最近6条）
    history_result = (
        db.table("messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .limit(6)
        .execute()
    )
    history = list(reversed(history_result.data or []))

    # RAG 检索
    chunks = await retrieve_chunks(user["id"], body.message, top_k=5)

    # 生成回答
    answer = await chat_with_context(body.message, chunks, history)

    # 保存消息
    db.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "user",
        "content": body.message,
        "sources": [],
    }).execute()

    msg_result = db.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": answer,
        "sources": [
            {
                "note_id": c.get("note_id"),
                "note_title": c.get("note_title"),
                "chunk_text": c.get("chunk_text", "")[:200],
                "score": c.get("score", 0),
            }
            for c in chunks
        ],
    }).execute()

    message_id = msg_result.data[0]["id"]

    sources = [
        {
            "note_id": c.get("note_id", ""),
            "note_title": c.get("note_title", ""),
            "chunk_text": c.get("chunk_text", ""),
            "score": c.get("score", 0.0),
        }
        for c in chunks
    ]

    return ChatResponse(
        conversation_id=conversation_id,
        message_id=message_id,
        answer=answer,
        sources=sources,
    )


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user=Depends(get_current_user)):
    db = get_supabase_admin()
    conv = db.table("conversations").select("user_id").eq("id", conv_id).execute()
    if not conv.data or conv.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问")

    db.table("messages").delete().eq("conversation_id", conv_id).execute()
    db.table("conversations").delete().eq("id", conv_id).execute()
    return {"ok": True}
