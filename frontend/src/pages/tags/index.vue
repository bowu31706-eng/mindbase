<template>
  <view class="page-root">
    <AppLayout current-page="tags">
      <view class="tags-page">
        <!-- Header -->
        <view class="page-header">
          <view class="header-left">
            <text class="page-title">标签管理</text>
            <text class="page-sub">{{ tags.length }} 个标签</text>
          </view>
          <view class="btn-add" @click="showAddModal = true">
            <text class="btn-add-icon">+</text>
            <text class="btn-add-label">新建标签</text>
          </view>
        </view>

        <!-- Loading -->
        <view v-if="loading" class="loading-wrap">
          <text class="loading-text">加载中...</text>
        </view>

        <!-- Empty -->
        <view v-else-if="!tags.length" class="empty-wrap">
          <text class="empty-icon">🏷️</text>
          <text class="empty-title">还没有标签</text>
          <text class="empty-sub">创建标签来整理你的知识库</text>
          <view class="btn-empty-add" @click="showAddModal = true">创建第一个标签</view>
        </view>

        <!-- Tag List -->
        <view v-else class="tag-list">
          <view v-for="tag in tags" :key="tag.id" class="tag-row">
            <!-- Color + Name -->
            <view class="tag-left">
              <view
                class="color-dot"
                :style="`background:${tag.color}`"
                @click="openColorPicker(tag)"
              />
              <view v-if="editingId === tag.id" class="name-edit-wrap">
                <input
                  v-model="editingName"
                  class="name-input"
                  @confirm="saveEdit(tag)"
                  @blur="saveEdit(tag)"
                  focus
                />
              </view>
              <text v-else class="tag-name" @click="startEdit(tag)">{{ tag.name }}</text>
            </view>

            <!-- Actions -->
            <view class="tag-actions">
              <view class="action-btn edit-btn" @click="startEdit(tag)">
                <text>✏️</text>
              </view>
              <view class="action-btn delete-btn" @click="deleteTag(tag)">
                <text>🗑️</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </AppLayout>

    <!-- Color Picker Overlay — 放在 AppLayout 外，position:fixed 不受父级 overflow 影响 -->
    <view v-if="colorPickerTag" class="overlay" @click="colorPickerTag = null">
      <view class="color-picker-card" @click.stop>
        <text class="picker-title">选择颜色</text>
        <view class="color-grid">
          <view
            v-for="c in PRESET_COLORS"
            :key="c"
            class="color-swatch"
            :class="colorPickerTag.color === c && 'selected'"
            :style="`background:${c}`"
            @click="applyColor(c)"
          />
        </view>
      </view>
    </view>

    <!-- Add Tag Modal -->
    <view v-if="showAddModal" class="overlay" @click="showAddModal = false">
      <view class="add-modal" @click.stop>
        <text class="modal-title">新建标签</text>
        <input
          v-model="newTagName"
          class="modal-input"
          placeholder="标签名称"
          placeholder-style="color:#94a3b8"
          @confirm="createTag"
          focus
        />
        <view class="color-row">
          <text class="color-row-label">颜色</text>
          <view class="color-grid">
            <view
              v-for="c in PRESET_COLORS"
              :key="c"
              class="color-swatch"
              :class="newTagColor === c && 'selected'"
              :style="`background:${c}`"
              @click="newTagColor = c"
            />
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn-cancel" @click="showAddModal = false">取消</button>
          <button class="btn-confirm" :loading="creating" @click="createTag">创建</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { tagsApi } from '@/api/index'

const PRESET_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#ef4444',
  '#f59e0b', '#10b981', '#14b8a6', '#3b82f6',
]

const tags    = ref([])
const loading = ref(true)

const editingId   = ref(null)
const editingName = ref('')

const colorPickerTag = ref(null)

const showAddModal = ref(false)
const newTagName   = ref('')
const newTagColor  = ref('#6366f1')
const creating     = ref(false)

onMounted(async () => {
  await loadTags()
})

async function loadTags() {
  loading.value = true
  try {
    tags.value = await tagsApi.list()
  } catch {}
  loading.value = false
}

function startEdit(tag) {
  editingId.value   = tag.id
  editingName.value = tag.name
}

async function saveEdit(tag) {
  if (!editingName.value.trim() || editingName.value.trim() === tag.name) {
    editingId.value = null
    return
  }
  try {
    await tagsApi.update(tag.id, { name: editingName.value.trim() })
    tag.name = editingName.value.trim()
  } catch {}
  editingId.value = null
}

function openColorPicker(tag) {
  colorPickerTag.value = tag
}

async function applyColor(color) {
  const tag = colorPickerTag.value
  if (!tag) return
  try {
    await tagsApi.update(tag.id, { color })
    tag.color = color
  } catch {}
  colorPickerTag.value = null
}

function deleteTag(tag) {
  uni.showModal({
    title: '删除标签',
    content: `确认删除「${tag.name}」？关联笔记的标签将被移除。`,
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        try {
          await tagsApi.delete(tag.id)
          tags.value = tags.value.filter(t => t.id !== tag.id)
          uni.showToast({ title: '已删除', icon: 'success' })
        } catch {}
      }
    },
  })
}

async function createTag() {
  if (!newTagName.value.trim()) {
    uni.showToast({ title: '请输入标签名称', icon: 'none' })
    return
  }
  creating.value = true
  try {
    const tag = await tagsApi.create({ name: newTagName.value.trim(), color: newTagColor.value })
    tags.value.push(tag)
    newTagName.value  = ''
    newTagColor.value = '#6366f1'
    showAddModal.value = false
    uni.showToast({ title: '创建成功', icon: 'success' })
  } catch {}
  creating.value = false
}
</script>

<style lang="scss" scoped>
.page-root {
  position: relative;
  height: 100vh;
}

.tags-page {
  padding: 28px 24px;
  max-width: 680px;
  margin: 0 auto;
  min-height: 100%;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.page-title { font-size: 22px; font-weight: 700; color: var(--text-1); }
.page-sub   { font-size: 13px; color: var(--text-3); }

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--accent);
  color: #fff;
  border-radius: var(--radius);
  cursor: pointer;
  transition: opacity 0.15s;

  &:hover { opacity: 0.88; }
  .btn-add-icon  { font-size: 18px; font-weight: 300; line-height: 1; }
  .btn-add-label { font-size: 13px; font-weight: 600; }
}

/* Loading / Empty */
.loading-wrap, .empty-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 10px;
}

.loading-text { font-size: 14px; color: var(--text-3); }
.empty-icon   { font-size: 48px; }
.empty-title  { font-size: 16px; font-weight: 600; color: var(--text-2); }
.empty-sub    { font-size: 13px; color: var(--text-3); }

.btn-empty-add {
  margin-top: 8px;
  padding: 9px 20px;
  background: var(--accent-bg);
  color: var(--accent-2);
  border: 1px solid rgba(99,102,241,0.25);
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

/* Tag List */
.tag-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  transition: box-shadow 0.15s;

  &:hover { box-shadow: var(--shadow-sm); }
}

.tag-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.15s;
  &:hover { transform: scale(1.3); }
}

.tag-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-1);
  cursor: pointer;
  &:hover { color: var(--accent-2); }
}

.name-edit-wrap { flex: 1; }
.name-input {
  width: 100%;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-1);
  background: var(--bg-input);
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  padding: 4px 10px;
}

.tag-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.action-btn {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: var(--bg-card-hover); }
}

/* Overlay */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  /* #ifdef H5 */
  backdrop-filter: blur(3px);
  /* #endif */
}

/* Color Picker */
.color-picker-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 20px;
  box-shadow: var(--shadow-lg);
}

.picker-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-1);
  margin-bottom: 14px;
  text-align: center;
}

.color-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.color-row {
  margin-top: 14px;
  .color-row-label {
    display: block;
    font-size: 12px;
    color: var(--text-3);
    margin-bottom: 8px;
  }
}

.color-swatch {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.15s;
  border: 2px solid transparent;

  &:hover    { transform: scale(1.15); }
  &.selected { border-color: var(--text-1); transform: scale(1.15); }
}

/* Add Modal */
.add-modal {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 22px 20px 18px;
  width: 100%;
  max-width: 360px;
  box-shadow: var(--shadow-lg);
}

.modal-title {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1);
  margin-bottom: 14px;
}

.modal-input {
  width: 100%;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-1);
  display: block;
  margin-bottom: 14px;
}

.modal-footer {
  display: flex;
  gap: 10px;
  margin-top: 16px;

  .btn-cancel, .btn-confirm {
    flex: 1;
    height: 38px;
    border-radius: var(--radius);
    font-size: 14px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    &::after { border: none; }
  }
  .btn-cancel  { background: var(--bg-input); color: var(--text-2); border: 1px solid var(--border); }
  .btn-confirm { background: var(--accent); color: #fff; }
}
</style>
