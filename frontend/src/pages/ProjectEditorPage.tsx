import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listThemes } from '../api/themes'
import { createProject } from '../api/projects'
import type { MasterTheme } from '../types/masterTheme'

function ProjectEditorPage() {
  const navigate = useNavigate()

  const [themes, setThemes] = useState<MasterTheme[]>([])
  const [themesLoading, setThemesLoading] = useState(true)
  const [themesError, setThemesError] = useState<string | null>(null)

  const [masterThemeId, setMasterThemeId] = useState('')
  const [name, setName] = useState('')
  const [clipCount, setClipCount] = useState(10)
  const [musicCount, setMusicCount] = useState(10)
  const [targetDuration, setTargetDuration] = useState(3600)

  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    listThemes()
      .then((list) => {
        setThemes(list)
        if (list.length > 0) setMasterThemeId(String(list[0].id))
      })
      .catch((err) => setThemesError(err.message))
      .finally(() => setThemesLoading(false))
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (!masterThemeId) {
      setError('Select a master theme')
      return
    }

    setSaving(true)
    try {
      const project = await createProject({
        master_theme_id: Number(masterThemeId),
        name,
        clip_count: clipCount,
        music_count: musicCount,
        target_duration: targetDuration,
      })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page">
      <h1>New Project</h1>

      {error && <p className="error">{error}</p>}
      {themesError && <p className="error">{themesError}</p>}

      {!themesLoading && themes.length === 0 && (
        <p>
          No master themes yet. <a href="/themes/new">Create one first</a>.
        </p>
      )}

      {!themesLoading && themes.length > 0 && (
        <form onSubmit={handleSubmit} className="form">
          <label>
            Master Theme
            <select value={masterThemeId} onChange={(e) => setMasterThemeId(e.target.value)}>
              {themes.map((theme) => (
                <option key={theme.id} value={theme.id}>
                  {theme.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Project Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>

          <label>
            Clip Count
            <input
              type="number"
              min={0}
              value={clipCount}
              onChange={(e) => setClipCount(Number(e.target.value))}
            />
          </label>

          <label>
            Music Count
            <input
              type="number"
              min={0}
              value={musicCount}
              onChange={(e) => setMusicCount(Number(e.target.value))}
            />
          </label>

          <label>
            Target Duration (seconds)
            <input
              type="number"
              min={1}
              value={targetDuration}
              onChange={(e) => setTargetDuration(Number(e.target.value))}
              required
            />
          </label>

          <div className="form-actions">
            <button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button type="button" onClick={() => navigate('/projects')}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

export default ProjectEditorPage
