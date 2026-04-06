<template>
  <view class="page">
    <view v-if="note" class="content">
      <view class="note-meta">
        <view :class="['source-badge', note.source_type]">
          {{ sourceLabel(note.source_type) }}
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
      </view>
      <rich-text class="note-body" :nodes="note.content" />
    </view>

    <view class="footer">
      <text class="footer-brand">🧠 MindBase — 构建你的 AI 知识库</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notesApi } from '@/api/index'

const props = defineProps({ slug: String })
const note = ref(null)

onMounted(async () => {
  note.value = await notesApi.getPublic(props.slug)
  if (note.value) {
    uni.setNavigationBarTitle({ title: note.value.title })
  }
})

function sourceLabel(type) {
  return { note: '笔记', url: '网页', pdf: 'PDF' }[type] || type
}
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; background: #0f0f23; padding: 32rpx; }
.note-meta { margin-bottom: 32rpx; }
.source-badge {
  display: inline-block;
  font-size: 20rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  margin-bottom: 16rpx;
  &.note { background: rgba(99,102,241,0.2); color: #a5b4fc; }
  &.url  { background: rgba(20,184,166,0.2); color: #5eead4; }
  &.pdf  { background: rgba(239,68,68,0.2);  color: #fca5a5; }
}
.note-title { font-size: 40rpx; font-weight: 700; color: #f1f5f9; display: block; margin-bottom: 20rpx; }
.tag-row { display: flex; flex-wrap: wrap; gap: 12rpx; }
.tag { font-size: 22rpx; border: 1px solid; padding: 4rpx 14rpx; border-radius: 8rpx; }
.note-body { font-size: 28rpx; color: #cbd5e1; line-height: 1.9; }
.footer { text-align: center; padding: 60rpx 0 32rpx; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 60rpx; }
.footer-brand { font-size: 24rpx; color: #334155; }
</style>
