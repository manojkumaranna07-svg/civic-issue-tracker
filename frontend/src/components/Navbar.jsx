import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuth } from '../auth'
import { api } from '../api'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    if (!user) { setUnread(0); return }
    let alive = true
    const load = () => api.notifications(true)
      .then(ns => { if (alive) setUnread(ns.length) }).catch(() => {})
    load()
    const t = setInterval(load, 30000)
    return () => { alive = false; clearInterval(t) }
  }, [user])

  if (!user) {
    return (
      <header className="nav">
        <Link className="brand" to="/">Civic Issue Tracker</Link>
        <nav className="nav-links">
          <NavLink to="/login">Login</NavLink>
          <NavLink to="/register" className="btn btn-primary btn-sm">Register</NavLink>
        </nav>
      </header>
    )
  }
  return (
    <header className="nav">
      <Link className="brand" to="/dashboard">Civic Issue Tracker</Link>
      <nav className="nav-links">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/report">Report Issue</NavLink>
        <NavLink to="/issues">Issues</NavLink>
        <NavLink to="/map">Map</NavLink>
        {user.role === 'admin' && <NavLink to="/admin">Admin</NavLink>}
        {user.role === 'admin' && <NavLink to="/admin/panel">Manage</NavLink>}
        <NavLink to="/notifications">
          Notifications{unread > 0 && <span className="pill" data-testid="unread-pill">{unread}</span>}
        </NavLink>
        <NavLink to="/profile" className="nav-user">{user.name}</NavLink>
        <button className="btn btn-ghost btn-sm" onClick={() => { logout(); navigate('/') }}>Logout</button>
      </nav>
    </header>
  )
}
