import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'
import { Spinner, ErrorBox } from '../components/Feedback'

const STATUS_COLORS = { 'Reported': '#d97706', 'Under Review': '#2563eb', 'In Progress': '#7c3aed', 'Resolved': '#16a34a', 'Rejected': '#dc2626' }
const PIE_COLORS = ['#2563eb', '#16a34a', '#d97706', '#7c3aed', '#dc2626', '#0891b2', '#be185d', '#65a30d']

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => { api.stats().then(setStats).catch(e => setError(e.message)) }, [])

  if (error) return <ErrorBox message={error} />
  if (!stats) return <Spinner label="Computing statistics…" />

  const by = Object.fromEntries(stats.by_status.map(s => [s.status, s.count]))
  return (
    <div>
      <div className="page-head">
        <h1>Admin dashboard</h1>
        <Link to="/admin/issues" className="btn btn-primary">Manage issues</Link>
      </div>
      <div className="stat-row">
        <div className="card stat"><b>{stats.total_issues}</b><span>Total issues</span></div>
        <div className="card stat"><b>{(by['Reported'] || 0) + (by['Under Review'] || 0)}</b><span>Awaiting action</span></div>
        <div className="card stat"><b>{by['In Progress'] || 0}</b><span>In progress</span></div>
        <div className="card stat"><b>{by['Resolved'] || 0}</b><span>Resolved</span></div>
        <div className="card stat"><b>{by['Rejected'] || 0}</b><span>Rejected</span></div>
        <div className="card stat"><b>{stats.total_users}</b><span>Users</span></div>
      </div>
      <div className="charts-grid">
        <div className="card">
          <h3>Issues by status</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats.by_status}>
              <XAxis dataKey="status" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={50} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count">
                {stats.by_status.map(s => <Cell key={s.status} fill={STATUS_COLORS[s.status]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Issues by sector</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={stats.by_sector} dataKey="count" nameKey="sector" cx="50%" cy="42%" outerRadius={70}>
                {stats.by_sector.map((s, i) => <Cell key={s.sector} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
                formatter={(value, entry) => `${value} (${entry.payload.count})`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="charts-grid">
        <div className="card">
          <h3>Top categories</h3>
          {stats.top_categories.length === 0 ? <p className="muted">No data yet.</p> : (
            <table className="table">
              <thead><tr><th>Category</th><th>Sector</th><th>Reports</th></tr></thead>
              <tbody>{stats.top_categories.map(c => (
                <tr key={c.category}><td>{c.category}</td><td className="muted">{c.sector}</td><td><b>{c.count}</b></td></tr>
              ))}</tbody>
            </table>
          )}
        </div>
        <div className="card">
          <h3>Resolution insight</h3>
          <p><b>{stats.resolved_last_30_days}</b> issues resolved in the last 30 days</p>
          <p>Average resolution time: <b>{stats.avg_resolution_hours != null ? `${stats.avg_resolution_hours} h` : 'not enough data'}</b></p>
          <h3>Most-supported issues</h3>
          {stats.most_upvoted.length === 0 ? <p className="muted">No upvotes yet.</p> : (
            <ol className="plain-list">
              {stats.most_upvoted.map(i => (
                <li key={i.id}><Link to={`/issues/${i.id}`}>{i.title}</Link> <span className="muted">&#9650; {i.upvotes}</span></li>
              ))}
            </ol>
          )}
        </div>
      </div>
      <div className="card">
        <h3>Latest reports</h3>
        <table className="table">
          <thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Reported</th></tr></thead>
          <tbody>{stats.recent.map(i => (
            <tr key={i.id}>
              <td className="mono">{i.public_id}</td>
              <td><Link to={`/issues/${i.id}`}>{i.title}</Link></td>
              <td><StatusBadge status={i.status} /></td>
              <td className="muted">{new Date(i.created_at).toLocaleDateString()}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </div>
  )
}
