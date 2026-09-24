import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { listProjectCompletedVideos, getProject } from '../api/projects'
import { listVideoFeedback, saveVideoFeedback } from '../api/clips'
import { API_URL } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import type { ProjectCompletedVideo } from '../types/completedVideo'
import type { Project } from '../types/project'
import type { VideoFeedback } from '../types/videoFeedback'

function ReviewerProjectVideosPage() {
  const { id } = useParams()
  const projectId = Number(id)
  const { user } = useAuth()

  const [project, setProject] = useState<Project | null>(null)
  const [videos, setVideos] = useState<ProjectCompletedVideo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [feedbackByVideo, setFeedbackByVideo] = useState<Record<number, VideoFeedback[]>>({})
  const [feedbackDrafts, setFeedbackDrafts] = useState<Record<number, string>>({})
  const [savingFeedbackId, setSavingFeedbackId] = useState<number | null>(null)
  const [feedbackErrors, setFeedbackErrors] = useState<Record<number, string>>({})

  useEffect(() => {
    Promise.all([getProject(projectId), listProjectCompletedVideos(projectId)])
      .then(async ([proj, videoList]) => {
        setProject(proj)
        setVideos(videoList)

        const feedbackLists = await Promise.all(
          videoList.map((video) => listVideoFeedback(video.id)),
        )
        const feedbackMap: Record<number, VideoFeedback[]> = {}
        const draftMap: Record<number, string> = {}
        videoList.forEach((video, index) => {
          feedbackMap[video.id] = feedbackLists[index]
          const ownFeedback = feedbackLists[index].find((fb) => fb.reviewer_id === user?.id)
          if (ownFeedback) draftMap[video.id] = ownFeedback.feedback_text
        })
        setFeedbackByVideo(feedbackMap)
        setFeedbackDrafts(draftMap)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [projectId, user?.id])

  async function handleSaveFeedback(videoId: number) {
    const text = (feedbackDrafts[videoId] ?? '').trim()
    if (!text) return

    setSavingFeedbackId(videoId)
    setFeedbackErrors((prev) => {
      const next = { ...prev }
      delete next[videoId]
      return next
    })
    try {
      const saved = await saveVideoFeedback(videoId, text)
      setFeedbackByVideo((prev) => {
        const existing = prev[videoId] ?? []
        const withoutOwn = existing.filter((fb) => fb.reviewer_id !== saved.reviewer_id)
        return { ...prev, [videoId]: [saved, ...withoutOwn] }
      })
    } catch (err) {
      setFeedbackErrors((prev) => ({ ...prev, [videoId]: (err as Error).message }))
    } finally {
      setSavingFeedbackId(null)
    }
  }

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

              {(feedbackByVideo[video.id]?.length ?? 0) > 0 && (
                <ul className="feedback-list">
                  {feedbackByVideo[video.id].map((fb) => (
                    <li key={fb.id} className="feedback-item">
                      <strong>{fb.reviewer_name}:</strong> {fb.feedback_text}
                    </li>
                  ))}
                </ul>
              )}

              {user?.role === 'reviewer' && (
                <div className="feedback-form">
                  <textarea
                    rows={2}
                    value={feedbackDrafts[video.id] ?? ''}
                    onChange={(e) =>
                      setFeedbackDrafts((prev) => ({ ...prev, [video.id]: e.target.value }))
                    }
                    placeholder="Leave feedback for this video..."
                  />
                  <button
                    type="button"
                    onClick={() => handleSaveFeedback(video.id)}
                    disabled={
                      savingFeedbackId === video.id || !(feedbackDrafts[video.id] ?? '').trim()
                    }
                  >
                    {savingFeedbackId === video.id ? 'Saving...' : 'Save Feedback'}
                  </button>
                  {feedbackErrors[video.id] && (
                    <p className="error">{feedbackErrors[video.id]}</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ReviewerProjectVideosPage
