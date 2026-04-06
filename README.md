# MindBase

AI 驱动的个人知识库 — 把笔记、PDF、网页变成可以对话的知识库

## 快速开始

### 1. 配置 Supabase 数据库

1. 注册 [Supabase](https://supabase.com)，新建项目
2. 进入 SQL Editor，执行 `supabase/migrations/001_init.sql`
3. Storage 中新建 bucket：`pdfs`（设为 private）

### 2. 启动后端

```bash
cd backend
cp .env.example .env
# 填写 .env 中的 API Keys

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install

# H5 开发
npm run dev:h5

# 微信小程序
npm run dev:mp
# 用微信开发者工具打开 dist/dev/mp-weixin
```

## 环境变量说明

| 变量 | 说明 |
|---|---|
| `SUPABASE_URL` | Supabase 项目 URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `ZHIPU_API_KEY` | 智谱 AI API Key（用于 Embedding）|
| `JWT_SECRET` | JWT 签名密钥（随机字符串）|
| `WECHAT_APPID` | 微信小程序 AppID（可选）|
| `WECHAT_SECRET` | 微信小程序 Secret（可选）|

## 技术栈

- **前端**: uni-app (Vue 3) — 编译到微信小程序 + H5
- **后端**: FastAPI (Python)
- **数据库**: Supabase (PostgreSQL + pgvector)
- **AI 对话**: DeepSeek Chat API
- **AI 向量化**: 智谱 AI Embedding
