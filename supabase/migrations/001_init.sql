-- =====================================================
-- MindBase 数据库初始化
-- 在 Supabase SQL Editor 中执行此文件
-- =====================================================

-- 启用 pgvector 扩展
create extension if not exists vector;

-- =====================================================
-- 用户表（自管理，不依赖 Supabase Auth）
-- =====================================================
create table if not exists users (
  id            uuid primary key default gen_random_uuid(),
  email         text unique not null,
  password_hash text,
  nickname      text not null default '新用户',
  avatar_url    text,
  wechat_openid text unique,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- =====================================================
-- 笔记表
-- =====================================================
create table if not exists notes (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references users(id) on delete cascade,
  title        text not null,
  content      text not null default '',      -- 富文本 HTML
  content_text text not null default '',      -- 纯文本，用于检索和 embedding
  source_type  text not null default 'note' check (source_type in ('note', 'url', 'pdf')),
  source_url   text,
  file_path    text,
  is_public    boolean not null default false,
  public_slug  text unique,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index if not exists notes_user_id_idx on notes(user_id);
create index if not exists notes_updated_at_idx on notes(updated_at desc);
create index if not exists notes_public_slug_idx on notes(public_slug) where public_slug is not null;

-- =====================================================
-- 标签表
-- =====================================================
create table if not exists tags (
  id      uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  name    text not null,
  color   text not null default '#6366f1',
  unique(user_id, name)
);

create index if not exists tags_user_id_idx on tags(user_id);

-- =====================================================
-- 笔记-标签关联表
-- =====================================================
create table if not exists note_tags (
  note_id uuid not null references notes(id) on delete cascade,
  tag_id  uuid not null references tags(id) on delete cascade,
  primary key (note_id, tag_id)
);

-- =====================================================
-- 笔记向量块表（RAG 核心）
-- =====================================================
create table if not exists note_chunks (
  id          uuid primary key default gen_random_uuid(),
  note_id     uuid not null references notes(id) on delete cascade,
  chunk_text  text not null,
  embedding   vector(1024),           -- 智谱 embedding-3 维度为 1024
  chunk_index integer not null default 0
);

create index if not exists note_chunks_note_id_idx on note_chunks(note_id);

-- 向量相似度索引（IVFFlat，适合数量级在万级以下）
create index if not exists note_chunks_embedding_idx
  on note_chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- =====================================================
-- 对话表
-- =====================================================
create table if not exists conversations (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references users(id) on delete cascade,
  title      text not null default '新对话',
  created_at timestamptz not null default now()
);

create index if not exists conversations_user_id_idx on conversations(user_id);

-- =====================================================
-- 消息表
-- =====================================================
create table if not exists messages (
  id              uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  role            text not null check (role in ('user', 'assistant')),
  content         text not null,
  sources         jsonb default '[]',
  created_at      timestamptz not null default now()
);

create index if not exists messages_conversation_id_idx on messages(conversation_id);
create index if not exists messages_created_at_idx on messages(created_at);

-- =====================================================
-- updated_at 自动更新触发器
-- =====================================================
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger notes_updated_at
  before update on notes
  for each row execute function update_updated_at();

create trigger users_updated_at
  before update on users
  for each row execute function update_updated_at();

-- =====================================================
-- pgvector 语义搜索函数（供 Python 端 rpc 调用）
-- =====================================================
create or replace function match_note_chunks(
  query_embedding vector(1024),
  match_user_id   uuid,
  match_count     int default 5,
  match_threshold float default 0.5
)
returns table (
  note_id    uuid,
  note_title text,
  chunk_text text,
  score      float
)
language sql stable
as $$
  select
    n.id        as note_id,
    n.title     as note_title,
    c.chunk_text,
    1 - (c.embedding <=> query_embedding) as score
  from note_chunks c
  join notes n on n.id = c.note_id
  where n.user_id = match_user_id
    and 1 - (c.embedding <=> query_embedding) >= match_threshold
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
