<template>
  <AppLayout current-page="favorites">
    <view class="fav-page">
      <view class="page-header">
        <text class="page-title">收藏</text>
        <text class="page-sub">{{ notes.length ? `${notes.length} 篇` : '' }}</text>
      </view>

      <view v-if="loading" class="state-wrap">
        <text class="state-text">加载中...</text>
      </view>

      <view v-else-if="!notes.length" class="state-wrap">
        <text class="state-icon">⭐</text>
        <text class="state-title">暂无收藏</text>
        <text class="state-sub">在笔记详情页点击收藏，快速找到重要内容</text>
      </view>

      <view v-else class="note-list">
        <view
          v-for="note in notes"
          :key="note.id"
          class="note-card"
          @tap="openNote(note.id)"
        >
          <view class="card-header">
            <view :class="['source-badge', note.source_type]">
              {{ sourceLabel(note.source_type) }}
            </view>
            <view class="card-actions" @tap.stop>
              <view class="action-star active" @tap="unstar(note)">⭐</view>
            </view>
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
          <text class="card-date">{{ formatDate(note.updated_at) }}</text>
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
  try {
    notes.value = await notesApi.list({ starred: true, limit: 100 })
  } catch {}
  loading.value = false
})

function openNote(id) {
  uni.navigateTo({ url: `/pages/note/detail?id=${id}` })
}

async function unstar(note) {
  try {
    await notesApi.starNote(note.id, false)
    notes.value = notes.value.filter(n => n.id !== note.id)
    uni.showToast({ title: '已取消收藏', icon: 'none' })
  } catch {}
}

function sourceLabel(type) {
  return { note: '笔记', url: '网页', pdf: 'PDF' }[type] || type
}

function formatDate(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 3600)  return `${Math.max(1, Math.floor(diff / 60))}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}
</script>

<style lang="scss" scoped>
.fav-page {
  padding: 28px 24px;
  max-width: 720px;
  margin: 0 auto;
  min-height: 100%;
}

.page-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 24px;
}
.page-title { font-size: 22px; font-weight: 700; color: var(--text-1); }
.page-sub   { font-size: 13px; color: var(--text-3); }

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

/* Note Grid */
.note-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.note-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;

  &:hover {
    box-shadow: var(--shadow);
    transform: translateY(-1px);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
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

.card-actions { display: flex; gap: 6px; }
.action-star {
  font-size: 16px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s, transform 0.15s;
  &:hover    { opacity: 1; transform: scale(1.2); }
  &.active   { opacity: 1; }
}

.card-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-1);
  line-height: 1.4;
  margin-bottom: 10px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.tag-chip {
  font-size: 11px;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 6px;
}

.card-date { font-size: 11px; color: var(--text-3); display: block; }
</style>
