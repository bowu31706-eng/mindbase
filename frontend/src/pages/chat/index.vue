<template>
  <AppLayout current-page="chat">
    <view class="chat-page">
      <!-- Conversation List Sidebar (desktop) -->
      <view class="conv-sidebar">
        <view class="cs-header">
          <text class="cs-title">对话历史</text>
          <view class="cs-new-btn" @tap="newConversation">
            <text>+ 新对话</text>
          </view>
        </view>
        <scroll-view scroll-y class="cs-list">
          <view v-if="conversations.length === 0" class="cs-empty">
            <text>暂无历史对话</text>
          </view>
          <view
            v-for="conv in conversations"
            :key="conv.id"
            :class="['cs-item', conv.id === conversationId && 'active']"
            @tap="switchConversation(conv.id)"
          >
            <text class="cs-item-title">{{ conv.title || '新对话' }}</text>
            <text class="cs-item-preview">{{ (conv.last_message || '').slice(0, 28) }}</text>
          </view>
        </scroll-view>
      </view>

      <!-- Chat Main Area -->
      <view class="chat-main">
        <!-- Top Bar (mobile) -->
        <view class="chat-topbar">
          <text class="ct-label">💬 AI 问答</text>
          <view class="ct-actions">
            <view class="ct-btn" @tap="showHistoryPanel = true">历史</view>
            <view class="ct-btn ct-new" @tap="newConversation">新对话</view>
          </view>
        </view>

        <!-- Messages -->
        <scroll-view
          scroll-y
          :scroll-top="scrollTop"
          class="messages"
          :scroll-with-animation="true"
        >
          <!-- Welcome Screen -->
          <view v-if="messages.length === 0" class="welcome">
            <view class="welcome-icon">🤖</view>
            <text class="welcome-title">向你的知识库提问</text>
            <text class="welcome-sub">基于你保存的笔记、网页、PDF 进行智能回答</text>
            <view class="suggestions-grid">
              <view
                v-for="s in suggestions"
                :key="s"
                class="suggestion-card"
                @tap="sendMessage(s)"
              >
                <text class="sg-icon">💡</text>
                <text class="sg-text">{{ s }}</text>
              </view>
            </view>
          </view>

          <!-- Message Bubbles -->
          <view
            v-for="msg in messages"
            :key="msg.id || msg._id"
            :class="['msg-row', msg.role]"
          >
            <view v-if="msg.role === 'assistant'" class="msg-avatar">🤖</view>
            <view class="msg-bubble">
              <text class="msg-text">{{ msg.content }}</text>
              <!-- Sources -->
              <view v-if="msg.sources?.length" class="sources-block">
                <text class="sources-title">📎 参考来源</text>
                <view
                  v-for="src in msg.sources"
                  :key="src.note_id"
                  class="source-chip"
                  @tap="openNote(src.note_id)"
                >
                  <text class="source-chip-text">{{ src.note_title }}</text>
                  <text class="source-chip-arrow">›</text>
                </view>
              </view>
            </view>
            <view v-if="msg.role === 'user'" class="msg-user-avatar">
              <text>{{ userInitial }}</text>
            </view>
          </view>

          <!-- Thinking Animation -->
          <view v-if="thinking" class="msg-row assistant">
            <view class="msg-avatar">🤖</view>
            <view class="msg-bubble thinking-bubble">
              <view class="dot" /><view class="dot" /><view class="dot" />
            </view>
          </view>

          <!-- Scroll anchor -->
          <view class="scroll-anchor" />
        </scroll-view>

        <!-- Input Area -->
        <view class="input-zone safe-area-bottom">
          <view class="input-row">
            <textarea
              v-model="inputText"
              class="chat-input"
              placeholder="问问你的知识库..."
              placeholder-style="color:var(--text-3)"
              :auto-height="true"
              :max-height="120"
              @confirm="onSend"
              @keydown="handleKeydown"
            />
            <view
              :class="['send-btn', inputText.trim() && 'ready']"
              @tap="onSend"
            >
              <text class="send-icon">↑</text>
            </view>
          </view>
          <text class="input-hint">AI 回答基于你的个人知识库</text>
        </view>
      </view>
    </view>

    <!-- Mobile History Overlay -->
    <view v-if="showHistoryPanel" class="history-overlay" @tap="showHistoryPanel = false">
      <view class="history-sheet" @tap.stop>
        <view class="sheet-handle" />
        <text class="sheet-title">历史对话</text>
        <view class="sheet-new-btn" @tap="newConversation(); showHistoryPanel = false">
          + 新对话
        </view>
        <scroll-view scroll-y style="max-height: 55vh">
          <view
            v-for="conv in conversations"
            :key="conv.id"
            :class="['sheet-item', conv.id === conversationId && 'active']"
            @tap="switchConversation(conv.id); showHistoryPanel = false"
          >
            <text class="sheet-item-title">{{ conv.title || '新对话' }}</text>
            <text class="sheet-item-preview">{{ (conv.last_message || '').slice(0, 40) }}</text>
          </view>
          <view v-if="conversations.length === 0" class="sheet-empty">暂无历史</view>
        </scroll-view>
      </view>
    </view>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { chatApi } from '@/api/index'
import { useUserStore } from '@/store/user'

const userStore   = useUserStore()
const userInitial = computed(() => (userStore.user?.nickname?.[0] ?? 'U').toUpperCase())

const messages        = ref([])
const inputText       = ref('')
const thinking        = ref(false)
const conversationId  = ref(null)
const conversations   = ref([])
const showHistoryPanel= ref(false)
const scrollTop       = ref(0)

const suggestions = [
  '我保存了哪些关于 AI 的内容？',
  '帮我总结最近保存的笔记',
  '我有哪些关于编程的资料？',
  '知识库里有什么学习资源？',
]

onMounted(() => loadConversations())

async function loadConversations() {
  conversations.value = await chatApi.listConversations()
}

async function switchConversation(id) {
  conversationId.value = id
  const msgs = await chatApi.getMessages(id)
  messages.value = msgs
  scrollToBottom()
}

function newConversation() {
  conversationId.value = null
  messages.value = []
  showHistoryPanel.value = false
}

async function onSend() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return
  await sendMessage(text)
}

function handleKeydown(e) {
  // Enter without Shift = send; Shift+Enter = newline
  if (e.keyCode === 13 && !e.shiftKey) {
    e.preventDefault()
    onSend()
  }
}

async function sendMessage(text) {
  inputText.value = ''
  messages.value.push({ _id: Date.now(), role: 'user', content: text })
  scrollToBottom()

  thinking.value = true
  try {
    const res = await chatApi.chat({
      conversation_id: conversationId.value,
      message: text,
    })
    conversationId.value = res.conversation_id
    messages.value.push({
      _id: res.message_id,
      role: 'assistant',
      content: res.answer,
      sources: res.sources,
    })
    await loadConversations()
    scrollToBottom()
  } finally {
    thinking.value = false
  }
}

function openNote(id) {
  uni.navigateTo({ url: `/pages/note/detail?id=${id}` })
}

function scrollToBottom() {
  nextTick(() => { scrollTop.value = 999999 })
}
</script>

<style lang="scss" scoped>
/* ── Chat Page Layout ─────────────────────────────── */
.chat-page {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* ── Conversation Sidebar (desktop only) ──────────── */
.conv-sidebar {
  display: none;
  width: 220px;
  min-width: 220px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  flex-direction: column;

  @media (min-width: 768px) { display: flex; }
}

.cs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--border);

  .cs-title  { font-size: 13px; font-weight: 700; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.5px; }

  .cs-new-btn {
    font-size: 12px;
    color: var(--accent-2);
    padding: 5px 10px;
    border: 1px solid var(--accent);
    border-radius: 20px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.15s;

    &:hover { background: var(--accent-bg); }
  }
}

.cs-list { flex: 1; padding: 8px; }

.cs-empty { padding: 24px 8px; font-size: 13px; color: var(--text-3); text-align: center; }

.cs-item {
  padding: 10px 12px;
  border-radius: var(--radius);
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.15s;

  &:hover { background: var(--bg-card-hover); }
  &.active { background: var(--accent-bg); }

  .cs-item-title   { display: block; font-size: 13px; font-weight: 500; color: var(--text-1); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cs-item-preview { display: block; font-size: 11px; color: var(--text-3); margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
}

/* ── Chat Main ────────────────────────────────────── */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Top Bar (mobile) */
.chat-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-surface);
  flex-shrink: 0;

  .ct-label  { font-size: 15px; font-weight: 600; color: var(--text-1); }
  .ct-actions{ display: flex; gap: 8px; }
  .ct-btn {
    font-size: 12px;
    color: var(--text-2);
    padding: 6px 12px;
    border: 1px solid var(--border);
    border-radius: 20px;
    cursor: pointer;
    background: var(--bg-card);

    &.ct-new {
      color: var(--accent-2);
      border-color: var(--accent);
      background: var(--accent-bg);
      font-weight: 500;
    }
  }

  @media (min-width: 768px) { display: none; }
}

/* Messages */
.messages {
  flex: 1;
  padding: 20px 16px;
}

/* Welcome */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 16px;
  gap: 10px;
}

.welcome-icon  { font-size: 52px; margin-bottom: 4px; }
.welcome-title { font-size: 18px; font-weight: 700; color: var(--text-1); }
.welcome-sub   { font-size: 14px; color: var(--text-3); max-width: 280px; line-height: 1.6; }

.suggestions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 16px;
  width: 100%;
  max-width: 440px;
}

.suggestion-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;

  &:hover { background: var(--bg-card-hover); border-color: var(--accent); }
  &:active { opacity: 0.7; }

  .sg-icon { font-size: 16px; flex-shrink: 0; }
  .sg-text { font-size: 13px; color: var(--text-2); line-height: 1.5; }
}

/* Message Row */
.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-bottom: 18px;

  &.user      { flex-direction: row-reverse; }
  &.assistant { flex-direction: row; }
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-bg);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.msg-user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 72%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.7;

  .msg-row.user & {
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    color: #fff;
    border-bottom-right-radius: 5px;
  }

  .msg-row.assistant & {
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text-1);
    border-bottom-left-radius: 5px;
  }
}

.msg-text { display: block; white-space: pre-wrap; word-break: break-word; }

/* Sources */
.sources-block {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.12);

  .sources-title {
    display: block;
    font-size: 11px;
    color: rgba(255,255,255,0.55);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;

    .msg-row.user & { color: rgba(255,255,255,0.55); }
    .msg-row.assistant & { color: var(--text-3); }
  }
}

.source-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: rgba(255,255,255,0.08);
  border-radius: var(--radius-sm);
  margin-bottom: 5px;
  cursor: pointer;

  .source-chip-text  { font-size: 12px; color: var(--accent-2); }
  .source-chip-arrow { font-size: 14px; color: var(--text-3); }

  &:hover { background: rgba(255,255,255,0.12); }
}

/* Thinking */
.thinking-bubble {
  display: flex !important;
  gap: 6px;
  padding: 14px 18px !important;

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    animation: thinking-bounce 1.3s infinite;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes thinking-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
  30%            { transform: translateY(-6px); opacity: 1; }
}

.scroll-anchor { height: 20px; }

/* ── Input Zone ───────────────────────────────────── */
.input-zone {
  background: var(--bg-surface);
  border-top: 1px solid var(--border);
  padding: 12px 16px 10px;
  flex-shrink: 0;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.chat-input {
  flex: 1;
  background: var(--bg-input);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-xl);
  padding: 12px 18px;
  font-size: 14px;
  color: var(--text-1);
  min-height: 46px;
  transition: border-color 0.2s;

  &:focus { border-color: var(--accent); }
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.2s;

  &.ready {
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    border-color: transparent;
    box-shadow: 0 3px 14px var(--accent-glow);
  }

  .send-icon { font-size: 18px; color: #fff; font-weight: 700; }
  &:active { transform: scale(0.93); }
}

.input-hint {
  display: block;
  text-align: center;
  font-size: 11px;
  color: var(--text-4);
  margin-top: 8px;
}

/* ── Mobile History Overlay ───────────────────────── */
.history-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  z-index: 200;
  display: flex;
  align-items: flex-end;
}

.history-sheet {
  width: 100%;
  background: var(--bg-surface);
  border-radius: 20px 20px 0 0;
  padding: 16px 20px 32px;
  max-height: 75vh;

  .sheet-handle {
    width: 40px;
    height: 4px;
    background: var(--border-strong);
    border-radius: 2px;
    margin: 0 auto 16px;
  }

  .sheet-title {
    display: block;
    font-size: 16px;
    font-weight: 700;
    color: var(--text-1);
    margin-bottom: 12px;
  }

  .sheet-new-btn {
    display: block;
    text-align: center;
    padding: 10px;
    border: 1px solid var(--accent);
    border-radius: var(--radius-lg);
    color: var(--accent-2);
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 12px;
    cursor: pointer;
  }
}

.sheet-item {
  padding: 12px 14px;
  border-radius: var(--radius);
  cursor: pointer;
  margin-bottom: 6px;
  transition: background 0.15s;

  &:hover { background: var(--bg-card-hover); }
  &.active { background: var(--accent-bg); }

  .sheet-item-title   { display: block; font-size: 14px; font-weight: 500; color: var(--text-1); }
  .sheet-item-preview { display: block; font-size: 12px; color: var(--text-3); margin-top: 3px; }
}

.sheet-empty { text-align: center; padding: 30px; font-size: 13px; color: var(--text-3); }
</style>
