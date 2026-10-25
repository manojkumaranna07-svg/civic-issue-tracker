// Small fetch wrapper: attaches the JWT, normalises errors, exports helpers.
const TOKEN_KEY = 'civic_token'

export function getToken() { return localStorage.getItem(TOKEN_KEY) }
export function setToken(t) { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY) }

export class ApiError extends Error {
  constructor(status, detail) { super(detail); this.status = status }
}

async function request(path, { method = 'GET', body, formData } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const res = await fetch(path, {
    method, headers,
    body: formData !== undefined ? formData : body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (res.status === 204) return null
  let data = null
  try { data = await res.json() } catch { /* non-JSON */ }
  if (!res.ok) {
    const detail = data?.detail
    const msg = typeof detail === 'string' ? detail
      : Array.isArray(detail) ? detail.map(d => d.msg).join('; ')
      : `Request failed (${res.status})`
    throw new ApiError(res.status, msg)
  }
  return data
}

export const api = {
  // auth
  login: (email, password) => request('/api/auth/login', { method: 'POST', body: { email, password } }),
  register: (payload) => request('/api/auth/register', { method: 'POST', body: payload }),
  me: () => request('/api/users/me'),
  updateMe: (payload) => request('/api/users/me', { method: 'PUT', body: payload }),
  changePassword: (payload) => request('/api/users/me/password', { method: 'PUT', body: payload }),
  // catalog
  bootstrap: () => request('/api/meta/bootstrap'),
  createSector: (b) => request('/api/meta/sectors', { method: 'POST', body: b }),
  deleteSector: (id) => request(`/api/meta/sectors/${id}`, { method: 'DELETE' }),
  createCategory: (b) => request('/api/meta/categories', { method: 'POST', body: b }),
  deleteCategory: (id) => request(`/api/meta/categories/${id}`, { method: 'DELETE' }),
  createDepartment: (b) => request('/api/meta/departments', { method: 'POST', body: b }),
  deleteDepartment: (id) => request(`/api/meta/departments/${id}`, { method: 'DELETE' }),
  // issues
  createIssue: (formData) => request('/api/issues', { method: 'POST', formData }),
  listIssues: (params = {}) => {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => { if (v !== '' && v != null) qs.set(k, v) })
    return request(`/api/issues?${qs.toString()}`)
  },
  getIssue: (id) => request(`/api/issues/${id}`),
  deleteIssue: (id) => request(`/api/issues/${id}`, { method: 'DELETE' }),
  upvote: (id) => request(`/api/issues/${id}/upvote`, { method: 'POST' }),
  removeUpvote: (id) => request(`/api/issues/${id}/upvote`, { method: 'DELETE' }),
  updateStatus: (id, b) => request(`/api/issues/${id}/status`, { method: 'POST', body: b }),
  assignIssue: (id, b) => request(`/api/issues/${id}/assign`, { method: 'POST', body: b }),
  addComment: (id, b) => request(`/api/issues/${id}/comments`, { method: 'POST', body: b }),
  // map
  mapIssues: (params = {}) => {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => { if (v !== '' && v != null) qs.set(k, v) })
    return request(`/api/map/issues?${qs.toString()}`)
  },
  // notifications & announcements
  notifications: (unreadOnly = false) => request(`/api/notifications${unreadOnly ? '?unread_only=1' : ''}`),
  markRead: (id) => request(`/api/notifications/${id}/read`, { method: 'POST' }),
  markAllRead: () => request('/api/notifications/read-all', { method: 'POST' }),
  announcements: () => request('/api/announcements'),
  createAnnouncement: (b) => request('/api/announcements', { method: 'POST', body: b }),
  // dashboard & users (admin)
  stats: () => request('/api/dashboard/stats'),
  listUsers: (role) => request(`/api/users${role ? `?role=${role}` : ''}`),
  updateUserRole: (id, b) => request(`/api/users/${id}/role`, { method: 'PUT', body: b }),
}
