import { useEffect, useState } from 'react'
import { api } from '../api'
import MapView from '../components/MapView'
import { Spinner, ErrorBox } from '../components/Feedback'

const STATUSES = ['Reported', 'Under Review', 'In Progress', 'Resolved', 'Rejected']

export default function MapPage() {
  const [catalog, setCatalog] = useState(null)
  const [issues, setIssues] = useState(null)
  const [error, setError] = useState('')
  const [sector, setSector] = useState('')
  const [status, setStatus] = useState('')

  useEffect(() => { api.bootstrap().then(setCatalog).catch(() => {}) }, [])
  useEffect(() => {
    setIssues(null)
    api.mapIssues({ sector_id: sector, status }).then(setIssues).catch(e => setError(e.message))
  }, [sector, status])

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Issue map</h1>
          <p className="muted">Only reports with a user-pinned location appear here; unpinned reports stay in the list view.</p>
        </div>
        <div className="filter-inline">
          <select value={sector} onChange={e => setSector(e.target.value)} aria-label="Sector filter">
            <option value="">All sectors</option>
            {catalog?.sectors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select value={status} onChange={e => setStatus(e.target.value)} aria-label="Status filter">
            <option value="">All statuses</option>
            {STATUSES.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
      </div>
      <ErrorBox message={error} />
      <div className="legend">
        {[['Reported', '#d97706'], ['Under Review', '#2563eb'], ['In Progress', '#7c3aed'],
          ['Resolved', '#16a34a'], ['Rejected', '#dc2626']].map(([s, c]) => (
          <span key={s} className="legend-item"><i style={{ background: c }} />{s}</span>
        ))}
      </div>
      {!issues ? <Spinner label="Loading map…" /> : (
        <>
          <MapView issues={issues} height={520} />
          <p className="muted">{issues.length} mapped issue{issues.length === 1 ? '' : 's'}</p>
          <p className="muted small">Demo dataset: seeded reports are fictional; their pins mark real, publicly known Chennai locations for demonstration.</p>
        </>
      )}
    </div>
  )
}
