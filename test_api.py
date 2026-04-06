import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000/api/v1"

def post(path, data, token=None):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        print(f"HTTP {e.code}: {raw.decode('utf-8', errors='replace')}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}

# 1. 注册
print("=== 注册 ===")
res = post("/auth/register", {"email": "test@mindbase.com", "password": "test1234", "nickname": "testuser"})
print(json.dumps(res, ensure_ascii=False, indent=2))

token = res.get("access_token")

if token:
    print("\n=== 创建笔记 ===")
    note = post("/notes/", {"title": "First Note", "content": "<p>Hello MindBase!</p>", "content_text": "Hello MindBase!"}, token)
    print(json.dumps(note, ensure_ascii=False, indent=2))
else:
    print("\n注册失败，跳过后续测试")
