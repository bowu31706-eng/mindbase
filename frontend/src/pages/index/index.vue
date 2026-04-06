<template>
  <AppLayout current-page="index">
    <view class="home">
      <view class="home-inner">

        <!-- ── Animated Icon ─────────────────────────── -->
        <view class="hero-icon-wrap">
          <view class="icon-pulse r1" />
          <view class="icon-pulse r2" />
          <view class="icon-circle">
            <svg class="icon-svg" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path class="wave-a"
                d="M10 28 C14 18 22 18 24 24 C26 30 34 30 38 20"
                stroke="#6366f1" stroke-width="2.2" stroke-linecap="round"/>
              <path class="wave-b"
                d="M8 35 C13 27 19 27 24 31 C29 35 35 29 40 23"
                stroke="#a5b4fc" stroke-width="1.5" stroke-linecap="round" opacity="0.55"/>
              <circle class="dot-a" cx="10" cy="28" r="2.2" fill="#6366f1"/>
              <circle class="dot-b" cx="24" cy="24" r="2.2" fill="#8b5cf6"/>
              <circle class="dot-c" cx="38" cy="20" r="2.2" fill="#6366f1"/>
            </svg>
          </view>
        </view>

        <!-- ── Title ──────────────────────────────────── -->
        <text class="hero-title">知识的第二大脑</text>

        <!-- ── Input Card ─────────────────────────────── -->
        <view class="input-card">
          <input
            v-model="queryText"
            class="ic-input"
            placeholder="搜索笔记，或向知识库提问…"
            placeholder-style="color:#b0b7c3;font-size:15px"
            confirm-type="search"
            @confirm="handleQuery"
          />
          <view class="ic-toolbar">
            <view class="ic-actions-left">
              <view class="tb-icon-btn" @tap="createNote">
                <text class="tib-text">+</text>
              </view>
              <view class="tb-icon-btn" @tap="goSearch">
                <text class="tib-text tib-search">⌕</text>
              </view>
            </view>
            <view class="ic-actions-right">
              <view :class="['tb-send', queryText.trim() ? 'active' : '']" @tap="handleQuery">
                <text class="send-arrow">↑</text>
              </view>
            </view>
          </view>
        </view>

        <!-- ── Tag chips ──────────────────────────────── -->
        <view class="tag-row" v-if="tags.length > 0">
          <text class="tag-row-label">标签</text>
          <scroll-view scroll-x class="tag-scroll" :show-scrollbar="false">
            <view class="tag-chips">
              <view
                v-for="tag in tags.slice(0, 6)"
                :key="tag.id"
                class="tag-chip"
                @tap="goSearch"
              >
                <view class="chip-dot" :style="`background:${tag.color}`" />
                <text class="chip-text">{{ tag.name }}</text>
              </view>
            </view>
          </scroll-view>
        </view>

        <!-- ── Quick Actions ──────────────────────────── -->
        <view class="quick-section" v-if="showActions">
          <view class="qs-head">
            <text class="qs-title">快速开始</text>
            <text class="qs-dismiss" @tap="showActions = false">×</text>
          </view>
          <view class="qs-grid">
            <view class="qs-card" @tap="createNote">
              <view class="qsc-icon-wrap">
                <text class="qsc-emoji">✏️</text>
              </view>
              <text class="qsc-name">写一篇笔记</text>
              <text class="qsc-desc">记录想法与灵感</text>
            </view>
            <view class="qs-card" @tap="importUrl">
              <view class="qsc-icon-wrap">
                <text class="qsc-emoji">🔗</text>
              </view>
              <text class="qsc-name">导入网页</text>
              <text class="qsc-desc">保存任意 URL 内容</text>
            </view>
            <view class="qs-card" @tap="importPdf">
              <view class="qsc-icon-wrap">
                <text class="qsc-emoji">📄</text>
              </view>
              <text class="qsc-name">上传 PDF</text>
              <text class="qsc-desc">解析文档自动入库</text>
            </view>
            <view class="qs-card" @tap="goChat">
              <view class="qsc-icon-wrap">
                <text class="qsc-emoji">💬</text>
              </view>
              <text class="qsc-name">AI 问答</text>
              <text class="qsc-desc">向知识库直接提问</text>
            </view>
          </view>
        </view>

        <!-- ── Recent Notes ────────────────────────────── -->
        <view class="recent-section" v-if="notes.length > 0">
          <view class="rs-head">
            <text class="rs-title">最近笔记</text>
            <text class="rs-all" @tap="showActions = true">快速操作</text>
          </view>
          <view class="recent-list">
            <view
              v-for="note in notes.slice(0, 5)"
              :key="note.id"
              class="recent-item"
              @tap="openNote(note.id)"
            >
              <view :class="['ri-dot', note.source_type || 'note']" />
              <view class="ri-body">
                <text class="ri-title">{{ note.title }}</text>
                <text class="ri-time">{{ formatDate(note.updated_at) }}</text>
              </view>
              <text class="ri-chevron">›</text>
            </view>
          </view>
        </view>

        <!-- ── Empty hint ─────────────────────────────── -->
        <view class="empty-hint" v-if="!loading && notes.length === 0 && !showActions">
          <text class="eh-btn" @tap="showActions = true">开始使用 →</text>
        </view>

      </view>
    </view>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { notesApi, tagsApi } from '@/api/index'

const notes       = ref([])
const tags        = ref([])
const loading     = ref(false)
const queryText   = ref('')
const showActions = ref(true)

onMounted(async () => {
  await Promise.all([loadTags(), loadNotes()])
})

async function loadTags() {
  try { tags.value = await tagsApi.list() } catch {}
}

async function loadNotes() {
  loading.value = true
  try {
    notes.value = await notesApi.list({ limit: 20, offset: 0 })
    if (notes.value.length > 0) showActions.value = false
  } finally {
    loading.value = false
  }
}

function handleQuery() {
  if (!queryText.value.trim()) return
  uni.switchTab({ url: '/pages/search/index', fail: () => uni.reLaunch({ url: '/pages/search/index' }) })
}

function goSearch() {
  uni.switchTab({ url: '/pages/search/index', fail: () => uni.reLaunch({ url: '/pages/search/index' }) })
}

function goChat() {
  uni.switchTab({ url: '/pages/chat/index', fail: () => uni.reLaunch({ url: '/pages/chat/index' }) })
}

function createNote() {
  uni.navigateTo({ url: '/pages/note/edit' })
}

function openNote(id) {
  uni.navigateTo({ url: `/pages/note/detail?id=${id}` })
}

function importUrl() {
  uni.showModal({
    title: '导入网页', editable: true, placeholderText: '请输入网址',
    success: async (res) => {
      if (res.confirm && res.content) {
        uni.showLoading({ title: '抓取中...' })
        try { await notesApi.fromUrl(res.content); await loadNotes(); uni.showToast({ title: '导入成功' }) }
        finally { uni.hideLoading() }
      }
    },
  })
}

function importPdf() {
  uni.chooseFile({
    count: 1,
    type: 'file',
    extension: ['.pdf'],
    success: async (res) => {
      uni.showLoading({ title: '解析中...' })
      try {
        await notesApi.fromPdf(res.tempFilePaths[0])
        await loadNotes()
        uni.showToast({ title: '导入成功' })
      } catch {
        uni.showToast({ title: '导入失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
  })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr), now = new Date(), diff = now - d
  if (diff < 60000)    return '刚刚'
  if (diff < 3600000)  return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}月${d.getDate()}日`
}
</script>

<style lang="scss" scoped>
/* ── Outer shell ──────────────────────────────────── */
.home {
  min-height: 100%;
  background: var(--bg-base);
  display: flex;
  justify-content: center;
  padding: 0 24px 80px;
}

.home-inner {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 64px;

  @media (min-width: 768px) { padding-top: 90px; }
}

/* ── Animated hero icon ───────────────────────────── */
.hero-icon-wrap {
  position: relative;
  margin-bottom: 28px;
  animation: float 5s ease-in-out infinite;
}

@keyframes float {
  0%,100% { transform: translateY(0); }
  50%      { transform: translateY(-10px); }
}

/* Pulsing outer rings */
.icon-pulse {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(99,102,241,0.25);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 3s ease-out infinite;

  &.r1 { width: 96px;  height: 96px;  animation-delay: 0s; }
  &.r2 { width: 116px; height: 116px; animation-delay: 0.9s; }
}

@keyframes pulse {
  0%   { opacity: 0.8; transform: scale(0.86); }
  70%  { opacity: 0.1; transform: scale(1); }
  100% { opacity: 0; }
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.icon-svg {
  width: 38px;
  height: 38px;
}

/* SVG path animations */
.wave-a {
  stroke-dasharray: 65;
  stroke-dashoffset: 65;
  animation: draw 1.8s cubic-bezier(0.4,0,0.2,1) 0.3s forwards;
}

.wave-b {
  stroke-dasharray: 75;
  stroke-dashoffset: 75;
  animation: draw 2.2s cubic-bezier(0.4,0,0.2,1) 0.6s forwards;
}

@keyframes draw {
  to { stroke-dashoffset: 0; }
}

.dot-a, .dot-b, .dot-c {
  opacity: 0;
  animation: pop 0.35s ease forwards;
}

.dot-a { animation-delay: 1.9s; }
.dot-b { animation-delay: 2.1s; }
.dot-c { animation-delay: 2.3s; }

@keyframes pop {
  0%   { opacity: 0; transform: scale(0); }
  70%  { opacity: 1; transform: scale(1.3); }
  100% { opacity: 1; transform: scale(1); }
}

/* ── Hero title ───────────────────────────────────── */
.hero-title {
  font-size: 30px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.5px;
  text-align: center;
  margin-bottom: 32px;
  display: block;

  @media (min-width: 768px) { font-size: 36px; }
}

/* ── Input card ───────────────────────────────────── */
.input-card {
  width: 100%;
  background: var(--bg-surface);
  border: 1.5px solid var(--border);
  border-radius: 16px;
  padding: 16px 16px 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05), 0 4px 20px rgba(0,0,0,0.04);
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 16px;
}

.input-card:focus-within {
  border-color: rgba(99,102,241,0.4);
  box-shadow: 0 0 0 4px rgba(99,102,241,0.07);
}

.ic-input {
  width: 100%;
  font-size: 15px;
  color: var(--text-1);
  background: transparent;
  min-height: 26px;
  display: block;
  margin-bottom: 12px;
}

.ic-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ic-actions-left, .ic-actions-right {
  display: flex;
  align-items: center;
  gap: 2px;
}

.tb-icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: var(--bg-card-hover); }
  &:active { opacity: 0.6; }

  .tib-text {
    font-size: 20px;
    color: var(--text-3);
    line-height: 1;
    font-weight: 300;
  }

  .tib-search { font-size: 18px; }
}

.tb-send {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--bg-card-hover);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s;

  .send-arrow {
    font-size: 15px;
    color: var(--text-3);
    font-weight: 600;
    line-height: 1;
    display: block;
  }

  &.active {
    background: var(--accent);
    border-color: transparent;
    box-shadow: 0 2px 10px var(--accent-glow);

    .send-arrow { color: #fff; }
  }

  &:active { transform: scale(0.9); }
}

/* ── Tag row ──────────────────────────────────────── */
.tag-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
}

.tag-row-label {
  font-size: 12px;
  color: var(--text-3);
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-scroll { overflow: hidden; flex: 1; }

.tag-chips {
  display: flex;
  gap: 6px;
  white-space: nowrap;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 100px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover { border-color: var(--accent); background: var(--accent-bg); }
  &:active { opacity: 0.7; }

  .chip-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
  .chip-text { font-size: 12px; color: var(--text-2); font-weight: 500; }
}

/* ── Quick Actions ────────────────────────────────── */
.quick-section { width: 100%; margin-bottom: 28px; }

.qs-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;

  .qs-title { font-size: 13px; font-weight: 600; color: var(--text-2); }
  .qs-dismiss {
    font-size: 18px;
    color: var(--text-3);
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
    transition: color 0.15s;

    &:hover { color: var(--text-1); }
  }
}

.qs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.qs-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px 14px 13px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    border-color: var(--border-strong);
    background: var(--bg-card-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }
  &:active { transform: scale(0.98); opacity: 0.8; }
}

.qsc-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--bg-base);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;

  .qsc-emoji { font-size: 16px; }
}

.qsc-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
  margin-bottom: 3px;
}

.qsc-desc {
  display: block;
  font-size: 11px;
  color: var(--text-3);
  line-height: 1.5;
}

/* ── Recent Notes ─────────────────────────────────── */
.recent-section { width: 100%; }

.rs-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;

  .rs-title { font-size: 13px; font-weight: 600; color: var(--text-2); }
  .rs-all   { font-size: 12px; color: var(--text-3); cursor: pointer; transition: color 0.15s; &:hover { color: var(--accent); } }
}

.recent-list { display: flex; flex-direction: column; }

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  user-select: none;

  &:hover { background: var(--bg-card-hover); }
  &:active { opacity: 0.65; }
}

.ri-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.note { background: #6366f1; }
  &.url  { background: #14b8a6; }
  &.pdf  { background: #ef4444; }
}

.ri-body { flex: 1; overflow: hidden; }

.ri-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ri-time {
  display: block;
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
}

.ri-chevron {
  font-size: 18px;
  color: var(--text-4);
  flex-shrink: 0;
  line-height: 1;
}

/* ── Empty hint ───────────────────────────────────── */
.empty-hint {
  margin-top: 8px;
  display: flex;
  justify-content: center;
}

.eh-btn {
  padding: 9px 24px;
  border: 1px solid var(--border-strong);
  border-radius: 100px;
  font-size: 13px;
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.15s;
  display: block;

  &:hover {
    background: var(--accent);
    color: #fff;
    border-color: transparent;
    box-shadow: 0 3px 12px var(--accent-glow);
  }
}
</style>
