import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProjectReviewSummary } from '../api/projects'
import type { ProjectReviewSummary } from '../types/project'

function ReviewerDashboardPage() {
  const [rows, setRows] = useState<ProjectReviewSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getProjectReviewSummary()
      .then(setRows)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <h1>Projects to Review</h1>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}
      {!loading && rows.length === 0 && <p>No projects yet.</p>}

      {rows.length > 0 && (
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Project Name</th>
                <th>Completed Videos</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.project_id}>
                  <td>{row.category_name ?? '-'}</td>
                  <td>{row.project_name}</td>
                  <td>{row.completed_video_count}</td>
                  <td>
                    <Link to={`/reviewer/projects/${row.project_id}`}>View Videos</Link>
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

export default ReviewerDashboardPage
