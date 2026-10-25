import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import { Link } from 'react-router-dom'

// Status-colored circle markers via divIcon: no external marker images needed.
export function statusIcon(status) {
  const colors = {
    'Reported': '#d97706', 'Under Review': '#2563eb', 'In Progress': '#7c3aed',
    'Resolved': '#16a34a', 'Rejected': '#dc2626',
  }
  const c = colors[status] || '#475569'
  return L.divIcon({
    className: 'cit-marker',
    html: `<span style="background:${c}"></span>`,
    iconSize: [18, 18], iconAnchor: [9, 9], popupAnchor: [0, -10],
  })
}

export function LocationPicker({ value, onChange }) {
  useMapEvents({
    click(e) { onChange({ lat: +e.latlng.lat.toFixed(6), lng: +e.latlng.lng.toFixed(6) }) },
  })
  return value ? <Marker position={[value.lat, value.lng]} icon={statusIcon('Under Review')} /> : null
}

// Chennai center as a neutral default view; no fabricated issue data.
export const DEFAULT_CENTER = [13.0827, 80.2707]

export default function MapView({ issues = [], center = DEFAULT_CENTER, zoom = 12, height = 480, onPick, pick }) {
  return (
    <MapContainer center={center} zoom={zoom} style={{ height, width: '100%', borderRadius: 12 }} scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {onPick && <LocationPicker value={pick} onChange={onPick} />}
      {issues.map(i => (
        <Marker key={i.id} position={[i.latitude, i.longitude]} icon={statusIcon(i.status)}>
          <Popup>
            <strong>{i.title}</strong><br />
            <small>{i.public_id} · {i.sector_name}</small><br />
            <small>Status: {i.status} · 👍 {i.upvote_count}</small><br />
            {i.id && <Link to={`/issues/${i.id}`}>Open details</Link>}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
