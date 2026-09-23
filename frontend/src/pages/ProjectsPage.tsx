import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listThemes } from '../api/themes'
import { listProjects } from '../api/projects'
import { listCategories } from '../api/categories'
import type { Project } from '../types/project'

function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [themeNames, setThemeNames] = useState<Record<number, string>>({})
  const [categoryNames, setCategoryNames] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([listProjects(), listThemes(), listCategories()])
      .then(([projectList, themeList, categoryList]) => {
        setProjects(projectList)
        setThemeNames(Object.fromEntries(themeList.map((t) => [t.id, t.name])))
        setCategoryNames(Object.fromEntries(categoryList.map((c) => [c.id, c.name])))
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <div className="page-header">
        <h1>Projects</h1>
        <Link className="button" to="/projects/new">
          New Project
        </Link>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && projects.length === 0 && <p>No projects yet.</p>}

      {!loading && projects.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Master Theme</th>
              <th>Category</th>
              <th>Target Duration</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id}>
                <td>{project.name}</td>
                <td>{themeNames[project.master_theme_id] ?? project.master_theme_id}</td>
                <td>{project.category_id !== null ? (categoryNames[project.category_id] ?? '-') : '-'}</td>
                <td>{project.target_duration}s</td>
                <td>{project.status}</td>
                <td>
                  <Link to={`/projects/${project.id}`}>Open</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default ProjectsPage
