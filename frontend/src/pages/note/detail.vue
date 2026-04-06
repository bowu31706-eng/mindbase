<template>
  <view class="page">
    <view v-if="note" class="content">
      <!-- 笔记头部 -->
      <view class="note-meta">
        <view class="source-row">
          <view :class="['source-badge', note.source_type]">
            {{ sourceLabel(note.source_type) }}
          </view>
          <text v-if="note.source_url" class="source-url" @tap="openUrl">
            {{ note.source_url }}
          </text>
        </view>
        <text class="note-title">{{ note.title }}</text>
        <view class="tag-row">
          <text
            v-for="tag in note.tags"
            :key="tag.id"
            class="tag"
            :style="`color:${tag.color};border-color:${tag.color}33`"
          ># {{ tag.name }}</text>
        </view>
        <text class="note-date">{{ formatDate(note.updated_at) }}</text>
      </view>

      <!-- 正文 -->
      <rich-text class="note-body" :nodes="note.content" />
    </view>

    <view v-if="!note && !loading" class="empty">
      <text>笔记不存在</text>
    </view>

    <!-- 底部操作 -->
    <view v-if="note" class="bottom-bar safe-area-bottom">
      <view class="action" @tap="editNote">
        <text class="action-icon">✏️</text>
        <text>编辑</text>
      </view>
      <view class="action" @tap="togglePublic">
        <text class="action-icon">{{ note.is_public ? '🔓' : '🔒' }}</text>
        <text>{{ note.is_public ? '已公开' : '私有' }}</text>
      </view>
      <view v-if="note.is_public" class="action" @tap="copyLink">
        <text class="action-icon">🔗</text>
        <text>复制链接</text>
      </view>
      <view class="action danger" @tap="deleteNote">
        <text class="action-icon">🗑️</text>
        <text>删除</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notesApi } from '@/api/index'

const props = defineProps({ id: String })
const note = ref(null)
const loading = ref(true)

onMounted(async () => {
  note.value = await notesApi.get(props.id)
  loading.value = false
})

function editNote() {
  uni.navigateTo({ url: `/pages/note/edit?id=${note.value.id}` })
}

async function togglePublic() {
  const updated = await notesApi.togglePublic(note.value.id, !note.value.is_public)
  note.value = updated
  uni.showToast({ title: updated.is_public ? '已设为公开' : '已设为私有' })
}

function copyLink() {
  const url = `https://your-domain.com/share/${note.value.public_slug}`
  uni.setClipboardData({ data: url })
  uni.showToast({ title: '链接已复制' })
}

async function deleteNote() {
  uni.showModal({
    title: '删除笔记',
    content: '确认删除？此操作不可撤销',
    success: async (res) => {
      if (res.confirm) {
        await notesApi.delete(note.value.id)
        uni.navigateBack()
      }
    },
  })
}

function openUrl() {
  // #ifdef H5
  window.open(note.value.source_url, '_blank')
  // #endif
  // #ifdef MP-WEIXIN
  uni.setClipboardData({ data: note.value.source_url })
  uni.showToast({ title: '链接已复制' })
  // #endif
}

function sourceLabel(type) {
  return { note: '笔记', url: '网页', pdf: 'PDF' }[type] || type
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #0f0f23;
  display: flex;
  flex-direction: column;
}

.content { padding: 32rpx; flex: 1; }

.note-meta {
  padding-bottom: 32rpx;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 32rpx;
}

.source-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.source-badge {
  font-size: 20rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;

  &.note { background: rgba(99,102,241,0.2); color: #a5b4fc; }
  &.url  { background: rgba(20,184,166,0.2); color: #5eead4; }
  &.pdf  { background: rgba(239,68,68,0.2);  color: #fca5a5; }
}

.source-url {
  font-size: 22rpx;
  color: #6366f1;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #f1f5f9;
  display: block;
  line-height: 1.4;
  margin-bottom: 20rpx;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.tag {
  font-size: 22rpx;
  border: 1px solid;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
}

.note-date {
  font-size: 22rpx;
  color: #475569;
  display: block;
}

.note-body {
  font-size: 28rpx;
  color: #cbd5e1;
  line-height: 1.9;
}

.empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
  font-size: 28rpx;
}

.bottom-bar {
  display: flex;
  justify-content: space-around;
  background: #1a1a2e;
  border-top: 1px solid rgba(255,255,255,0.08);
  padding: 20rpx 0;
}

.action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #94a3b8;

  .action-icon { font-size: 36rpx; }
  &.danger { color: #f87171; }
}
</style>
