-- =====================================================
-- MindBase 迁移 002：新增收藏 & 回收站字段
-- 在 Supabase SQL Editor 中执行此文件
-- =====================================================

ALTER TABLE notes
  ADD COLUMN IF NOT EXISTS is_starred boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_deleted boolean NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS notes_starred_idx
  ON notes(user_id, is_starred) WHERE is_starred = true;

CREATE INDEX IF NOT EXISTS notes_deleted_idx
  ON notes(user_id, is_deleted) WHERE is_deleted = true;
