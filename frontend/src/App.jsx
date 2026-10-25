import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './auth'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import CitizenDashboard from './pages/CitizenDashboard'
import ReportIssue from './pages/ReportIssue'
import IssueList from './pages/IssueList'
import IssueDetail from './pages/IssueDetail'
import MapPage from './pages/MapPage'
import NotificationsPage from './pages/NotificationsPage'
import AdminDashboard from './pages/AdminDashboard'
import AdminIssues from './pages/AdminIssues'
import AdminPanel from './pages/AdminPanel'
import Profile from './pages/Profile'

function Protected({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-center"><div className="spinner" /></div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  const { user } = useAuth()
  return (
    <div className="app-shell">
      <Navbar />
      <main className="page">
        <Routes>
          <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Protected><CitizenDashboard /></Protected>} />
          <Route path="/report" element={<Protected><ReportIssue /></Protected>} />
          <Route path="/issues" element={<Protected><IssueList /></Protected>} />
          <Route path="/issues/:id" element={<Protected><IssueDetail /></Protected>} />
          <Route path="/map" element={<Protected><MapPage /></Protected>} />
          <Route path="/notifications" element={<Protected><NotificationsPage /></Protected>} />
          <Route path="/profile" element={<Protected><Profile /></Protected>} />
          <Route path="/admin" element={<Protected roles={['admin']}><AdminDashboard /></Protected>} />
          <Route path="/admin/issues" element={<Protected roles={['admin']}><AdminIssues /></Protected>} />
          <Route path="/admin/panel" element={<Protected roles={['admin']}><AdminPanel /></Protected>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
