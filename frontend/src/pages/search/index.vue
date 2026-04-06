<template>
  <AppLayout current-page="search">
    <view class="search-page">
      <!-- ── Hero Search Bar ───────────────────────── -->
      <view class="search-hero">
        <text class="hero-title">语义搜索</text>
        <text class="hero-sub">在你的整个知识库中精准定位内容</text>
        <view class="search-box">
          <text class="sb-icon">🔍</text>
          <input
            v-model="query"
            class="sb-input"
            placeholder="输入关键词或描述，支持自然语言..."
            placeholder-style="color:var(--text-3)"
            confirm-type="search"
            @input="onInput"
            @confirm="doSearch"
          />
          <view v-if="query" class="sb-clear" @tap="clear">
            <text>✕</text>
          </view>
          <view
            :class="['sb-btn', query.trim() && 'active']"
            @tap="doSearch"
          >搜索</view>
        </view>
        <view class="search-tips">
          <text class="tip-label">试一试：</text>
          <view
            v-for="tip in quickTips"
            :key="tip"
            class="tip-chip"
            @tap="query = tip; doSearch()"
          >{{ tip }}</view>
        </view>
      </view>

      <!-- ── Results ──────────────────────────────── -->
      <view class="results-area">
        <!-- Idle hint -->
        <view v-if="!searched && !loading" class="idle-state">
          <view class="idle-cards">
            <view class="idle-card" v-for="c in idleCards" :key="c.title">
              <text class="ic-icon">{{ c.icon }}</text>
              <text class="ic-title">{{ c.title }}</text>
              <text class="ic-desc">{{ c.desc }}</text>
            </view>
          </view>
        </view>

        <!-- Loading -->
        <view v-if="loading" class="loading-state">
          <view class="loading-dots">
            <view class="ld" /><view class="ld" /><view class="ld" />
          </view>
          <text class="loading-label">正在搜索...</text>
        </view>

        <!-- No results -->
        <view v-if="searched && results.length === 0 && !loading" class="no-results">
          <text class="nr-icon">🔭</text>
          <text class="nr-title">没有找到相关内容</text>
          <text class="nr-sub">试试换个关键词，或者添加更多笔记到知识库</text>
        </view>

        <!-- Result Cards -->
        <view v-if="results.length > 0" class="results-header">
          <text class="results-count">找到 {{ results.length }} 条相关内容</text>
        </view>

        <view class="results-list">
          <view
            v-for="item in results"
            :key="item.note_id + (item.chunk_index || 0)"
            class="result-card"
            @tap="openNote(item.note_id)"
          >
            <view class="rc-header">
              <view :class="['rc-type', item.search_type]">
                {{ item.search_type === 'semantic' ? '🧠 语义' : '🔤 关键词' }}
              </view>
              <view v-if="item.score > 0" class="rc-score">
                <view class="score-bar">
                  <view class="score-fill" :style="`width:${Math.round(item.score * 100)}%`" />
                </view>
                <text class="score-pct">{{ Math.round(item.score * 100) }}%</text>
              </view>
            </view>

            <text class="rc-title">{{ item.note_title }}</text>

            <view class="rc-snippet-wrap">
              <text class="rc-snippet">{{ item.chunk_text?.slice(0, 140) }}</text>
              <text v-if="item.chunk_text?.length > 140" class="rc-more">...</text>
            </view>

            <view class="rc-footer">
              <text class="rc-open">查看笔记 →</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { searchApi } from '@/api/index'

const query    = ref('')
const results  = ref([])
const loading  = ref(false)
const searched = ref(false)
let timer = null

const quickTips = ['AI 相关内容', '最近学到的知识', '编程技巧']

const idleCards = [
  { icon: '🧠', title: '语义搜索',   desc: '理解语义，不只是关键词匹配' },
  { icon: '🔤', title: '关键词搜索', desc: '精准查找特定词语或短语' },
  { icon: '📊', title: '相关度排序', desc: '按相关程度展示最匹配的内容' },
]

function onInput() {
  clearTimeout(timer)
  if (query.value.trim().length >= 2) {
    timer = setTimeout(doSearch, 700)
  }
}

async function doSearch() {
  if (!query.value.trim()) return
  clearTimeout(timer)
  loading.value = true
  searched.value = true
  try {
    results.value = await searchApi.search(query.value.trim())
  } finally {
    loading.value = false
  }
}

function clear() {
  query.value   = ''
  results.value = []
  searched.value= false
}

function openNote(id) {
  uni.navigateTo({ url: `/pages/note/detail?id=${id}` })
}
</script>

<style lang="scss" scoped>
.search-page {
  min-height: 100%;
  padding-bottom: 40px;
}

/* ── Hero Section ─────────────────────────────────── */
.search-hero {
  padding: 32px 20px 24px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
}

.hero-title { display: block; font-size: 22px; font-weight: 800; color: var(--text-1); margin-bottom: 4px; }
.hero-sub   { display: block; font-size: 13px; color: var(--text-3); margin-bottom: 20px; }

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-input);
  border: 1.5px solid var(--border-strong);
  border-radius: var(--radius-xl);
  padding: 12px 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 14px;

  &:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-bg);
  }

  .sb-icon  { font-size: 18px; flex-shrink: 0; }
  .sb-input { flex: 1; font-size: 15px; color: var(--text-1); height: 24px; }
  .sb-clear {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--bg-card-hover);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    color: var(--text-3);
    cursor: pointer;
    flex-shrink: 0;
  }
  .sb-btn {
    padding: 7px 16px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-3);
    background: var(--bg-card);
    border: 1px solid var(--border);
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.15s;

    &.active {
      background: var(--accent);
      color: #fff;
      border-color: transparent;
      box-shadow: 0 2px 10px var(--accent-glow);
    }
  }
}

.search-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;

  .tip-label { font-size: 12px; color: var(--text-3); }
  .tip-chip  {
    font-size: 12px;
    padding: 5px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 100px;
    color: var(--text-2);
    cursor: pointer;
    transition: all 0.15s;

    &:hover { border-color: var(--accent); color: var(--accent-2); }
    &:active { opacity: 0.7; }
  }
}

/* ── Results Area ─────────────────────────────────── */
.results-area { padding: 20px; }

/* Idle State */
.idle-state { padding: 8px 0 20px; }

.idle-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;

  @media (max-width: 500px) { grid-template-columns: 1fr; }
}

.idle-card {
  padding: 18px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  text-align: center;

  .ic-icon  { display: block; font-size: 28px; margin-bottom: 8px; }
  .ic-title { display: block; font-size: 13px; font-weight: 600; color: var(--text-1); margin-bottom: 4px; }
  .ic-desc  { display: block; font-size: 12px; color: var(--text-3); line-height: 1.5; }
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
}

.loading-dots {
  display: flex;
  gap: 8px;

  .ld {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--accent);
    animation: ld-bounce 1.2s infinite;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes ld-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
  30%            { transform: translateY(-8px); opacity: 1; }
}

.loading-label { font-size: 13px; color: var(--text-3); }

/* No Results */
.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 60px 20px;
  gap: 10px;

  .nr-icon  { font-size: 48px; }
  .nr-title { font-size: 16px; font-weight: 600; color: var(--text-1); }
  .nr-sub   { font-size: 13px; color: var(--text-3); max-width: 260px; line-height: 1.6; }
}

/* Results Header */
.results-header {
  margin-bottom: 14px;
  .results-count { font-size: 13px; color: var(--text-3); font-weight: 500; }
}

/* Result Card */
.results-list { display: flex; flex-direction: column; gap: 12px; }

.result-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 16px 18px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-strong);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }
  &:active { transform: scale(0.99); opacity: 0.85; }
}

.rc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.rc-type {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;

  &.semantic { background: var(--accent-bg); color: var(--accent-2); }
  &.keyword  { background: rgba(20,184,166,0.12); color: #2dd4bf; }
}

.rc-score {
  display: flex;
  align-items: center;
  gap: 6px;

  .score-bar {
    width: 60px;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }
  .score-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #8b5cf6);
    border-radius: 2px;
  }
  .score-pct { font-size: 11px; color: var(--text-3); }
}

.rc-title {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-1);
  margin-bottom: 6px;
}

.rc-snippet-wrap {
  display: flex;
  margin-bottom: 10px;

  .rc-snippet {
    font-size: 13px;
    color: var(--text-2);
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.rc-footer {
  .rc-open { font-size: 12px; color: var(--accent-2); font-weight: 500; }
}
</style>
