# MindBase 项目启动与排错记录

## 项目概览

| 层级 | 技术栈 |
|------|--------|
| 前端 | uni-app (Vue 3 + Pinia) → H5 / 微信小程序 |
| 后端 | FastAPI (Python 3.14) |
| 数据库 | Supabase (PostgreSQL + pgvector) |
| AI | DeepSeek Chat + 智谱 Embedding |

---

## 一、后端启动

### 环境要求
- Python 3.14+
- 所有依赖已安装（见 `backend/requirements.txt`）

### 启动命令

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

开发模式（热重载）：

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
# {"status": "ok", "version": "1.0.0"}
```

---

## 二、前端启动

### 环境要求
- Node.js v24+
- 已执行 `npm install`（含 `--legacy-peer-deps`）

### 启动命令

```bash
cd frontend
npm run dev:h5      # H5 Web，访问 http://localhost:5173
npm run dev:mp      # 微信小程序，输出到 dist/dev/mp-weixin
```

---

## 三、已解决的问题

---

### 问题 1：安装 supabase 时 pyiceberg 编译失败

**现象：**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**原因：** `supabase >= 2.28` 依赖 `pyiceberg`，需要 C++ 编译器。

**解决：** 降级到兼容版本：

```bash
pip install supabase==2.7.4
```

---

### 问题 2：zhipuai 安装时版本回溯卡住

**现象：** pip 不停尝试数百个版本。

**解决：** 直接指定版本：

```bash
pip install zhipuai==2.1.5.20230904
```

---

### 问题 3：Supabase 新格式 API Key 不兼容

**现象：** Supabase 控制台新版生成的 key 格式为 `sb_publishable_xxx` / `sb_secret_xxx`，supabase Python SDK 2.7.4 无法识别。

**错误：**
```
SupabaseException: Invalid API key
```

**解决：**
1. 进入 Supabase 控制台 → Project Settings → API
2. 找到 **"Legacy anon, service_role API keys"** 标签
3. 复制旧格式的 JWT key（以 `eyJ...` 开头）
4. 填入 `backend/.env` 的 `SUPABASE_KEY` 和 `SUPABASE_SERVICE_KEY`

---

### 问题 4：.env 更新后仍使用旧 Key（lru_cache 缓存）

**现象：** 修改 `.env` 后重新测试，依然报 `Invalid API key`。

**原因：** `config.py` 和 `database.py` 都使用了 `@lru_cache`，进程内缓存了旧值，必须重启进程才生效。

**解决：**

```bash
# 找到占用 8000 端口的进程并终止
powershell -Command "Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess"
powershell -Command "Stop-Process -Id <PID> -Force"
```

然后重新启动 uvicorn。

---

### 问题 5：config.py 相对路径 .env 找不到

**现象：** 从非 `backend/` 目录启动 uvicorn 时，`.env` 加载失败，所有配置为空。

**原因：** `pydantic-settings` 的 `env_file = ".env"` 是相对于**当前工作目录**的，不是相对于文件本身。

**解决：** 修改 `backend/app/config.py`，使用绝对路径：

```python
from pathlib import Path

_ENV_FILE = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"
```

---

### 问题 6：注册接口返回 500（bcrypt 版本不兼容）

**现象：**
```
POST /api/v1/auth/register → 500 Internal Server Error
```

**服务器日志：**
```
(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
...
ValueError: password cannot be longer than 72 bytes, truncate manually
```

**原因：** `passlib 1.7.4`（2020年停止维护）与 `bcrypt >= 4.0` 不兼容。bcrypt 4.x 改变了 API，passlib 在检测"wrap bug"时触发 ValueError。

**解决：** 降级 bcrypt：

```bash
pip install bcrypt==3.2.2
```

---

### 问题 7：前端 npm run dev:h5 报 'uni' 未找到

**现象：**
```
'uni' 不是内部或外部命令
```

**原因：** `package.json` 中的 `@dcloudio/uni-app` 不包含 `bin/uni`，`uni` CLI 来自单独的包 `@dcloudio/vite-plugin-uni`。

**解决：**

```bash
npm install -D "@dcloudio/vite-plugin-uni@3.0.0-4020920240930001" --legacy-peer-deps
```

> 版本号必须与 `@dcloudio/uni-app` 保持一致。

---

### 问题 8：Vite 报 404 / 无法确定入口点

**现象：**
```
Could not auto-determine entry point from rollupOptions or html files
```
访问 `http://localhost:5173/` 返回 404。

**原因：** uni-app Vite 项目需要在**项目根目录**（`frontend/`）有 `index.html`，否则 Vite 无法确定入口。

**解决：** 在 `frontend/` 根目录创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" />
    <title>MindBase - AI 知识库</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

同时确保 `frontend/vite.config.js` 存在：

```js
import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## 四、依赖版本锁定（关键）

| 包 | 版本 | 原因 |
|----|------|------|
| `supabase` | `2.7.4` | 避免 pyiceberg 编译依赖 |
| `bcrypt` | `3.2.2` | passlib 1.7.4 不兼容 bcrypt >= 4.0 |
| `zhipuai` | `2.1.5.20230904` | 版本回溯问题 |
| `@dcloudio/vite-plugin-uni` | `3.0.0-4020920240930001` | 与 uni-app 版本匹配 |

---

## 五、端口占用处理

```bash
# 查看 8000 端口占用进程
powershell -Command "netstat -ano | Select-String ':8000'"

# 终止指定 PID
powershell -Command "Stop-Process -Id <PID> -Force"

# 终止所有 python 进程
powershell -Command "Get-Process -Name 'python*' | Stop-Process -Force"
```

---

## 六、完整安装顺序（从零开始）

### 后端

```bash
cd backend

# 1. 安装核心依赖（指定兼容版本）
pip install supabase==2.7.4
pip install bcrypt==3.2.2
pip install passlib[bcrypt]
pip install zhipuai==2.1.5.20230904
pip install fastapi uvicorn[standard] python-dotenv
pip install "pydantic>=2.9" "pydantic-settings>=2.5"
pip install "openai>=1.0"
pip install httpx beautifulsoup4 readability-lxml lxml pymupdf
pip install python-multipart "python-jose[cryptography]"

# 2. 配置 .env（从 .env.example 复制并填写）

# 3. 运行数据库 migration（在 Supabase SQL Editor 中执行）
#    文件：supabase/migrations/001_init.sql

# 4. 启动
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 前端

```bash
cd frontend

# 1. 安装依赖
npm install --legacy-peer-deps
npm install -D "@dcloudio/vite-plugin-uni@3.0.0-4020920240930001" --legacy-peer-deps

# 2. 确认以下文件存在：
#    - index.html（项目根目录）
#    - vite.config.js（项目根目录）
#    - src/static/tab-*.png（8 个 tab bar 图标）

# 3. 启动 H5 开发服务器
npm run dev:h5
# 访问 http://localhost:5173
```
