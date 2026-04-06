<template>
  <view class="app-layout">
    <!-- ── Desktop Sidebar ──────────────────────────── -->
    <view class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Brand -->
      <view class="sidebar-brand">
        <view class="brand-logo">🧠</view>
        <text class="brand-name">MindBase</text>
      </view>

      <!-- Scrollable nav content -->
      <scroll-view class="sidebar-scroll" scroll-y>
        <!-- Group 1: Main Navigation -->
        <view class="nav-group">
          <view
            v-for="item in mainNavItems"
            :key="item.key"
            :class="['nav-item', currentPage === item.key && 'active']"
            @tap="navigate(item)"
          >
            <text class="nav-icon">{{ item.icon }}</text>
            <text class="nav-label">{{ item.label }}</text>
            <view v-if="currentPage === item.key" class="active-dot" />
          </view>
        </view>

        <view class="nav-divider" />

        <!-- Group 2: Tools -->
        <view class="nav-group">
          <text class="nav-group-label">工具</text>
          <view
            v-for="item in toolNavItems"
            :key="item.key"
            :class="['nav-item', currentPage === item.key && 'active']"
            @tap="navigate(item)"
          >
            <text class="nav-icon">{{ item.icon }}</text>
            <text class="nav-label">{{ item.label }}</text>
            <view v-if="currentPage === item.key" class="active-dot" />
          </view>
        </view>

        <view class="nav-divider" />

        <!-- Group 3: Quick Actions -->
        <view class="nav-group">
          <text class="nav-group-label">快捷操作</text>

          <!-- 快速导入 -->
          <view class="nav-item" @tap="showImportModal = true">
            <text class="nav-icon">📥</text>
            <text class="nav-label">快速导入</text>
          </view>

          <!-- 最近浏览 -->
          <view class="nav-item" @tap="toggleRecent">
            <text class="nav-icon">🕐</text>
            <text class="nav-label">最近浏览</text>
            <text v-if="!sidebarCollapsed" class="expand-icon">{{ recentExpanded ? '▾' : '›' }}</text>
          </view>
          <view v-if="recentExpanded && !sidebarCollapsed" class="recent-list">
            <view v-if="recentLoading" class="recent-placeholder">加载中...</view>
            <template v-else>
              <view
                v-for="note in recentNotes"
                :key="note.id"
                class="recent-item"
                @tap="openNote(note.id)"
              >
                <text class="recent-title">{{ note.title }}</text>
                <text class="recent-date">{{ formatRecent(note.updated_at) }}</text>
              </view>
              <view v-if="!recentNotes.length" class="recent-placeholder">暂无笔记</view>
            </template>
          </view>
        </view>

        <view class="nav-divider" />

        <!-- Group 4: Settings -->
        <view class="nav-group">
          <view
            :class="['nav-item', currentPage === 'profile' && 'active']"
            @tap="navigate({ key: 'profile', icon: '⚙️', label: '个人中心', path: '/pages/profile/index', isTab: true })"
          >
            <text class="nav-icon">⚙️</text>
            <text class="nav-label">个人中心</text>
            <view v-if="currentPage === 'profile'" class="active-dot" />
          </view>
        </view>
      </scroll-view>

      <!-- Footer: User Info -->
      <view class="sidebar-footer">
        <view class="avatar-chip">{{ userInitial }}</view>
        <view class="user-details">
          <text class="user-name">{{ userName }}</text>
          <text class="user-email">{{ userEmail }}</text>
        </view>
      </view>

      <!-- Collapse Toggle -->
      <view class="collapse-btn" @tap="sidebarCollapsed = !sidebarCollapsed">
        <text>{{ sidebarCollapsed ? '›' : '‹' }}</text>
      </view>
    </view>

    <!-- ── Main Content Area ──────────────────────── -->
    <view class="main-area">
      <!-- Mobile Header -->
      <view class="mobile-header safe-area-top">
        <view class="mobile-brand">
          <text class="mobile-brand-icon">🧠</text>
          <text class="mobile-brand-text">{{ currentTitle }}</text>
        </view>
      </view>

      <!-- Page Slot -->
      <view class="content-area">
        <slot />
      </view>

      <!-- Mobile Bottom Navigation -->
      <view class="bottom-nav safe-area-bottom">
        <view
          v-for="item in mobileNavItems"
          :key="item.key"
          :class="['bottom-nav-item', currentPage === item.key && 'active']"
          @tap="navigate(item)"
        >
          <text class="bottom-icon">{{ item.icon }}</text>
          <text class="bottom-label">{{ item.label }}</text>
        </view>
      </view>
    </view>

    <!-- ── Import Modal ────────────────────────────── -->
    <view v-if="showImportModal" class="modal-overlay" @tap="closeImportModal">
      <view class="modal-card" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">快速导入</text>
          <view class="modal-close" @tap="closeImportModal">✕</view>
        </view>

        <view class="modal-tabs">
          <view
            :class="['modal-tab', importTab === 'url' && 'active']"
            @tap="importTab = 'url'"
          >🌐 网页 URL</view>
          <view
            :class="['modal-tab', importTab === 'pdf' && 'active']"
            @tap="importTab = 'pdf'"
          >📄 PDF 文件</view>
        </view>

        <!-- URL Panel -->
        <view v-if="importTab === 'url'" class="modal-panel">
          <input
            v-model="importUrl"
            class="modal-input"
            placeholder="https://..."
            placeholder-style="color:#94a3b8"
          />
          <text class="modal-hint">自动提取正文并生成 AI 标签</text>
        </view>

        <!-- PDF Panel -->
        <view v-if="importTab === 'pdf'" class="modal-panel">
          <view class="pdf-upload-area" @tap="pickPdf">
            <text class="pdf-icon">📄</text>
            <text class="pdf-text">{{ pdfName || '点击选择 PDF 文件' }}</text>
            <text class="pdf-hint">支持最大 20MB</text>
          </view>
        </view>

        <!-- Status -->
        <view v-if="importStatus" :class="['import-status', importStatus.type]">
          {{ importStatus.msg }}
        </view>

        <view class="modal-footer">
          <button class="btn-cancel" @tap="closeImportModal">取消</button>
          <button
            class="btn-confirm"
            :loading="importing"
            :disabled="importing"
            @tap="doImport"
          >{{ importing ? '导入中...' : '开始导入' }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { notesApi } from '@/api/index'

const props = defineProps({
  currentPage: { type: String, default: 'index' },
})

const userStore        = useUserStore()
const sidebarCollapsed = ref(false)

const mainNavItems = [
  { key: 'index',  icon: '🏠', label: '知识库', path: '/pages/index/index',  isTab: true },
  { key: 'chat',   icon: '💬', label: 'AI 问答', path: '/pages/chat/index',   isTab: true },
  { key: 'search', icon: '🔍', label: '搜索',   path: '/pages/search/index', isTab: true },
]

const toolNavItems = [
  { key: 'tags',      icon: '🏷️', label: '标签管理', path: '/pages/tags/index' },
  { key: 'stats',     icon: '📊', label: '统计洞察', path: '/pages/stats/index' },
  { key: 'favorites', icon: '⭐', label: '收藏',     path: '/pages/favorites/index' },
  { key: 'trash',     icon: '🗑️', label: '回收站',   path: '/pages/trash/index' },
]

const mobileNavItems = [
  { key: 'index',   icon: '🏠', label: '知识库', path: '/pages/index/index',   isTab: true },
  { key: 'chat',    icon: '💬', label: '问答',   path: '/pages/chat/index',    isTab: true },
  { key: 'search',  icon: '🔍', label: '搜索',   path: '/pages/search/index',  isTab: true },
  { key: 'profile', icon: '👤', label: '我的',   path: '/pages/profile/index', isTab: true },
]

const allNavItems = [...mainNavItems, ...toolNavItems, { key: 'profile', label: '个人中心' }]
const currentTitle = computed(() =>
  allNavItems.find(i => i.key === props.currentPage)?.label ?? 'MindBase'
)

const userName    = computed(() => userStore.user?.nickname || '用户')
const userEmail   = computed(() => userStore.user?.email || '')
const userInitial = computed(() => (userName.value[0] ?? 'U').toUpperCase())

function navigate(item) {
  if (item.isTab) {
    uni.switchTab({ url: item.path, fail: () => uni.reLaunch({ url: item.path }) })
  } else {
    uni.navigateTo({ url: item.path })
  }
}

// ── Recent Notes ──────────────────────────────────
const recentExpanded = ref(false)
const recentNotes    = ref([])
const recentLoading  = ref(false)

async function toggleRecent() {
  recentExpanded.value = !recentExpanded.value
  if (recentExpanded.value && !recentNotes.value.length) {
    recentLoading.value = true
    try {
      const res = await notesApi.list({ limit: 5 })
      recentNotes.value = res
    } catch {}
    recentLoading.value = false
  }
}

function openNote(id) {
  uni.navigateTo({ url: `/pages/note/detail?id=${id}` })
}

function formatRecent(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 3600)  return `${Math.max(1, Math.floor(diff / 60))}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

// ── Import Modal ──────────────────────────────────
const showImportModal = ref(false)
const importTab       = ref('url')
const importUrl       = ref('')
const pdfFilePath     = ref('')
const pdfName         = ref('')
const importing       = ref(false)
const importStatus    = ref(null)

function closeImportModal() {
  showImportModal.value = false
  importUrl.value   = ''
  pdfFilePath.value = ''
  pdfName.value     = ''
  importStatus.value = null
  importing.value   = false
}

function pickPdf() {
  uni.chooseFile({
    count: 1,
    type: 'file',
    extension: ['.pdf'],
    success: (res) => {
      pdfFilePath.value = res.tempFilePaths[0]
      pdfName.value     = res.tempFiles[0]?.name || 'document.pdf'
    },
  })
}

async function doImport() {
  importing.value    = true
  importStatus.value = null
  try {
    if (importTab.value === 'url') {
      if (!importUrl.value.trim()) {
        importStatus.value = { type: 'error', msg: '请输入网页地址' }
        return
      }
      await notesApi.fromUrl(importUrl.value.trim())
      importStatus.value = { type: 'success', msg: '✓ 导入成功，已保存到知识库' }
      recentNotes.value  = []
      setTimeout(closeImportModal, 1500)
    } else {
      if (!pdfFilePath.value) {
        importStatus.value = { type: 'error', msg: '请选择 PDF 文件' }
        return
      }
      await notesApi.fromPdf(pdfFilePath.value)
      importStatus.value = { type: 'success', msg: '✓ PDF 解析成功，已保存' }
      recentNotes.value  = []
      setTimeout(closeImportModal, 1500)
    }
  } catch {
    importStatus.value = { type: 'error', msg: '导入失败，请检查内容后重试' }
  } finally {
    importing.value = false
  }
}
</script>

<style lang="scss" scoped>
/* ── Layout Shell ─────────────────────────────────── */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-base);
  position: relative;
}

/* ── Sidebar ──────────────────────────────────────── */
.sidebar {
  display: none;
  width: 220px;
  min-width: 220px;
  flex-direction: column;
  background: var(--sidebar-bg);
  flex-shrink: 0;
  position: relative;
  z-index: 5;
  transition: width 0.25s ease, min-width 0.25s ease;

  &.collapsed {
    width: 60px;
    min-width: 60px;

    .brand-name, .nav-label, .nav-group-label,
    .expand-icon, .recent-list, .user-details, .active-dot {
      display: none;
    }
    .nav-item     { justify-content: center; padding: 10px; }
    .sidebar-footer { justify-content: center; }
  }
}

@media (min-width: 768px) {
  .sidebar { display: flex; }
}

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  flex-shrink: 0;

  .brand-logo { font-size: 24px; flex-shrink: 0; }
  .brand-name {
    font-size: 16px;
    font-weight: 700;
    color: var(--sidebar-text);
    letter-spacing: 0.3px;
    white-space: nowrap;
  }
}

/* Scrollable nav */
.sidebar-scroll {
  flex: 1;
  overflow-x: hidden;
}

/* Nav Group */
.nav-group {
  padding: 6px 8px;
}

.nav-group-label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  color: rgba(30,41,59,0.35);
  padding: 6px 10px 4px;
  white-space: nowrap;
}

.nav-divider {
  height: 1px;
  background: rgba(0,0,0,0.07);
  margin: 2px 8px;
}

/* Nav Item */
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  transition: background 0.15s;

  .nav-icon  { font-size: 15px; flex-shrink: 0; line-height: 1; }
  .nav-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--sidebar-text-muted);
    white-space: nowrap;
    flex: 1;
    transition: color 0.15s;
  }
  .expand-icon { font-size: 11px; color: rgba(30,41,59,0.3); flex-shrink: 0; }
  .active-dot  {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
  }

  &:hover {
    background: rgba(0,0,0,0.05);
    .nav-label { color: var(--sidebar-text); }
  }

  &.active {
    background: rgba(99,102,241,0.12);
    .nav-label { color: var(--accent-2); font-weight: 600; }
  }
}

/* Recent Notes Inline List */
.recent-list {
  padding: 2px 0 4px 32px;
}

.recent-placeholder {
  font-size: 11px;
  color: rgba(30,41,59,0.3);
  padding: 4px 10px;
}

.recent-item {
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: rgba(255,255,255,0.05); }

  .recent-title {
    display: block;
    font-size: 11.5px;
    color: rgba(30,41,59,0.6);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 140px;
  }
  .recent-date {
    display: block;
    font-size: 10px;
    color: rgba(30,41,59,0.3);
    margin-top: 1px;
  }
}

/* Sidebar Footer */
.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-top: 1px solid rgba(0,0,0,0.07);
  flex-shrink: 0;

  .avatar-chip {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
  }
  .user-name  {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--sidebar-text);
    white-space: nowrap;
  }
  .user-email {
    display: block;
    font-size: 10px;
    color: var(--sidebar-text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 148px;
  }
}

/* Collapse Button */
.collapse-btn {
  position: absolute;
  top: 50%;
  right: -12px;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f5f0e8;
  border: 1px solid rgba(0,0,0,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  z-index: 20;
  transition: all 0.15s;

  &:hover { background: #ede8de; color: var(--accent); }
}

/* ── Main Area ────────────────────────────────────── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-base);
  min-width: 0;
}

/* Mobile Header */
.mobile-header {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  background: var(--header-bg);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;

  .mobile-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    .mobile-brand-icon { font-size: 22px; }
    .mobile-brand-text { font-size: 17px; font-weight: 700; color: var(--text-1); }
  }
}

@media (min-width: 768px) {
  .mobile-header { display: none; }
}

/* Content Area */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

/* Mobile Bottom Nav */
.bottom-nav {
  display: flex;
  background: var(--header-bg);
  border-top: 1px solid var(--border);
  flex-shrink: 0;

  .bottom-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding: 10px 4px;
    cursor: pointer;
    transition: all 0.15s;

    .bottom-icon  { font-size: 21px; line-height: 1; transition: transform 0.15s; }
    .bottom-label { font-size: 10px; color: var(--text-3); font-weight: 500; transition: color 0.15s; }

    &.active {
      .bottom-icon  { transform: translateY(-2px); }
      .bottom-label { color: var(--accent-2); font-weight: 600; }
    }
    &:active { opacity: 0.7; }
  }
}

@media (min-width: 768px) {
  .bottom-nav { display: none; }
}

/* ── Import Modal ─────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  /* #ifdef H5 */
  backdrop-filter: blur(4px);
  /* #endif */
}

.modal-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 440px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border);

  .modal-title { font-size: 15px; font-weight: 700; color: var(--text-1); }
  .modal-close {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: var(--bg-input);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    color: var(--text-3);
    cursor: pointer;
    transition: background 0.15s;
    &:hover { background: var(--border); }
  }
}

.modal-tabs {
  display: flex;
  padding: 12px 16px 0;
  gap: 6px;

  .modal-tab {
    flex: 1;
    text-align: center;
    padding: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-3);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.15s;

    &:hover { background: var(--bg-card-hover); color: var(--text-2); }
    &.active { background: var(--accent-bg); color: var(--accent-2); font-weight: 600; }
  }
}

.modal-panel { padding: 14px 20px; }

.modal-input {
  width: 100%;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 11px 14px;
  font-size: 14px;
  color: var(--text-1);
  display: block;
}

.modal-hint { display: block; font-size: 12px; color: var(--text-3); margin-top: 7px; }

.pdf-upload-area {
  border: 2px dashed var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;

  &:hover { border-color: var(--accent); background: var(--accent-bg); }

  .pdf-icon { font-size: 30px; }
  .pdf-text { font-size: 14px; color: var(--text-2); font-weight: 500; }
  .pdf-hint { font-size: 11px; color: var(--text-3); }
}

.import-status {
  margin: 0 20px 6px;
  padding: 9px 14px;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;

  &.success {
    background: rgba(16,185,129,0.09);
    color: #059669;
    border: 1px solid rgba(16,185,129,0.18);
  }
  &.error {
    background: rgba(239,68,68,0.07);
    color: #dc2626;
    border: 1px solid rgba(239,68,68,0.14);
  }
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 10px 20px 18px;

  .btn-cancel, .btn-confirm {
    flex: 1;
    height: 40px;
    border-radius: var(--radius);
    font-size: 14px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.15s;
    &::after { border: none; }
  }

  .btn-cancel {
    background: var(--bg-input);
    color: var(--text-2);
    border: 1px solid var(--border);
    &:hover { background: var(--bg-card-hover); }
  }

  .btn-confirm {
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    color: #fff;
    &[disabled] { opacity: 0.5; }
  }
}
</style>
