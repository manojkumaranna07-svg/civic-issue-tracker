import { useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth'
import { ErrorBox, SuccessBox } from '../components/Feedback'

export default function Profile() {
  const { user, setUser } = useAuth()
  const [form, setForm] = useState({ name: user.name, phone: user.phone || '' })
  const [pw, setPw] = useState({ current_password: '', new_password: '', confirm: '' })
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [pwMsg, setPwMsg] = useState('')
  const [pwErr, setPwErr] = useState('')

  async function saveProfile(e) {
    e.preventDefault(); setMsg(''); setErr('')
    try {
      const u = await api.updateMe({ name: form.name, phone: form.phone })
      setUser(u); setMsg('Profile saved.')
    } catch (e2) { setErr(e2.message) }
  }

  async function savePassword(e) {
    e.preventDefault(); setPwMsg(''); setPwErr('')
    if (pw.new_password !== pw.confirm) { setPwErr('New passwords do not match.'); return }
    try {
      await api.changePassword({ current_password: pw.current_password, new_password: pw.new_password })
      setPwMsg('Password changed.'); setPw({ current_password: '', new_password: '', confirm: '' })
    } catch (e2) { setPwErr(e2.message) }
  }

  return (
    <div className="page-narrow">
      <h1>Profile</h1>
      <div className="card">
        <p><span className="badge badge-grey">{user.role}</span> <span className="muted">{user.email}</span></p>
        <form onSubmit={saveProfile} className="form-card">
          <ErrorBox message={err} /><SuccessBox message={msg} />
          <label>Full name<input required minLength={2} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></label>
          <label>Phone<input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} /></label>
          <button className="btn btn-primary">Save profile</button>
        </form>
      </div>
      <div className="card">
        <h3>Change password</h3>
        <form onSubmit={savePassword} className="form-card">
          <ErrorBox message={pwErr} /><SuccessBox message={pwMsg} />
          <label>Current password<input type="password" required value={pw.current_password} onChange={e => setPw({ ...pw, current_password: e.target.value })} /></label>
          <label>New password<input type="password" required minLength={8} value={pw.new_password} onChange={e => setPw({ ...pw, new_password: e.target.value })} /></label>
          <label>Confirm new password<input type="password" required value={pw.confirm} onChange={e => setPw({ ...pw, confirm: e.target.value })} /></label>
          <button className="btn btn-primary">Change password</button>
        </form>
      </div>
    </div>
  )
}
