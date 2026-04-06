<template>
  <AppLayout current-page="profile">
    <view class="profile-page">
      <!-- ── User Hero Card ────────────────────────── -->
      <view class="user-hero">
        <view class="avatar-ring">
          <view class="avatar-large">{{ userInitial }}</view>
        </view>
        <text class="hero-name">{{ user?.nickname || '用户' }}</text>
        <text class="hero-email">{{ user?.email }}</text>
        <view class="hero-badge">
          <text class="badge-icon">🧠</text>
          <text class="badge-text">知识库成员</text>
        </view>
      </view>

      <!-- ── Stats ─────────────────────────────────── -->
      <view class="stats-section">
        <view class="stats-grid">
          <view class="stat-block" v-for="s in statsItems" :key="s.label">
            <text class="sb-num">{{ s.value }}</text>
            <text class="sb-icon">{{ s.icon }}</text>
            <text class="sb-label">{{ s.label }}</text>
          </view>
        </view>
      </view>

      <!-- ── Menu Sections ─────────────────────────── -->
      <view class="menu-section">
        <text class="menu-section-title">知识管理</text>
        <view class="menu-card">
          <view class="menu-item" @tap="goTags">
            <view class="mi-left">
              <view class="mi-icon-wrap mi-purple">🏷️</view>
              <view class="mi-text">
                <text class="mi-label">标签管理</text>
                <text class="mi-sub">管理你的知识分类标签</text>
              </view>
            </view>
            <text class="mi-arrow">›</text>
          </view>
          <view class="menu-divider" />
          <view class="menu-item" @tap="goImport">
            <view class="mi-left">
              <view class="mi-icon-wrap mi-teal">📥</view>
              <view class="mi-text">
                <text class="mi-label">导入内容</text>
                <text class="mi-sub">批量导入网页或 PDF</text>
              </view>
            </view>
            <text class="mi-arrow">›</text>
          </view>
        </view>
      </view>

      <view class="menu-section">
        <text class="menu-section-title">分享与协作</text>
        <view class="menu-card">
          <view class="menu-item" @tap="shareKb">
            <view class="mi-left">
              <view class="mi-icon-wrap mi-amber">🔗</view>
              <view class="mi-text">
                <text class="mi-label">分享知识库</text>
                <text class="mi-sub">生成公开链接分享笔记</text>
              </view>
            </view>
            <view class="mi-badge-soon">即将上线</view>
          </view>
        </view>
      </view>

      <view class="menu-section">
        <text class="menu-section-title">账号与设置</text>
        <view class="menu-card">
          <view class="menu-item" @tap="logout">
            <view class="mi-left">
              <view class="mi-icon-wrap mi-red">🚪</view>
              <view class="mi-text">
                <text class="mi-label mi-danger">退出登录</text>
                <text class="mi-sub">退出后需要重新登录</text>
              </view>
            </view>
            <text class="mi-arrow mi-danger">›</text>
          </view>
        </view>
      </view>

      <!-- Footer -->
      <view class="profile-footer">
        <text class="footer-logo">🧠 MindBase</text>
        <text class="footer-ver">v1.0.0 · 让知识变得更有价值</text>
      </view>
    </view>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useUserStore } from '@/store/user'
import { notesApi, tagsApi, chatApi } from '@/api/index'

const userStore = useUserStore()

const user        = computed(() => userStore.user)
const userInitial = computed(() => (user.value?.nickname?.[0] ?? 'U').toUpperCase())

const statValues = ref({ notes: '-', tags: '-', chats: '-' })

const statsItems = computed(() => [
  { icon: '📝', value: statValues.value.notes, label: '篇笔记' },
  { icon: '🏷️', value: statValues.value.tags,  label: '个标签' },
  { icon: '💬', value: statValues.value.chats, label: '次对话' },
])

onMounted(async () => {
  try {
    const [notes, tags, conversations] = await Promise.all([
      notesApi.list({ limit: 100 }),
      tagsApi.list(),
      chatApi.listConversations(),
    ])
    statValues.value = {
      notes: notes.length,
      tags:  tags.length,
      chats: conversations.length,
    }
  } catch {}
})

function goTags() {
  uni.navigateTo({ url: '/pages/tags/index' })
}

function goImport() {
  uni.switchTab({ url: '/pages/index/index', fail: () => uni.reLaunch({ url: '/pages/index/index' }) })
}

function shareKb() {
  uni.showToast({ title: '即将上线，敬请期待', icon: 'none' })
}

function logout() {
  uni.showModal({
    title: '确认退出',
    content: '退出后需要重新登录',
    success: (res) => { if (res.confirm) userStore.logout() },
  })
}
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100%;
  padding-bottom: 60px;
}

/* ── User Hero ────────────────────────────────────── */
.user-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 36px 20px 28px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  text-align: center;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 80px;
    background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.1) 100%);
  }
}

.avatar-ring {
  position: relative;
  z-index: 1;
  padding: 3px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  margin-bottom: 14px;
}

.avatar-large {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--bg-base);
  border: 3px solid var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 800;
  color: var(--accent-2);
}

.hero-name  { font-size: 20px; font-weight: 700; color: var(--text-1); display: block; margin-bottom: 4px; }
.hero-email { font-size: 13px; color: var(--text-3); display: block; margin-bottom: 14px; }

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  background: var(--accent-bg);
  border: 1px solid rgba(99,102,241,0.25);
  border-radius: 100px;

  .badge-icon { font-size: 13px; }
  .badge-text { font-size: 12px; color: var(--accent-2); font-weight: 500; }
}

/* ── Stats Grid ───────────────────────────────────── */
.stats-section { padding: 20px; }

.stats-grid {
  display: flex;
  gap: 12px;
}

.stat-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 18px 10px;
  text-align: center;

  .sb-num   { font-size: 26px; font-weight: 800; color: var(--accent-2); line-height: 1; }
  .sb-icon  { font-size: 18px; }
  .sb-label { font-size: 11px; color: var(--text-3); }
}

/* ── Menu Section ─────────────────────────────────── */
.menu-section { padding: 0 20px 16px; }

.menu-section-title {
  display: block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-3);
  margin-bottom: 8px;
  padding-left: 4px;
}

.menu-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: var(--bg-card-hover); }
  &:active { opacity: 0.7; }

  .mi-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.mi-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.mi-purple { background: rgba(99,102,241,0.15); }
.mi-teal   { background: rgba(20,184,166,0.15); }
.mi-amber  { background: rgba(245,158,11,0.15); }
.mi-blue   { background: rgba(59,130,246,0.15); }
.mi-red    { background: rgba(239,68,68,0.12); }

.mi-label { display: block; font-size: 14px; font-weight: 500; color: var(--text-1); }
.mi-sub   { display: block; font-size: 12px; color: var(--text-3); margin-top: 2px; }
.mi-arrow { font-size: 18px; color: var(--text-3); }
.mi-danger { color: #f87171 !important; }

.mi-badge-soon {
  font-size: 11px;
  padding: 3px 9px;
  background: rgba(245,158,11,0.12);
  color: #fbbf24;
  border-radius: 6px;
  font-weight: 500;
}

.menu-divider {
  height: 1px;
  background: var(--border);
  margin: 0 16px;
}

/* ── Footer ───────────────────────────────────────── */
.profile-footer {
  text-align: center;
  padding: 32px 20px 20px;

  .footer-logo { display: block; font-size: 16px; font-weight: 700; color: var(--text-3); margin-bottom: 4px; }
  .footer-ver  { display: block; font-size: 12px; color: var(--text-4); }
}
</style>
