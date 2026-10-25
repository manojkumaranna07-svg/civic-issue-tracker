export const STATUS_COLORS = {
  'Reported': 'badge-amber',
  'Under Review': 'badge-blue',
  'In Progress': 'badge-violet',
  'Resolved': 'badge-green',
  'Rejected': 'badge-red',
}

export default function StatusBadge({ status }) {
  return <span className={`badge ${STATUS_COLORS[status] || 'badge-grey'}`}>{status}</span>
}
