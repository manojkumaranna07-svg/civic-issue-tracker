import { Link } from 'react-router-dom'
import StatusBadge from './StatusBadge'

export default function IssueCard({ issue }) {
  return (
    <Link to={`/issues/${issue.id}`} className="card issue-card">
      <div className="issue-card-top">
        <span className="issue-id">{issue.public_id}</span>
        <StatusBadge status={issue.status} />
      </div>
      <h3>{issue.title}</h3>
      <p className="muted clamp">{issue.description}</p>
      <div className="issue-card-meta">
        <span>{issue.sector_name} · {issue.category_name}</span>
        <span>{issue.location_text}</span>
      </div>
      <div className="issue-card-foot">
        <span>&#9650; {issue.upvote_count} supporters</span>
        <span>{new Date(issue.created_at).toLocaleDateString()}</span>
      </div>
    </Link>
  )
}
