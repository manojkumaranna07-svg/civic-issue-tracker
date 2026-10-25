import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { api, setToken, getToken } from './api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!getToken())

  useEffect(() => {
    if (!getToken()) return
    api.me()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const res = await api.login(email, password)
    setToken(res.access_token)
    setUser(res.user)
    return res.user
  }, [])

  const register = useCallback(async (payload) => {
    const res = await api.register(payload)
    setToken(res.access_token)
    setUser(res.user)
    return res.user
  }, [])

  const logout = useCallback(() => { setToken(null); setUser(null) }, [])

  return <AuthCtx.Provider value={{ user, setUser, loading, login, register, logout }}>
    {children}
  </AuthCtx.Provider>
}

export function useAuth() { return useContext(AuthCtx) }
