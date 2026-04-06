import httpx
from bs4 import BeautifulSoup
from readability import Document


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


async def scrape_url(url: str) -> dict:
    """抓取网页，提取标题和正文"""
    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        timeout=15.0,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    html = response.text
    doc = Document(html)
    title = doc.title()

    # readability 提取正文 HTML，再转纯文本
    content_html = doc.summary()
    soup = BeautifulSoup(content_html, "lxml")
    content_text = soup.get_text(separator="\n", strip=True)

    # 清理多余空行
    lines = [line for line in content_text.splitlines() if line.strip()]
    content_text = "\n".join(lines)

    return {
        "title": title or url,
        "content": content_html,
        "content_text": content_text,
        "source_url": url,
    }
