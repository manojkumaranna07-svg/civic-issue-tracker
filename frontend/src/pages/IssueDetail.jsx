import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import StatusBadge from '../components/StatusBadge'
import MapView from '../components/MapView'
import ConfirmDialog from '../components/ConfirmDialog'
import { Spinner, ErrorBox, SuccessBox } from '../components/Feedback'

const NEXT_STATUSES = {
  'Reported': ['Under Review', 'In Progress', 'Resolved', 'Rejected'],
  'Under Review': ['In Progress', 'Resolved', 'Rejected', 'Reported'],
  'In Progress': ['Resolved', 'Under Review'],
  'Resolved': ['In Progress'],
  'Rejected': ['Under Review'],
}

export default function IssueDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [issue, setIssue] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [catalog, setCatalog] = useState(null)
  const [staffUsers, setStaffUsers] = useState([])
  const [statusForm, setStatusForm] = useState({ status: '', comment: '', rejection_reason: '' })
  const [assignForm, setAssignForm] = useState({ department_id: '', assigned_to_id: '', note: '' })
  const [comment, setComment] = useState('')
  const [confirming, setConfirming] = useState(null) // {kind:'status'|'delete'|'unvote'}
  const [busy, setBusy] = useState(false)

  const load = useCallback(() => {
    setError('')
    return api.getIssue(id).then(setIssue).catch(e => setError(e.message))
  }, [id])

  useEffect(() => { load() }, [load])
  useEffect(() => {
    if (user.role === 'admin') {
      api.bootstrap().then(setCatalog).catch(() => {})
      api.listUsers('staff').then(setStaffUsers).catch(() => {})
    }
  }, [user.role])

  if (error && !issue) return <ErrorBox message={error} onRetry={load} />
  if (!issue) return <Spinner />

  const canModerate = user.role === 'admin' ||
    (user.role === 'staff' && issue.assignments.some(a => a.is_active && a.assigned_to_name === user.name))
  const allowedNext = NEXT_STATUSES[issue.status] || []

  async function doUpvote() {
    setError('')
    try {
      issue.upvoted_by_me ? await api.removeUpvote(issue.id) : await api.upvote(issue.id)
      await load()
    } catch (e) { setError(e.message) }
    setConfirming(null)
  }

  async function doStatus() {
    setBusy(true); setError(''); setNotice('')
    try {
      const body = { status: statusForm.status }
      if (statusForm.comment) body.comment = statusForm.comment
      if (statusForm.rejection_reason) body.rejection_reason = statusForm.rejection_reason
      await api.updateStatus(issue.id, body)
      setNotice(`Status updated to ${statusForm.status}.`)
      setStatusForm({ status: '', comment: '', rejection_reason: '' })
      await load()
    } catch (e) { setError(e.message) } finally { setBusy(false); setConfirming(null) }
  }

  async function doAssign(e) {
    e.preventDefault()
    setError('')
    try {
      const body = { department_id: Number(assignForm.department_id) }
      if (assignForm.assigned_to_id) body.assigned_to_id = Number(assignForm.assigned_to_id)
      if (assignForm.note) body.note = assignForm.note
      await api.assignIssue(issue.id, body)
      setAssignForm({ department_id: '', assigned_to_id: '', note: '' })
      setNotice('Assignment saved.')
      await load()
    } catch (e2) { setError(e2.message) }
  }

  async function doComment(e) {
    e.preventDefault()
    if (!comment.trim()) return
    setError('')
    try { await api.addComment(issue.id, { body: comment.trim() }); setComment(''); await load() }
    catch (e2) { setError(e2.message) }
  }

  async function doDelete() {
    try { await api.deleteIssue(issue.id); navigate('/issues') }
    catch (e) { setError(e.message); setConfirming(null) }
  }

  const deptStaff = staffUsers.filter(u => String(u.department_id) === String(assignForm.department_id))

  return (
    <div>
      <p><Link to="/issues" className="muted">← All issues</Link></p>
      <div className="page-head">
        <div>
          <div className="issue-card-top">
            <span className="issue-id-lg">{issue.public_id}</span>
            <StatusBadge status={issue.status} />
          </div>
          <h1>{issue.title}</h1>
          <p className="muted">Reported by {issue.reporter_name} on {new Date(issue.created_at).toLocaleString()}</p>
        </div>
        <button className={`btn ${issue.upvoted_by_me ? 'btn-outline' : 'btn-primary'}`}
                onClick={() => issue.upvoted_by_me ? setConfirming({ kind: 'unvote' }) : doUpvote()}>
          &#9650; {issue.upvoted_by_me ? 'Supported' : 'Me Too'} ({issue.upvote_count})
        </button>
      </div>
      <ErrorBox message={error} />
      <SuccessBox message={notice} />
      {issue.status === 'Rejected' && issue.rejection_reason &&
        <div className="alert alert-error"><strong>Rejected:</strong> {issue.rejection_reason}</div>}

      <div className="detail-grid">
        <div>
          <div className="card">
            <h3>Details</h3>
            <p>{issue.description}</p>
            <dl className="facts">
              <dt>Sector</dt><dd>{issue.sector_name}</dd>
              <dt>Category</dt><dd>{issue.category_name}</dd>
              <dt>Location</dt><dd>{issue.location_text}</dd>
              {issue.resolved_at && <><dt>Resolved</dt><dd>{new Date(issue.resolved_at).toLocaleString()}</dd></>}
            </dl>
            {issue.images.length > 0 && (
              <div className="image-row">
                {issue.images.map(img => (
                  <a key={img.id} href={img.url} target="_blank" rel="noreferrer">
                    <img src={img.url} alt={img.original_name} className="issue-photo" />
                  </a>
                ))}
              </div>
            )}
          </div>

          {issue.latitude != null && (
            <div className="card">
              <h3>Location on map</h3>
              <MapView issues={[{ id: null, public_id: issue.public_id, title: issue.title, status: issue.status, sector_name: issue.sector_name, latitude: issue.latitude, longitude: issue.longitude, upvote_count: issue.upvote_count }]}
                       center={[issue.latitude, issue.longitude]} zoom={15} height={260} />
            </div>
          )}

          <div className="card">
            <h3>Discussion ({issue.comments.length})</h3>
            {issue.comments.length === 0 && <p className="muted">No comments yet.</p>}
            {issue.comments.map(c => (
              <div key={c.id} className={`comment ${c.is_admin ? 'comment-admin' : ''}`}>
                <b>{c.author_name}{c.is_admin && <span className="badge badge-blue">Official</span>}</b>
                <span className="muted small"> · {new Date(c.created_at).toLocaleString()}</span>
                <p>{c.body}</p>
              </div>
            ))}
            <form onSubmit={doComment} className="comment-form">
              <textarea rows={2} placeholder="Add a comment…" value={comment} onChange={e => setComment(e.target.value)} />
              <button className="btn btn-primary btn-sm" disabled={!comment.trim()}>Post</button>
            </form>
          </div>
        </div>

        <div>
          <div className="card">
            <h3>Progress history</h3>
            <ol className="timeline">
              {issue.status_history.map(h => (
                <li key={h.id}>
                  <StatusBadge status={h.new_status} />
                  <div>
                    {h.comment && <p>{h.comment}</p>}
                    <span className="muted small">{h.changed_by_name} · {new Date(h.created_at).toLocaleString()}</span>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          {issue.assignments.length > 0 && (
            <div className="card">
              <h3>Assignments</h3>
              {issue.assignments.filter(a => a.is_active).map(a => (
                <p key={a.id}><b>{a.department_name}</b>
                  {a.assigned_to_name && <> → {a.assigned_to_name}</>}
                  {a.note && <><br /><span className="muted small">{a.note}</span></>}</p>
              ))}
            </div>
          )}

          {canModerate && allowedNext.length > 0 && (
            <div className="card admin-box">
              <h3>Update status</h3>
              <label>New status
                <select value={statusForm.status} onChange={e => setStatusForm({ ...statusForm, status: e.target.value })}>
                  <option value="">Choose…</option>
                  {(user.role === 'staff' ? allowedNext.filter(s => ['In Progress', 'Resolved'].includes(s)) : allowedNext)
                    .map(s => <option key={s}>{s}</option>)}
                </select>
              </label>
              {statusForm.status === 'Rejected' && (
                <label>Rejection reason *
                  <input value={statusForm.rejection_reason}
                         onChange={e => setStatusForm({ ...statusForm, rejection_reason: e.target.value })} />
                </label>
              )}
              <label>Note (visible to reporter)
                <input value={statusForm.comment}
                       onChange={e => setStatusForm({ ...statusForm, comment: e.target.value })} />
              </label>
              <button className="btn btn-primary" disabled={!statusForm.status || busy}
                      onClick={() => setConfirming({ kind: 'status' })}>Apply</button>
            </div>
          )}

          {user.role === 'admin' && catalog && (
            <div className="card admin-box">
              <h3>Assign to department</h3>
              <form onSubmit={doAssign}>
                <label>Department
                  <select required value={assignForm.department_id}
                          onChange={e => setAssignForm({ ...assignForm, department_id: e.target.value, assigned_to_id: '' })}>
                    <option value="">Choose…</option>
                    {catalog.departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </label>
                {deptStaff.length > 0 && (
                  <label>Staff member (optional)
                    <select value={assignForm.assigned_to_id}
                            onChange={e => setAssignForm({ ...assignForm, assigned_to_id: e.target.value })}>
                      <option value="">Whole department</option>
                      {deptStaff.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                    </select>
                  </label>
                )}
                <label>Note
                  <input value={assignForm.note} onChange={e => setAssignForm({ ...assignForm, note: e.target.value })} />
                </label>
                <button className="btn btn-primary">Assign</button>
              </form>
            </div>
          )}

          {(user.role === 'admin' || (user.id === issue.reporter_id && issue.status === 'Reported')) && (
            <button className="btn btn-danger btn-sm" onClick={() => setConfirming({ kind: 'delete' })}>Delete issue</button>
          )}
        </div>
      </div>

      <ConfirmDialog open={confirming?.kind === 'status'} title="Change status?"
        body={`Move ${issue.public_id} to "${statusForm.status}"? The reporter will be notified.`}
        confirmLabel="Change status" onConfirm={doStatus} onCancel={() => setConfirming(null)} />
      <ConfirmDialog open={confirming?.kind === 'delete'} title="Delete this issue?"
        body={`${issue.public_id} and its history will be permanently removed.`} danger
        confirmLabel="Delete" onConfirm={doDelete} onCancel={() => setConfirming(null)} />
      <ConfirmDialog open={confirming?.kind === 'unvote'} title="Remove your support?"
        body="Your Me Too vote will be withdrawn from this issue."
        confirmLabel="Remove vote" onConfirm={doUpvote} onCancel={() => setConfirming(null)} />
    </div>
  )
}
