import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { deleteTheme, listThemes } from '../api/themes'
import type { MasterTheme } from '../types/masterTheme'

function ThemesPage() {
  const [themes, setThemes] = useState<MasterTheme[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  function loadThemes() {
    setLoading(true)
    listThemes()
      .then(setThemes)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadThemes()
  }, [])

  async function handleDelete(id: number) {
    if (!confirm('Delete this master theme?')) return
    try {
      await deleteTheme(id)
      setThemes((prev) => prev.filter((t) => t.id !== id))
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Master Themes</h1>
        <Link className="button" to="/themes/new">
          New Theme
        </Link>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && themes.length === 0 && <p>No master themes yet.</p>}

      {!loading && themes.length > 0 && (
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Concept</th>
                <th>Updated</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {themes.map((theme) => (
                <tr key={theme.id}>
                  <td>{theme.name}</td>
                  <td>{theme.concept}</td>
                  <td>{new Date(theme.updated_at).toLocaleString()}</td>
                  <td className="row-actions">
                    <Link to={`/themes/${theme.id}`}>Edit</Link>
                    <button onClick={() => handleDelete(theme.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default ThemesPage
