import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { ErrorBox } from '../components/Feedback'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError(''); setBusy(true)
    try {
      const user = await login(form.email.trim(), form.password)
      navigate(user.role === 'admin' ? '/admin' : '/dashboard')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Welcome back</h1>
        <p className="muted">Log in to report and track issues.</p>
        <ErrorBox message={error} />
        <label>Email
          <input type="email" required value={form.email} autoComplete="email"
                 onChange={e => setForm({ ...form, email: e.target.value })} />
        </label>
        <label>Password
          <input type="password" required value={form.password} autoComplete="current-password"
                 onChange={e => setForm({ ...form, password: e.target.value })} />
        </label>
        <button className="btn btn-primary" disabled={busy}>{busy ? 'Logging in…' : 'Login'}</button>
        <p className="muted center">New here? <Link to="/register">Create an account</Link></p>
        {import.meta.env.VITE_SHOW_DEMO_HINT !== 'false' && (
        <details className="demo-hint">
          <summary>Demo accounts</summary>
          <p className="muted small">
            citizen@example.com / Citizen@123<br />
            staff@example.com / Staff@123<br />
            admin@example.com / Admin@123
          </p>
        </details>
        )}
      </form>
    </div>
  )
}
