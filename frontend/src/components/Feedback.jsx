export function Spinner({ label = 'Loading…' }) {
  return <div className="page-center"><div className="spinner" /><p className="muted">{label}</p></div>
}

export function EmptyState({ title, hint }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">&#9634;</div>
      <h3>{title}</h3>
      {hint && <p className="muted">{hint}</p>}
    </div>
  )
}

export function ErrorBox({ message, onRetry }) {
  if (!message) return null
  return (
    <div className="alert alert-error" role="alert">
      {message}
      {onRetry && <button className="btn btn-sm btn-ghost" onClick={onRetry}>Retry</button>}
    </div>
  )
}

export function SuccessBox({ message }) {
  if (!message) return null
  return <div className="alert alert-success" role="status">{message}</div>
}
