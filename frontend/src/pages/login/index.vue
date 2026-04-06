<template>
  <view class="login-page">
    <!-- Theme Toggle -->
    <view class="theme-toggle" @tap="themeStore.toggle()">
      <text>{{ isDark ? '☀️' : '🌙' }}</text>
    </view>

    <!-- Left Panel: Branding (desktop only) -->
    <view class="brand-panel">
      <view class="brand-inner">
        <view class="brand-logo">🧠</view>
        <text class="brand-title">MindBase</text>
        <text class="brand-tagline">把知识变成可以对话的第二大脑</text>
        <view class="feature-list">
          <view class="feature-item" v-for="f in features" :key="f.text">
            <text class="f-icon">{{ f.icon }}</text>
            <text class="f-text">{{ f.text }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Right Panel: Form -->
    <view class="form-panel">
      <view class="form-inner">
        <!-- Mobile brand (only visible on mobile) -->
        <view class="mobile-brand">
          <view class="mobile-logo">🧠</view>
          <text class="mobile-title">MindBase</text>
          <text class="mobile-sub">把知识变成可以对话的第二大脑</text>
        </view>

        <!-- Tab Bar -->
        <view class="tab-bar">
          <view
            :class="['tab', mode === 'login' && 'active']"
            @tap="mode = 'login'"
          >登录</view>
          <view
            :class="['tab', mode === 'register' && 'active']"
            @tap="mode = 'register'"
          >注册</view>
        </view>

        <!-- Form Fields -->
        <view class="fields">
          <view v-if="mode === 'register'" class="field">
            <text class="field-label">昵称</text>
            <input
              v-model="form.nickname"
              class="field-input"
              placeholder="你的昵称"
              placeholder-style="color:var(--text-3)"
            />
          </view>

          <view class="field">
            <text class="field-label">邮箱</text>
            <input
              v-model="form.email"
              class="field-input"
              type="email"
              placeholder="your@email.com"
              placeholder-style="color:var(--text-3)"
            />
          </view>

          <view class="field">
            <text class="field-label">密码</text>
            <input
              v-model="form.password"
              class="field-input"
              type="password"
              placeholder="至少 8 位"
              placeholder-style="color:var(--text-3)"
            />
          </view>
        </view>

        <!-- Submit -->
        <button class="submit-btn" :loading="loading" @tap="submit">
          {{ mode === 'login' ? '登录' : '创建账号' }}
        </button>

        <!-- WeChat (mp only) -->
        <button
          v-if="isMP"
          class="wechat-btn"
          open-type="getPhoneNumber"
          @tap="wechatLogin"
        >
          <text>微信一键登录</text>
        </button>

        <text class="footer-hint">
          {{ mode === 'login' ? '没有账号？' : '已有账号？' }}
          <text
            class="footer-link"
            @tap="mode = mode === 'login' ? 'register' : 'login'"
          >{{ mode === 'login' ? '立即注册' : '去登录' }}</text>
        </text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'

const userStore  = useUserStore()
const themeStore = useThemeStore()
const isDark     = computed(() => themeStore.isDark)

const mode    = ref('login')
const loading = ref(false)
const form    = ref({ email: '', password: '', nickname: '' })

// #ifdef MP-WEIXIN
const isMP = true
// #endif
// #ifndef MP-WEIXIN
const isMP = false
// #endif

const features = [
  { icon: '✍️', text: '笔记、网页、PDF 一站式管理' },
  { icon: '🔍', text: '语义搜索，找到真正需要的内容' },
  { icon: '💬', text: 'AI 问答，与知识库直接对话' },
  { icon: '🏷️', text: '智能标签，自动分类整理' },
]

async function submit() {
  if (!form.value.email || !form.value.password) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }
  loading.value = true
  try {
    if (mode.value === 'login') {
      await userStore.login(form.value.email, form.value.password)
    } else {
      if (!form.value.nickname) {
        uni.showToast({ title: '请填写昵称', icon: 'none' })
        return
      }
      await userStore.register(form.value.email, form.value.password, form.value.nickname)
    }
    uni.reLaunch({ url: '/pages/index/index' })
  } catch (e) {
    uni.showToast({ title: e?.message || '操作失败，请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function wechatLogin() {
  loading.value = true
  try {
    await userStore.wechatLogin()
    uni.reLaunch({ url: '/pages/index/index' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: var(--bg-base);
  position: relative;
}

/* ── Theme Toggle ─────────────────────────────────── */
.theme-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}

/* ── Brand Panel (desktop left) ───────────────────── */
.brand-panel {
  display: none;
  flex: 1;
  background: var(--sidebar-bg);
  border-right: 1px solid rgba(255,255,255,0.06);
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
}

@media (min-width: 768px) {
  .brand-panel { display: flex; }
}

.brand-inner {
  position: relative;
  z-index: 1;
  text-align: center;
}

.brand-logo {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
}

.brand-title {
  display: block;
  font-size: 36px;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.5px;
  margin-bottom: 12px;
}

.brand-tagline {
  display: block;
  font-size: 16px;
  color: rgba(241,245,249,0.55);
  margin-bottom: 48px;
  line-height: 1.6;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;

  .f-icon { font-size: 20px; }
  .f-text { font-size: 14px; color: rgba(241,245,249,0.7); }
}

/* ── Form Panel ───────────────────────────────────── */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;

  @media (min-width: 768px) {
    max-width: 480px;
  }
}

.form-inner {
  width: 100%;
  max-width: 400px;
}

/* Mobile Brand */
.mobile-brand {
  text-align: center;
  margin-bottom: 36px;

  .mobile-logo { font-size: 48px; display: block; margin-bottom: 10px; }
  .mobile-title { display: block; font-size: 26px; font-weight: 800; color: var(--text-1); margin-bottom: 6px; }
  .mobile-sub { display: block; font-size: 13px; color: var(--text-3); }

  @media (min-width: 768px) { display: none; }
}

/* Tab Bar */
.tab-bar {
  display: flex;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 4px;
  margin-bottom: 28px;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-3);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s ease;

  &.active {
    background: var(--accent);
    color: #fff;
    font-weight: 600;
    box-shadow: 0 2px 12px var(--accent-glow);
  }
}

/* Fields */
.fields { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;

  .field-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-2);
  }

  .field-input {
    background: var(--bg-input);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 15px;
    color: var(--text-1);
    width: 100%;
    transition: border-color 0.2s;

    &:focus { border-color: var(--accent); }
  }
}

/* Submit Button */
.submit-btn {
  width: 100%;
  background: linear-gradient(135deg, var(--accent) 0%, #8b5cf6 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  padding: 14px;
  border-radius: var(--radius-lg);
  border: none;
  margin-bottom: 14px;
  box-shadow: 0 4px 20px var(--accent-glow);
  transition: opacity 0.2s, transform 0.1s;

  &::after { border: none; }
  &:active { opacity: 0.9; transform: scale(0.99); }
}

/* WeChat Button */
.wechat-btn {
  width: 100%;
  background: #07c160;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  padding: 13px;
  border-radius: var(--radius-lg);
  border: none;
  margin-bottom: 14px;

  &::after { border: none; }
}

/* Footer Hint */
.footer-hint {
  display: block;
  text-align: center;
  font-size: 13px;
  color: var(--text-3);
  margin-top: 8px;

  .footer-link {
    color: var(--accent-2);
    font-weight: 500;
    cursor: pointer;
  }
}
</style>
