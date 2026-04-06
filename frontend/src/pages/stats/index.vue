<template>
  <AppLayout current-page="stats">
    <view class="stats-page">
      <view class="page-header">
        <text class="page-title">统计洞察</text>
        <text class="page-sub">{{ subtitle }}</text>
      </view>

      <!-- Loading -->
      <view v-if="loading" class="loading-wrap">
        <text class="loading-text">加载数据中...</text>
      </view>

      <template v-else>
        <!-- Summary Cards -->
        <view class="summary-grid">
          <view class="summary-card" v-for="s in summaryCards" :key="s.label">
            <text class="sc-icon">{{ s.icon }}</text>
            <text class="sc-num">{{ s.value }}</text>
            <text class="sc-label">{{ s.label }}</text>
          </view>
        </view>

        <!-- Notes by Type -->
        <view class="section-card">
          <text class="section-title">笔记来源分布</text>
          <view class="bar-list">
            <view v-for="item in notesByType" :key="item.label" class="bar-row">
              <view class="bar-meta">
                <text class="bar-label">{{ item.icon }} {{ item.label }}</text>
                <text class="bar-count">{{ item.count }} 篇</text>
              </view>
              <view class="bar-track">
                <view
                  class="bar-fill"
                  :style="`width:${item.pct}%; background:${item.color}`"
                />
              </view>
            </view>
          </view>
        </view>

        <!-- Top Tags -->
        <view class="section-card" v-if="topTags.length">
          <text class="section-title">热门标签 Top {{ topTags.length }}</text>
          <view class="bar-list">
            <view v-for="item in topTags" :key="item.name" class="bar-row">
              <view class="bar-meta">
                <view class="bar-label-wrap">
                  <view class="tag-dot" :style="`background:${item.color}`" />
                  <text class="bar-label">{{ item.name }}</text>
                </view>
                <text class="bar-count">{{ item.count }} 篇</text>
              </view>
              <view class="bar-track">
                <view
                  class="bar-fill"
                  :style="`width:${item.pct}%; background:${item.color || '#6366f1'}`"
                />
              </view>
            </view>
          </view>
        </view>

        <!-- 7-day Activity -->
        <view class="section-card">
          <text class="section-title">最近 7 天新增</text>
          <view class="day-chart">
            <view v-for="day in weekActivity" :key="day.label" class="day-col">
              <text class="day-count">{{ day.count || '' }}</text>
              <view class="day-bar-wrap">
                <view
                  class="day-bar"
                  :style="`height:${day.pct}%`"
                  :class="day.count > 0 && 'has-data'"
                />
              </view>
              <text class="day-label">{{ day.label }}</text>
            </view>
          </view>
        </view>
      </template>
    </view>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { notesApi, tagsApi, chatApi } from '@/api/index'

const loading   = ref(true)
const allNotes  = ref([])
const allTags   = ref([])
const convCount = ref(0)

onMounted(async () => {
  try {
    const [notes, tags, convs] = await Promise.all([
      notesApi.list({ limit: 500 }),
      tagsApi.list(),
      chatApi.listConversations(),
    ])
    allNotes.value  = notes
    allTags.value   = tags
    convCount.value = convs.length
  } catch {}
  loading.value = false
})

const subtitle = computed(() => {
  if (loading.value) return ''
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 更新`
})

const summaryCards = computed(() => [
  { icon: '📝', value: allNotes.value.length, label: '篇笔记' },
  { icon: '🏷️', value: allTags.value.length,  label: '个标签' },
  { icon: '💬', value: convCount.value,        label: '次对话' },
  { icon: '⭐', value: allNotes.value.filter(n => n.is_starred).length, label: '已收藏' },
])

const notesByType = computed(() => {
  const total = allNotes.value.length || 1
  const counts = { note: 0, url: 0, pdf: 0 }
  allNotes.value.forEach(n => { counts[n.source_type] = (counts[n.source_type] || 0) + 1 })
  return [
    { label: '手动笔记', icon: '✏️', count: counts.note, color: '#6366f1', pct: Math.round(counts.note / total * 100) },
    { label: '网页抓取', icon: '🌐', count: counts.url,  color: '#14b8a6', pct: Math.round(counts.url  / total * 100) },
    { label: 'PDF 解析', icon: '📄', count: counts.pdf,  color: '#f59e0b', pct: Math.round(counts.pdf  / total * 100) },
  ]
})

const topTags = computed(() => {
  const countMap = {}
  const colorMap = {}
  allNotes.value.forEach(note => {
    ;(note.tags || []).forEach(tag => {
      countMap[tag.name] = (countMap[tag.name] || 0) + 1
      colorMap[tag.name] = tag.color
    })
  })
  const sorted = Object.entries(countMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
  const maxCount = sorted[0]?.[1] || 1
  return sorted.map(([name, count]) => ({
    name,
    count,
    color: colorMap[name] || '#6366f1',
    pct: Math.round(count / maxCount * 100),
  }))
})

const weekActivity = computed(() => {
  const days = []
  const DAY_LABELS = ['日', '一', '二', '三', '四', '五', '六']
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
    days.push({ label: DAY_LABELS[d.getDay()], key, count: 0 })
  }
  allNotes.value.forEach(note => {
    const d = new Date(note.created_at)
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
    const day = days.find(x => x.key === key)
    if (day) day.count++
  })
  const maxCount = Math.max(...days.map(d => d.count), 1)
  return days.map(d => ({ ...d, pct: Math.round(d.count / maxCount * 100) }))
})
</script>

<style lang="scss" scoped>
.stats-page {
  padding: 28px 24px;
  max-width: 720px;
  margin: 0 auto;
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.page-title { font-size: 22px; font-weight: 700; color: var(--text-1); }
.page-sub   { font-size: 13px; color: var(--text-3); }

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 60px;
}
.loading-text { font-size: 14px; color: var(--text-3); }

/* Summary Cards */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

@media (max-width: 600px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
}

.summary-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;

  .sc-icon  { font-size: 24px; }
  .sc-num   { font-size: 28px; font-weight: 800; color: var(--accent-2); line-height: 1; }
  .sc-label { font-size: 11px; color: var(--text-3); }
}

/* Section Card */
.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 20px;
  margin-bottom: 16px;
}

.section-title {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-1);
  margin-bottom: 18px;
}

/* Bar Chart */
.bar-list { display: flex; flex-direction: column; gap: 14px; }

.bar-row {}

.bar-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.bar-label-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bar-label { font-size: 13px; font-weight: 500; color: var(--text-2); }
.bar-count { font-size: 12px; color: var(--text-3); font-weight: 600; }

.bar-track {
  height: 7px;
  background: var(--bg-input);
  border-radius: 100px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 100px;
  min-width: 4px;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 7-day Chart */
.day-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 100px;
}

.day-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
}

.day-count {
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-2);
  min-height: 16px;
  display: block;
}

.day-bar-wrap {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
}

.day-bar {
  width: 100%;
  background: var(--bg-input);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  transition: height 0.5s ease;

  &.has-data { background: linear-gradient(180deg, var(--accent), #8b5cf6); }
}

.day-label {
  font-size: 11px;
  color: var(--text-3);
  display: block;
}
</style>
