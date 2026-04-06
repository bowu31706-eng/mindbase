import fitz  # PyMuPDF
import io


def parse_pdf(file_bytes: bytes) -> dict:
    """解析 PDF，提取文本内容"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    pages_text = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages_text.append(text.strip())

    doc.close()

    content_text = "\n\n".join(pages_text)

    # 提取标题：优先用第一页前100字
    title = ""
    if pages_text:
        first_lines = [l for l in pages_text[0].splitlines() if l.strip()]
        title = first_lines[0][:100] if first_lines else "未命名文档"

    return {
        "title": title,
        "content_text": content_text,
        "page_count": len(pages_text),
    }
