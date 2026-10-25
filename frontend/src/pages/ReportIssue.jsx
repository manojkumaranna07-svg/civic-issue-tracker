import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import MapView from '../components/MapView'
import { ErrorBox, SuccessBox, Spinner } from '../components/Feedback'

const MAX_MB = 5

export default function ReportIssue() {
  const navigate = useNavigate()
  const [catalog, setCatalog] = useState(null)
  const [form, setForm] = useState({ title: '', description: '', sector_id: '', category_id: '', location_text: '' })
  const [point, setPoint] = useState(null)
  const [image, setImage] = useState(null)
  const [error, setError] = useState('')
  const [done, setDone] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => { api.bootstrap().then(setCatalog).catch(e => setError(e.message)) }, [])

  const categories = catalog?.categories.filter(c => String(c.sector_id) === String(form.sector_id)) ?? []

  function onImage(e) {
    const f = e.target.files[0]
    setError('')
    if (!f) { setImage(null); return }
    if (f.size > MAX_MB * 1024 * 1024) { setError(`Image must be under ${MAX_MB} MB.`); e.target.value = ''; return }
    setImage(f)
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError(''); setBusy(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => fd.append(k, v))
      if (point) { fd.append('latitude', point.lat); fd.append('longitude', point.lng) }
      if (image) fd.append('image', image)
      const issue = await api.createIssue(fd)
      setDone(issue)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  if (!catalog) return <Spinner label="Loading form…" />

  if (done) {
    return (
      <div className="page-narrow">
        <div className="card success-panel">
          <div className="success-icon">&#10003;</div>
          <h1>Issue reported</h1>
          <p>Your tracking ID is <strong className="issue-id-lg">{done.public_id}</strong></p>
          <SuccessBox message="The issue was submitted and the admin team has been notified." />
          <div className="modal-actions center">
            <button className="btn btn-primary" onClick={() => navigate(`/issues/${done.id}`)}>View issue</button>
            <button className="btn btn-outline" onClick={() => { setDone(null); setForm({ title: '', description: '', sector_id: '', category_id: '', location_text: '' }); setPoint(null); setImage(null) }}>Report another</button>
          </div>
        </div>
      </div>
    )
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  return (
    <div className="page-narrow">
      <h1>Report an issue</h1>
      <p className="muted">Fields marked * are required. Add a photo and pin the location to help crews respond faster.</p>
      <form className="card form-card" onSubmit={onSubmit}>
        <ErrorBox message={error} />
        <label>Issue title *
          <input required minLength={4} maxLength={200} value={form.title} onChange={set('title')}
                 placeholder="e.g. Streetlight not working near the bus stop" />
        </label>
        <div className="form-row">
          <label>Sector *
            <select required value={form.sector_id}
                    onChange={e => setForm({ ...form, sector_id: e.target.value, category_id: '' })}>
              <option value="">Select sector</option>
              {catalog.sectors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </label>
          <label>Category *
            <select required value={form.category_id} onChange={set('category_id')} disabled={!form.sector_id}>
              <option value="">{form.sector_id ? 'Select category' : 'Pick a sector first'}</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>
        </div>
        <label>Description *
          <textarea required minLength={10} rows={4} value={form.description} onChange={set('description')}
                    placeholder="Describe the problem: where it is, how long it's been there, who it affects." />
        </label>
        <label>Location / address *
          <input required minLength={2} maxLength={300} value={form.location_text} onChange={set('location_text')}
                 placeholder="e.g. Ranganathan Street, T. Nagar" />
        </label>
        <fieldset className="map-pick">
          <legend>Pin on map (optional)</legend>
          <p className="muted small">Click the map to drop a pin at the exact spot. Only issues you pin on the map appear in the public map view.</p>
          <MapView height={280} onPick={setPoint} pick={point} />
          {point
            ? <p className="small">Pin: {point.lat}, {point.lng} <button type="button" className="btn btn-ghost btn-sm" onClick={() => setPoint(null)}>Clear pin</button></p>
            : <p className="muted small">No pin set — the issue will appear in lists only.</p>}
        </fieldset>
        <label>Photo (optional, JPEG/PNG/WEBP/GIF up to {MAX_MB} MB)
          <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={onImage} />
        </label>
        <button className="btn btn-primary btn-lg" disabled={busy}>{busy ? 'Submitting…' : 'Submit issue'}</button>
      </form>
    </div>
  )
}
