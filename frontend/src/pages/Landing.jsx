import { Link } from 'react-router-dom'

const FEATURES = [
  ['R', 'Report issues', 'Log potholes, leaks, broken lights and more with photos and map locations.'],
  ['M', 'Live map view', 'See every verified report plotted on an OpenStreetMap-powered map.'],
  ['S', 'Community support', 'Add a "Me Too" to issues you also face so they get priority.'],
  ['A', 'Admin dashboard', 'Statuses, assignments, analytics and resolution tracking in one place.'],
]

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero">
        <h1>Report it. Track it. Get it fixed.</h1>
        <p className="hero-sub">
          Civic Issue Tracker lets communities report local problems, support each
          other's reports, and follow every issue from report to resolution.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-primary btn-lg" to="/register">Get started</Link>
          <Link className="btn btn-outline btn-lg" to="/login">I have an account</Link>
        </div>
      </section>
      <section className="feature-grid">
        {FEATURES.map(([icon, t, d]) => (
          <div className="card feature" key={t}>
            <div className="feature-icon"><span>{icon}</span></div>
            <h3>{t}</h3>
            <p className="muted">{d}</p>
          </div>
        ))}
      </section>
      <section className="sectors-strip">
        <h2>Built for every sector</h2>
        <p className="muted">
          Municipal services · Education · Healthcare · Offices · Apartments ·
          Transportation · Industry · Environment
        </p>
      </section>
    </div>
  )
}
