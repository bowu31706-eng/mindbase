import { defineStore } from 'pinia'
import { authApi } from '@/api/index'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    user: uni.getStorageSync('user') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(email, password) {
      const res = await authApi.login({ email, password })
      this._saveAuth(res)
    },

    async register(email, password, nickname) {
      const res = await authApi.register({ email, password, nickname })
      this._saveAuth(res)
    },

    async wechatLogin() {
      return new Promise((resolve, reject) => {
        uni.login({
          provider: 'weixin',
          success: async (loginRes) => {
            try {
              const res = await authApi.wechatLogin(loginRes.code)
              this._saveAuth(res)
              resolve(res)
            } catch (e) {
              reject(e)
            }
          },
          fail: reject,
        })
      })
    },

    logout() {
      this.token = ''
      this.user = null
      uni.removeStorageSync('token')
      uni.removeStorageSync('user')
      uni.reLaunch({ url: '/pages/login/index' })
    },

    _saveAuth(res) {
      this.token = res.access_token
      this.user = res.user
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('user', res.user)
    },
  },
})
