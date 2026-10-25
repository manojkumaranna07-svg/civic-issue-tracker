import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api'
import IssueCard from '../components/IssueCard'
import { Spinner, EmptyState, ErrorBox } from '../components/Feedback'

const STATUSES = ['Reported', 'Under Review', 'In Progress', 'Resolved', 'Rejected']

export default function IssueList() {
  const [params, setParams] = useSearchParams()
  const [catalog, setCatalog] = useState(null)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)

  const filters = useMemo(() => ({
    q: params.get('q') || '', sector_id: params.get('sector_id') || '',
    category_id: params.get('category_id') || '', status: params.get('status') || '',
    location: params.get('location') || '', mine: params.get('mine') || '',
    sort: params.get('sort') || 'newest',
  }), [params])

  useEffect(() => { api.bootstrap().then(setCatalog).catch(() => {}) }, [])

  useEffect(() => {
    setData(null); setError('')
    api.listIssues({ ...filters, page, page_size: 12 })
      .then(setData).catch(e => setError(e.message))
  }, [filters, page])

  const setFilter = (k, v) => {
    const next = new URLSearchParams(params)
    v ? next.set(k, v) : next.delete(k)
    if (k === 'sector_id') next.delete('category_id')
    setParams(next); setPage(1)
  }

  const categories = catalog?.categories.filter(c => !filters.sector_id || String(c.sector_id) === filters.sector_id) ?? []
  const pages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1

  return (
    <div>
      <div className="page-head"><h1>Reported issues</h1></div>
      <ErrorBox message={error} />
      <div className="card filter-bar">
        <input placeholder="Search title, description or ID…" value={filters.q}
               onChange={e => setFilter('q', e.target.value)} aria-label="Search issues" />
        <select value={filters.sector_id} onChange={e => setFilter('sector_id', e.target.value)} aria-label="Sector">
          <option value="">All sectors</option>
          {catalog?.sectors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select value={filters.category_id} onChange={e => setFilter('category_id', e.target.value)} aria-label="Category">
          <option value="">All categories</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filters.status} onChange={e => setFilter('status', e.target.value)} aria-label="Status">
          <option value="">All statuses</option>
          {STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
        <input placeholder="Location…" value={filters.location}
               onChange={e => setFilter('location', e.target.value)} aria-label="Location" />
        <select value={filters.sort} onChange={e => setFilter('sort', e.target.value)} aria-label="Sort">
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="most_upvoted">Most supported</option>
        </select>
        <label className="check">
          <input type="checkbox" checked={!!filters.mine} onChange={e => setFilter('mine', e.target.checked ? '1' : '')} /> Mine only
        </label>
      </div>
      {!data ? <Spinner /> : data.items.length === 0 ? (
        <EmptyState title="No issues match" hint="Try widening the filters or search text." />
      ) : (
        <>
          <p className="muted">{data.total} issue{data.total === 1 ? '' : 's'} found</p>
          <div className="card-grid">{data.items.map(i => <IssueCard key={i.id} issue={i} />)}</div>
          {pages > 1 && (
            <div className="pager">
              <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
              <span>Page {page} of {pages}</span>
              <button className="btn btn-outline btn-sm" disabled={page >= pages} onClick={() => setPage(p => p + 1)}>Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
