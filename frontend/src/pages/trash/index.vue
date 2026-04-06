<template>
  <AppLayout current-page="trash">
    <view class="trash-page">
      <view class="page-header">
        <view class="header-left">
          <text class="page-title">回收站</text>
          <text class="page-sub">{{ notes.length ? `${notes.length} 篇` : '' }}</text>
        </view>
        <view v-if="notes.length" class="btn-empty" @tap="emptyTrash">清空回收站</view>
      </view>

      <view v-if="notes.length" class="hint-bar">
        <text class="hint-text">💡 回收站中的笔记可以恢复，或永久删除</text>
      </view>

      <view v-if="loading" class="state-wrap">
        <text class="state-text">加载中...</text>
      </view>

      <view v-else-if="!notes.length" class="state-wrap">
        <text class="state-icon">🗑️</text>
        <text class="state-title">回收站为空</text>
        <text class="state-sub">删除的笔记会出现在这里，可以随时恢复</text>
      </view>

      <view v-else class="note-list">
        <view v-for="note in notes" :key="note.id" class="note-card">
          <view class="card-body" @tap="openNote(note.id)">
            <view class="card-header">
              <view :class="['source-badge', note.source_type]">
                {{ sourceLabel(note.source_type) }}
              </view>
              <text class="card-date">{{ formatDate(note.updated_at) }}</text>
            </view>
            <text class="card-title">{{ note.title }}</text>
            <view v-if="note.tags && note.tags.length" class="card-tags">
              <text
                v-for="tag in note.tags.slice(0, 3)"
                :key="tag.id"
                class="tag-chip"
                :style="`color:${tag.color};border-color:${tag.color}28`"
              ># {{ tag.name }}</text>
            </view>
          </view>

          <view class="card-actions">
            <view class="action-btn restore-btn" @tap="restore(note)">
              <text class="action-icon">↩️</text>
              <text class="action-label">恢复</text>
            </view>
            <view class="action-btn delete-btn" @tap="deletePermanent(note)">
              <text class="action-icon">🗑️</text>
              <text class="action-label">彻底删除</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { notesApi } from '@/api/index'

const notes   = ref([])
const loading = ref(true)

onMounted(async () => {
  await loadNotes()
})

async function loadNotes() {
  loading.value = true
  try {
    notes.value = await notesApi.list({ deleted: true, limit: 100 })
  } catch {}
  loading.value = false
}

function openNote(id) {
  uni.navigateTo({ url: `/pages/note/detail?id=${id}` })
}

async function restore(note) {
  try {
    await notesApi.restoreNote(note.id)
    notes.value = notes.value.filter(n => n.id !== note.id)
    uni.showToast({ title: '已恢复到知识库', icon: 'success' })
  } catch {}
}

function deletePermanent(note) {
  uni.showModal({
    title: '永久删除',
    content: '删除后无法恢复，确认吗？',
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        try {
          await notesApi.deletePermanent(note.id)
          notes.value = notes.value.filter(n => n.id !== note.id)
          uni.showToast({ title: '已永久删除', icon: 'success' })
        } catch {}
      }
    },
  })
}

function emptyTrash() {
  uni.showModal({
    title: '清空回收站',
    content: `将永久删除全部 ${notes.value.length} 篇笔记，不可恢复`,
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        try {
          await notesApi.emptyTrash()
          notes.value = []
          uni.showToast({ title: '已清空回收站', icon: 'success' })
        } catch {}
      }
    },
  })
}

function sourceLabel(type) {
  return { note: '笔记', url: '网页', pdf: 'PDF' }[type] || type
}

function formatDate(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 86400) return `${Math.floor(diff / 3600) || 1}小时前`
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}天前`
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}
</script>

<style lang="scss" scoped>
.trash-page {
  padding: 28px 24px;
  max-width: 720px;
  margin: 0 auto;
  min-height: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.page-title { font-size: 22px; font-weight: 700; color: var(--text-1); }
.page-sub   { font-size: 13px; color: var(--text-3); }

.btn-empty {
  padding: 7px 14px;
  background: rgba(239,68,68,0.08);
  color: #dc2626;
  border: 1px solid rgba(239,68,68,0.18);
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  &:hover { background: rgba(239,68,68,0.14); }
}

.hint-bar {
  background: rgba(245,158,11,0.08);
  border: 1px solid rgba(245,158,11,0.18);
  border-radius: var(--radius);
  padding: 9px 14px;
  margin-bottom: 20px;

  .hint-text { font-size: 12px; color: #b45309; }
}

.state-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 72px 20px;
  gap: 10px;
  text-align: center;
}
.state-icon  { font-size: 48px; }
.state-title { font-size: 16px; font-weight: 600; color: var(--text-2); }
.state-sub   { font-size: 13px; color: var(--text-3); max-width: 280px; line-height: 1.6; }
.state-text  { font-size: 14px; color: var(--text-3); }

/* Note List */
.note-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.note-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.card-body {
  padding: 14px 16px 10px;
  cursor: pointer;
  transition: background 0.15s;
  &:hover { background: var(--bg-card-hover); }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.source-badge {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 6px;
  font-weight: 500;

  &.note { background: rgba(99,102,241,0.1);  color: #6366f1; }
  &.url  { background: rgba(20,184,166,0.1);  color: #0d9488; }
  &.pdf  { background: rgba(239,68,68,0.1);   color: #dc2626; }
}

.card-date  { font-size: 11px; color: var(--text-3); }
.card-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-1);
  line-height: 1.4;
  margin-bottom: 8px;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-chip {
  font-size: 11px;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 6px;
}

/* Actions */
.card-actions {
  display: flex;
  border-top: 1px solid var(--border);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  cursor: pointer;
  transition: background 0.15s;

  .action-icon  { font-size: 15px; }
  .action-label { font-size: 12px; font-weight: 500; }

  &.restore-btn {
    border-right: 1px solid var(--border);
    color: var(--accent-2);
    &:hover { background: var(--accent-bg); }
  }

  &.delete-btn {
    color: #dc2626;
    &:hover { background: rgba(239,68,68,0.07); }
  }
}
</style>
