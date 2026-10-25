import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { ErrorBox } from '../components/Feedback'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', phone: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) { setError('Passwords do not match.'); return }
    if (form.password.length < 8) { setError('Password must be at least 8 characters.'); return }
    setBusy(true)
    try {
      await register({ name: form.name.trim(), email: form.email.trim(),
                       password: form.password, phone: form.phone || null })
      navigate('/dashboard')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Create your account</h1>
        <p className="muted">Register as a citizen to start reporting.</p>
        <ErrorBox message={error} />
        <label>Full name
          <input required minLength={2} value={form.name} onChange={set('name')} />
        </label>
        <label>Email
          <input type="email" required value={form.email} onChange={set('email')} autoComplete="email" />
        </label>
        <label>Phone (optional)
          <input value={form.phone} onChange={set('phone')} />
        </label>
        <label>Password
          <input type="password" required minLength={8} value={form.password} onChange={set('password')} autoComplete="new-password" />
        </label>
        <label>Confirm password
          <input type="password" required value={form.confirm} onChange={set('confirm')} autoComplete="new-password" />
        </label>
        <button className="btn btn-primary" disabled={busy}>{busy ? 'Creating…' : 'Register'}</button>
        <p className="muted center">Already registered? <Link to="/login">Login</Link></p>
      </form>
    </div>
  )
}
