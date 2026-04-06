<template>
  <view class="page">
    <view class="toolbar">
      <input
        v-model="title"
        class="title-input"
        placeholder="标题..."
        placeholder-style="color:#475569"
        maxlength="200"
      />
    </view>

    <!-- 富文本编辑器（uni-app 内置） -->
    <editor
      id="editor"
      class="editor"
      :read-only="false"
      placeholder="开始记录你的想法..."
      @input="onEditorInput"
      @ready="onEditorReady"
    />

    <!-- 标签选择 -->
    <view class="tag-section">
      <text class="section-label">标签</text>
      <scroll-view scroll-x>
        <view class="tag-list">
          <view
            v-for="tag in tags"
            :key="tag.id"
            :class="['tag-chip', selectedTagIds.includes(tag.id) && 'selected']"
            :style="selectedTagIds.includes(tag.id) ? `background:${tag.color}33;border-color:${tag.color}` : ''"
            @tap="toggleTag(tag.id)"
          >
            <text class="tag-dot" :style="`background:${tag.color}`" />
            {{ tag.name }}
          </view>
          <view class="tag-chip add-tag" @tap="addTag">+ 新建</view>
        </view>
      </scroll-view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar safe-area-bottom">
      <view class="format-tools">
        <text class="fmt-btn" @tap="format('bold')"><b>B</b></text>
        <text class="fmt-btn" @tap="format('italic')"><i>I</i></text>
        <text class="fmt-btn" @tap="format('insertOrderedList')">1.</text>
        <text class="fmt-btn" @tap="format('insertUnorderedList')">•</text>
        <text class="fmt-btn" @tap="format('formatBlock', 'h2')">H</text>
      </view>
      <button class="save-btn" :loading="saving" @tap="save">保存</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notesApi, tagsApi } from '@/api/index'

const props = defineProps({ id: String })

const title = ref('')
const content = ref('')
const contentText = ref('')
const tags = ref([])
const selectedTagIds = ref([])
const saving = ref(false)
let editorCtx = null

onMounted(async () => {
  tags.value = await tagsApi.list()
  if (props.id) {
    const note = await notesApi.get(props.id)
    title.value = note.title
    content.value = note.content
    selectedTagIds.value = note.tags.map(t => t.id)
  }
})

function onEditorReady() {
  uni.createSelectorQuery()
    .select('#editor')
    .context((res) => {
      editorCtx = res.context
      if (content.value) {
        editorCtx.setContents({ html: content.value })
      }
    })
    .exec()
}

function onEditorInput(e) {
  content.value = e.detail.html
  contentText.value = e.detail.text
}

function format(type, value) {
  editorCtx?.format(type, value)
}

function toggleTag(id) {
  const idx = selectedTagIds.value.indexOf(id)
  if (idx > -1) {
    selectedTagIds.value.splice(idx, 1)
  } else {
    selectedTagIds.value.push(id)
  }
}

function addTag() {
  uni.showModal({
    title: '新建标签',
    editable: true,
    placeholderText: '标签名称',
    success: async (res) => {
      if (res.confirm && res.content) {
        const tag = await tagsApi.create({ name: res.content })
        tags.value.push(tag)
        selectedTagIds.value.push(tag.id)
      }
    },
  })
}

async function save() {
  if (!title.value.trim()) {
    uni.showToast({ title: '请输入标题', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const payload = {
      title: title.value.trim(),
      content: content.value,
      content_text: contentText.value,
      tag_ids: selectedTagIds.value,
    }
    if (props.id) {
      await notesApi.update(props.id, payload)
    } else {
      await notesApi.create(payload)
    }
    uni.showToast({ title: '保存成功' })
    setTimeout(() => uni.navigateBack(), 500)
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
}

.toolbar {
  padding: 20rpx 30rpx;
  border-bottom: 1px solid var(--border);
  position: relative;
  z-index: 2;
  background: var(--bg-base);
}

.title-input {
  font-size: 36rpx;
  font-weight: 600;
  color: var(--text-1);
  background: transparent;
  width: 100%;
}

.editor {
  flex: 1;
  padding: 24rpx 30rpx;
  font-size: 28rpx;
  color: var(--text-1);
  line-height: 1.8;
  background: var(--bg-base);
}

.tag-section {
  padding: 16rpx 24rpx;
  border-top: 1px solid var(--border);

  .section-label {
    font-size: 22rpx;
    color: #475569;
    margin-bottom: 12rpx;
    display: block;
  }
}

.tag-list {
  display: flex;
  gap: 12rpx;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 100rpx;
  font-size: 24rpx;
  color: var(--text-3);
  white-space: nowrap;

  &.selected { color: var(--text-1); }
  &.add-tag { color: var(--accent-2); border-color: rgba(99,102,241,0.3); }
}

.tag-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  display: inline-block;
}

.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  background: var(--bg-surface);
  border-top: 1px solid var(--border);
}

.format-tools {
  display: flex;
  gap: 24rpx;
}

.fmt-btn {
  font-size: 30rpx;
  color: var(--text-3);
  padding: 8rpx 12rpx;
}

.save-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 28rpx;
  padding: 16rpx 40rpx;
  border-radius: 12rpx;
  border: none;
  &::after { border: none; }
}
</style>
