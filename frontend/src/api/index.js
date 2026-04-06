import { request, uploadFile } from './request'

// ── 认证 ──────────────────────────────────────────────
export const authApi = {
  register: (data) => request({ url: '/auth/register', method: 'POST', data }),
  login: (data) => request({ url: '/auth/login', method: 'POST', data }),
  wechatLogin: (code) => request({ url: '/auth/wechat', method: 'POST', data: { code } }),
}

// ── 笔记 ──────────────────────────────────────────────
export const notesApi = {
  list: (params = {}) => request({ url: '/notes/', method: 'GET', data: params }),
  get: (id) => request({ url: `/notes/${id}` }),
  create: (data) => request({ url: '/notes/', method: 'POST', data }),
  update: (id, data) => request({ url: `/notes/${id}`, method: 'PUT', data }),
  delete: (id) => request({ url: `/notes/${id}`, method: 'DELETE' }),
  fromUrl: (url) => request({ url: `/notes/from-url?url=${encodeURIComponent(url)}`, method: 'POST' }),
  fromPdf: (filePath) => uploadFile(filePath, '/notes/from-pdf'),
  togglePublic: (id, isPublic) => request({ url: `/notes/${id}/public`, method: 'PATCH', data: { is_public: isPublic } }),
  getPublic: (slug) => request({ url: `/notes/public/${slug}` }),
  starNote: (id, isStarred) => request({ url: `/notes/${id}/star`, method: 'PATCH', data: { is_starred: isStarred } }),
  restoreNote: (id) => request({ url: `/notes/${id}/restore`, method: 'POST' }),
  deletePermanent: (id) => request({ url: `/notes/${id}/permanent`, method: 'DELETE' }),
  emptyTrash: () => request({ url: '/notes/trash/empty', method: 'DELETE' }),
}

// ── 标签 ──────────────────────────────────────────────
export const tagsApi = {
  list: () => request({ url: '/tags/' }),
  create: (data) => request({ url: '/tags/', method: 'POST', data }),
  update: (id, data) => request({ url: `/tags/${id}`, method: 'PUT', data }),
  delete: (id) => request({ url: `/tags/${id}`, method: 'DELETE' }),
}

// ── 搜索 ──────────────────────────────────────────────
export const searchApi = {
  search: (q) => request({ url: `/search/?q=${encodeURIComponent(q)}` }),
}

// ── 对话 ──────────────────────────────────────────────
export const chatApi = {
  listConversations: () => request({ url: '/chat/conversations' }),
  getMessages: (convId) => request({ url: `/chat/conversations/${convId}/messages` }),
  chat: (data) => request({ url: '/chat/', method: 'POST', data }),
  deleteConversation: (convId) => request({ url: `/chat/conversations/${convId}`, method: 'DELETE' }),
}
