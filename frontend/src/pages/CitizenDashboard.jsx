import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import IssueCard from '../components/IssueCard'
import { Spinner, EmptyState, ErrorBox } from '../components/Feedback'

export default function CitizenDashboard() {
  const { user } = useAuth()
  const [mine, setMine] = useState(null)
  const [announcements, setAnnouncements] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.listIssues({ mine: 1, page_size: 6 }).then(r => setMine(r.items)).catch(e => setError(e.message))
    api.announcements().then(setAnnouncements).catch(() => {})
  }, [])

  const counts = (status) => mine?.filter(i => i.status === status).length ?? 0

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Hello, {user.name.split(' ')[0]}</h1>
          <p className="muted">Track your reports and see what's happening around you.</p>
        </div>
        <Link to="/report" className="btn btn-primary">+ Report an issue</Link>
      </div>
      <ErrorBox message={error} />
      {announcements.length > 0 && (
        <div className="announce-strip">
          {announcements.slice(0, 2).map(a => (
            <div className="alert alert-info" key={a.id}><strong>{a.title}</strong> — {a.body}</div>
          ))}
        </div>
      )}
      {!mine ? <Spinner /> : mine.length === 0 ? (
        <EmptyState title="You haven't reported anything yet"
                    hint="Spot a problem in your area? Report it in under a minute." />
      ) : (
        <>
          <div className="stat-row">
            <div className="card stat"><b>{mine.length}</b><span>Reported by you</span></div>
            <div className="card stat"><b>{counts('In Progress')}</b><span>In progress</span></div>
            <div className="card stat"><b>{counts('Resolved')}</b><span>Resolved</span></div>
            <div className="card stat"><b>{mine.reduce((n, i) => n + i.upvote_count, 0)}</b><span>Supporters</span></div>
          </div>
          <h2>Your recent reports</h2>
          <div className="card-grid">
            {mine.map(i => <IssueCard key={i.id} issue={i} />)}
          </div>
          <p className="center"><Link to="/issues?mine=1">View all your issues →</Link></p>
        </>
      )}
    </div>
  )
}
