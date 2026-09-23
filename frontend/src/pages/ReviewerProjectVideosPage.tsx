import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { listProjectCompletedVideos, getProject } from '../api/projects'
import { API_URL } from '../api/client'
import type { ProjectCompletedVideo } from '../types/completedVideo'
import type { Project } from '../types/project'

function ReviewerProjectVideosPage() {
  const { id } = useParams()
  const projectId = Number(id)

  const [project, setProject] = useState<Project | null>(null)
  const [videos, setVideos] = useState<ProjectCompletedVideo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([getProject(projectId), listProjectCompletedVideos(projectId)])
      .then(([proj, videoList]) => {
        setProject(proj)
        setVideos(videoList)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [projectId])

  return (
    <div className="page">
      <div className="page-header">
        <h1>{project ? `${project.name} — Completed Videos` : 'Completed Videos'}</h1>
        <Link to="/reviewer">Back to Review</Link>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}
      {!loading && videos.length === 0 && <p>No completed videos yet.</p>}

      {videos.length > 0 && (
        <div className="video-thumbnail-grid">
          {videos.map((video) => (
            <div key={video.id} className="video-thumbnail-card">
              <video
                controls
                className="video-thumbnail-player"
                src={`${API_URL}/media/${video.file_path}`}
              />
              <p className="video-thumbnail-label">{video.clip_activity}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ReviewerProjectVideosPage
