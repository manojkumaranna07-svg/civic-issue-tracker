import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Spinner, EmptyState, ErrorBox } from '../components/Feedback'

const ICONS = { submission: 'N', status_change: 'S', comment: 'C', resolved: '\u2713', announcement: 'A' }

export default function NotificationsPage() {
  const [notes, setNotes] = useState(null)
  const [error, setError] = useState('')
  const [unreadOnly, setUnreadOnly] = useState(false)

  const load = () => {
    setError('')
    api.notifications(unreadOnly).then(setNotes).catch(e => setError(e.message))
  }
  useEffect(load, [unreadOnly])

  async function markAll() { await api.markAllRead(); load() }
  async function markOne(n) { if (!n.is_read) { await api.markRead(n.id); load() } }

  return (
    <div className="page-narrow">
      <div className="page-head">
        <h1>Notifications</h1>
        <div className="filter-inline">
          <label className="check">
            <input type="checkbox" checked={unreadOnly} onChange={e => setUnreadOnly(e.target.checked)} /> Unread only
          </label>
          <button className="btn btn-outline btn-sm" onClick={markAll}>Mark all read</button>
        </div>
      </div>
      <ErrorBox message={error} />
      {!notes ? <Spinner /> : notes.length === 0 ? (
        <EmptyState title="All caught up" hint="You'll be notified when your issues change status." />
      ) : (
        <div className="note-list">
          {notes.map(n => (
            <button key={n.id} className={`card note ${n.is_read ? '' : 'note-unread'}`} onClick={() => markOne(n)}>
              <span className="note-icon">{ICONS[n.type] || '\u25CF'}</span>
              <span className="note-body">
                <b>{n.title}</b>
                <span className="muted">{n.message}</span>
                <span className="muted small">{new Date(n.created_at).toLocaleString()}</span>
              </span>
              {n.issue_id && <Link className="btn btn-ghost btn-sm" to={`/issues/${n.issue_id}`}>View</Link>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
