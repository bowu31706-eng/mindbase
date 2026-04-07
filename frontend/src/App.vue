<script setup>
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'

const DEMO_EMAIL = 'demo@mindbase.app'
const DEMO_PASS  = 'mindbase2024'
const DEMO_NAME  = 'Demo'

onLaunch(async () => {
  const userStore  = useUserStore()
  const themeStore = useThemeStore()
  themeStore.init()

  if (!userStore.isLoggedIn) {
    // 自动用 demo 账号登录，让访客无需注册即可体验
    try {
      await userStore.login(DEMO_EMAIL, DEMO_PASS)
    } catch {
      try {
        await userStore.register(DEMO_EMAIL, DEMO_PASS, DEMO_NAME)
      } catch {}
    }
    uni.reLaunch({ url: '/pages/index/index' })
  }
})
</script>

<style lang="scss">
/* ── Global Design Tokens ─────────────────────────────────────── */
:root {
  --bg-base:       #f0f2f5;
  --bg-surface:    #ffffff;
  --bg-card:       #ffffff;
  --bg-card-hover: #f8fafc;
  --bg-input:      #f8fafc;
  --border:        #e2e8f0;
  --border-strong: #cbd5e1;

  --text-1: #0f172a;
  --text-2: #475569;
  --text-3: #94a3b8;
  --text-4: #cbd5e1;

  --accent:        #6366f1;
  --accent-2:      #4f46e5;
  --accent-bg:     rgba(99,102,241,0.09);
  --accent-glow:   rgba(99,102,241,0.22);

  --sidebar-bg:    #f5f0e8;
  --sidebar-text:  #1e293b;
  --sidebar-text-muted: #64748b;
  --header-bg:     #ffffff;

  --shadow-sm:   0 1px 4px rgba(0,0,0,0.07);
  --shadow:      0 4px 16px rgba(0,0,0,0.10);
  --shadow-lg:   0 8px 32px rgba(0,0,0,0.13);

  --radius-xs: 6px;
  --radius-sm: 8px;
  --radius:    12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 28px;
}

/* ── Base Reset ───────────────────────────────────────────────── */
page {
  background-color: var(--bg-base);
  color: var(--text-1);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'PingFang SC',
               'Hiragino Sans GB', 'Microsoft YaHei', 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

/* Hide the default uni-app tabBar so our custom nav takes over */
/* #ifdef H5 */
.uni-tabbar { display: none !important; }
.uni-app--showlayout .uni-tabbar-bottom { display: none !important; }
/* #endif */

.safe-area-bottom { padding-bottom: env(safe-area-inset-bottom); }
.safe-area-top    { padding-top:    env(safe-area-inset-top);    }
</style>
