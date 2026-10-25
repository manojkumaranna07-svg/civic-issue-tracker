import { describe, it, expect, beforeEach, vi } from 'vitest'
import { api, setToken, ApiError } from '../api'

function mockFetch(status, body) {
  return vi.fn().mockResolvedValue({
    status, ok: status >= 200 && status < 300,
    json: () => Promise.resolve(body),
  })
}

describe('api client', () => {
  beforeEach(() => { setToken(null); vi.unstubAllGlobals() })

  it('attaches the bearer token to requests', async () => {
    setToken('tok123')
    const f = mockFetch(200, { ok: true })
    vi.stubGlobal('fetch', f)
    await api.me()
    expect(f.mock.calls[0][1].headers.Authorization).toBe('Bearer tok123')
  })

  it('throws ApiError with server detail on failure', async () => {
    vi.stubGlobal('fetch', mockFetch(401, { detail: 'Incorrect email or password.' }))
    await expect(api.login('a@b.co', 'x')).rejects.toMatchObject({
      status: 401, message: 'Incorrect email or password.',
    })
  })

  it('flattens pydantic validation arrays into a readable message', async () => {
    vi.stubGlobal('fetch', mockFetch(422, { detail: [{ msg: 'field required' }, { msg: 'too short' }] }))
    await expect(api.me()).rejects.toThrow('field required; too short')
  })

  it('omits empty filters from the issues query string', async () => {
    const f = mockFetch(200, { items: [], total: 0, page: 1, page_size: 12 })
    vi.stubGlobal('fetch', f)
    await api.listIssues({ q: 'pothole', status: '', page: 1 })
    expect(f.mock.calls[0][0]).toBe('/api/issues?q=pothole&page=1')
  })

  it('204 responses resolve to null', async () => {
    vi.stubGlobal('fetch', mockFetch(204, null))
    await expect(api.deleteIssue(5)).resolves.toBeNull()
  })
})
