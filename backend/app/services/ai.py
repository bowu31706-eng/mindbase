from openai import AsyncOpenAI
from app.config import get_settings
from functools import lru_cache


@lru_cache
def get_deepseek_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


async def generate_tags(content_text: str) -> list[str]:
    """根据笔记内容自动生成标签"""
    client = get_deepseek_client()
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个知识库标签助手。根据用户提供的笔记内容，"
                    "生成3-5个简洁的中文标签（每个标签2-6个字）。"
                    "只返回标签，用逗号分隔，不要解释。"
                ),
            },
            {"role": "user", "content": content_text[:1000]},
        ],
        max_tokens=100,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    tags = [t.strip() for t in raw.replace("，", ",").split(",") if t.strip()]
    return tags[:5]


async def chat_with_context(
    question: str,
    context_chunks: list[dict],
    history: list[dict],
) -> str:
    """基于检索到的上下文回答问题"""
    client = get_deepseek_client()

    context_text = "\n\n---\n\n".join(
        f"[来源：{c['note_title']}]\n{c['chunk_text']}" for c in context_chunks
    )

    system_prompt = (
        "你是用户的个人知识库助手。请根据以下知识库内容回答用户的问题。\n"
        "回答要准确、有条理，如果知识库中没有相关内容，请如实说明。\n"
        "不要编造不在知识库中的信息。\n\n"
        f"知识库内容：\n{context_text}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])  # 保留最近3轮对话
    messages.append({"role": "user", "content": question})

    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=2000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


async def generate_conversation_title(first_message: str) -> str:
    """根据第一条消息生成对话标题"""
    client = get_deepseek_client()
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "根据用户的问题，生成一个简短的对话标题（10字以内）。只返回标题，不要标点符号。",
            },
            {"role": "user", "content": first_message},
        ],
        max_tokens=30,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
