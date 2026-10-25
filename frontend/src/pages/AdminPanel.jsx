import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import ConfirmDialog from '../components/ConfirmDialog'
import { Spinner, ErrorBox, SuccessBox } from '../components/Feedback'

export default function AdminPanel() {
  const [tab, setTab] = useState('users')
  const [users, setUsers] = useState(null)
  const [catalog, setCatalog] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [confirming, setConfirming] = useState(null)
  const [annForm, setAnnForm] = useState({ title: '', body: '' })
  const [sectorName, setSectorName] = useState('')
  const [catForm, setCatForm] = useState({ sector_id: '', name: '' })
  const [deptForm, setDeptForm] = useState({ name: '', sector_id: '' })

  const load = useCallback(() => {
    setError('')
    api.listUsers().then(setUsers).catch(e => setError(e.message))
    api.bootstrap().then(setCatalog).catch(e => setError(e.message))
  }, [])
  useEffect(() => { load() }, [load])

  const run = (fn, msg) => async () => {
    setError(''); setNotice('')
    try { await fn(); setNotice(msg); load() } catch (e) { setError(e.message) }
    setConfirming(null)
  }

  async function postAnnouncement(e) {
    e.preventDefault()
    setError(''); setNotice('')
    try {
      await api.createAnnouncement(annForm)
      setAnnForm({ title: '', body: '' })
      setNotice('Announcement broadcast to all users.')
    } catch (e2) { setError(e2.message) }
  }

  if (!users || !catalog) return <Spinner />
  return (
    <div>
      <div className="page-head"><h1>Administration</h1></div>
      <ErrorBox message={error} /><SuccessBox message={notice} />
      <div className="tabs">
        {[['users', 'Users & roles'], ['catalog', 'Sectors, categories & departments'], ['broadcast', 'Announcements']].map(([k, label]) => (
          <button key={k} className={`tab ${tab === k ? 'tab-active' : ''}`} onClick={() => setTab(k)}>{label}</button>
        ))}
      </div>

      {tab === 'users' && (
        <div className="card">
          <table className="table">
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Active</th><th>Actions</th></tr></thead>
            <tbody>{users.map(u => (
              <tr key={u.id}>
                <td>{u.name}</td><td className="muted">{u.email}</td>
                <td><span className="badge badge-grey">{u.role}</span></td>
                <td>{u.is_active ? 'Yes' : 'No'}</td>
                <td className="row-actions">
                  {u.role !== 'staff' && catalog.departments.length > 0 && (
                    <button className="btn btn-sm btn-outline"
                      onClick={() => setConfirming({ kind: 'make-staff', user: u, dept: catalog.departments[0].id })}>
                      Make staff</button>
                  )}
                  {u.role !== 'admin' && (
                    <button className="btn btn-sm btn-outline"
                      onClick={() => setConfirming({ kind: 'toggle-active', user: u })}>
                      {u.is_active ? 'Deactivate' : 'Reactivate'}</button>
                  )}
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}

      {tab === 'catalog' && (
        <div className="charts-grid">
          <div className="card">
            <h3>Sectors</h3>
            <ul className="plain-list">
              {catalog.sectors.map(s => (
                <li key={s.id}>{s.name}
                  <button className="btn btn-ghost btn-sm" onClick={() => setConfirming({ kind: 'del-sector', id: s.id, name: s.name })}>&#215;</button>
                </li>
              ))}
            </ul>
            <form className="inline-form" onSubmit={e => { e.preventDefault(); run(() => api.createSector({ name: sectorName }), 'Sector added.')(); setSectorName('') }}>
              <input required minLength={2} placeholder="New sector" value={sectorName} onChange={e => setSectorName(e.target.value)} />
              <button className="btn btn-primary btn-sm">Add</button>
            </form>
          </div>
          <div className="card">
            <h3>Categories</h3>
            <ul className="plain-list">
              {catalog.categories.map(c => (
                <li key={c.id}>{c.name} <span className="muted small">({catalog.sectors.find(s => s.id === c.sector_id)?.name})</span>
                  <button className="btn btn-ghost btn-sm" onClick={() => setConfirming({ kind: 'del-cat', id: c.id, name: c.name })}>&#215;</button>
                </li>
              ))}
            </ul>
            <form className="inline-form" onSubmit={e => { e.preventDefault(); run(() => api.createCategory({ sector_id: Number(catForm.sector_id), name: catForm.name }), 'Category added.')(); setCatForm({ sector_id: '', name: '' }) }}>
              <select required value={catForm.sector_id} onChange={e => setCatForm({ ...catForm, sector_id: e.target.value })}>
                <option value="">Sector…</option>
                {catalog.sectors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
              <input required minLength={2} placeholder="New category" value={catForm.name} onChange={e => setCatForm({ ...catForm, name: e.target.value })} />
              <button className="btn btn-primary btn-sm">Add</button>
            </form>
          </div>
          <div className="card">
            <h3>Departments</h3>
            <ul className="plain-list">
              {catalog.departments.map(d => (
                <li key={d.id}>{d.name}
                  <button className="btn btn-ghost btn-sm" onClick={() => setConfirming({ kind: 'del-dept', id: d.id, name: d.name })}>&#215;</button>
                </li>
              ))}
            </ul>
            <form className="inline-form" onSubmit={e => { e.preventDefault(); run(() => api.createDepartment({ name: deptForm.name, sector_id: deptForm.sector_id ? Number(deptForm.sector_id) : null }), 'Department added.')(); setDeptForm({ name: '', sector_id: '' }) }}>
              <input required minLength={2} placeholder="New department" value={deptForm.name} onChange={e => setDeptForm({ ...deptForm, name: e.target.value })} />
              <select value={deptForm.sector_id} onChange={e => setDeptForm({ ...deptForm, sector_id: e.target.value })}>
                <option value="">No sector link</option>
                {catalog.sectors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
              <button className="btn btn-primary btn-sm">Add</button>
            </form>
          </div>
        </div>
      )}

      {tab === 'broadcast' && (
        <form className="card form-card page-narrow" onSubmit={postAnnouncement}>
          <h3>Broadcast an announcement</h3>
          <p className="muted">Every user gets an in-app notification.</p>
          <label>Title<input required minLength={3} value={annForm.title} onChange={e => setAnnForm({ ...annForm, title: e.target.value })} /></label>
          <label>Message<textarea required minLength={3} rows={4} value={annForm.body} onChange={e => setAnnForm({ ...annForm, body: e.target.value })} /></label>
          <button className="btn btn-primary">Broadcast</button>
        </form>
      )}

      <ConfirmDialog open={confirming?.kind === 'make-staff'} title="Change role to staff?"
        body={`${confirming?.user.name} will become department staff.`}
        onConfirm={run(() => api.updateUserRole(confirming.user.id, { role: 'staff', department_id: confirming.dept }), 'Role updated.')}
        onCancel={() => setConfirming(null)} />
      <ConfirmDialog open={confirming?.kind === 'toggle-active'} title={confirming?.user.is_active ? 'Deactivate account?' : 'Reactivate account?'}
        body={confirming?.user.email} danger={confirming?.user.is_active}
        onConfirm={run(() => api.updateUserRole(confirming.user.id, { role: confirming.user.role, is_active: !confirming.user.is_active }), 'Account updated.')}
        onCancel={() => setConfirming(null)} />
      <ConfirmDialog open={['del-sector', 'del-cat', 'del-dept'].includes(confirming?.kind)} title="Delete entry?"
        body={`"${confirming?.name}" will be removed. Entries used by issues cannot be deleted.`} danger
        onConfirm={run(() =>
          confirming.kind === 'del-sector' ? api.deleteSector(confirming.id)
          : confirming.kind === 'del-cat' ? api.deleteCategory(confirming.id)
          : api.deleteDepartment(confirming.id), 'Deleted.')}
        onCancel={() => setConfirming(null)} />
    </div>
  )
}
