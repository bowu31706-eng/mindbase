from zhipuai import ZhipuAI
from app.config import get_settings
import asyncio


_client: ZhipuAI | None = None


def _get_client() -> ZhipuAI:
    global _client
    if _client is None:
        _client = ZhipuAI(api_key=get_settings().zhipu_api_key)
    return _client


CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def split_text(text: str) -> list[str]:
    """将长文本切割成带重叠的小块"""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


async def embed_text(text: str) -> list[float]:
    """单条文本向量化"""
    client = _get_client()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.embeddings.create(model="embedding-3", input=text),
    )
    return response.data[0].embedding


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量向量化"""
    tasks = [embed_text(t) for t in texts]
    return await asyncio.gather(*tasks)
