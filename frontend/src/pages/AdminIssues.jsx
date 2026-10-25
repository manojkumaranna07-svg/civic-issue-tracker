import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'
import { Spinner, EmptyState, ErrorBox } from '../components/Feedback'

const STATUSES = ['Reported', 'Under Review', 'In Progress', 'Resolved', 'Rejected']

export default function AdminIssues() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)

  useEffect(() => {
    setData(null); setError('')
    api.listIssues({ q, status, sort, page, page_size: 15 })
      .then(setData).catch(e => setError(e.message))
  }, [q, status, sort, page])

  const pages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1

  return (
    <div>
      <div className="page-head"><h1>Manage issues</h1></div>
      <ErrorBox message={error} />
      <div className="card filter-bar">
        <input placeholder="Search…" value={q} onChange={e => { setQ(e.target.value); setPage(1) }} />
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(1) }}>
          <option value="">All statuses</option>
          {STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
        <select value={sort} onChange={e => setSort(e.target.value)}>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="most_upvoted">Most supported</option>
        </select>
      </div>
      {!data ? <Spinner /> : data.items.length === 0 ? <EmptyState title="Nothing found" /> : (
        <div className="card">
          <table className="table">
            <thead><tr><th>ID</th><th>Title</th><th>Sector</th><th>Status</th><th>👍</th><th>Reported</th><th></th></tr></thead>
            <tbody>{data.items.map(i => (
              <tr key={i.id}>
                <td className="mono">{i.public_id}</td>
                <td>{i.title}</td>
                <td className="muted">{i.sector_name}</td>
                <td><StatusBadge status={i.status} /></td>
                <td>{i.upvote_count}</td>
                <td className="muted">{new Date(i.created_at).toLocaleDateString()}</td>
                <td><Link className="btn btn-sm btn-outline" to={`/issues/${i.id}`}>Open</Link></td>
              </tr>
            ))}</tbody>
          </table>
          {pages > 1 && (
            <div className="pager">
              <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
              <span>Page {page} of {pages}</span>
              <button className="btn btn-outline btn-sm" disabled={page >= pages} onClick={() => setPage(p => p + 1)}>Next →</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
