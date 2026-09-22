import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { generateActivities, getProject, listClips, createClips } from '../api/projects'
import {
  generateImagePrompt,
  generateClipImage,
  generateVideoPrompt,
  uploadClipVideo,
  updateClip,
} from '../api/clips'
import { getJob } from '../api/jobs'
import { getAsset } from '../api/assets'
import { API_URL } from '../api/client'
import type { Project } from '../types/project'
import type { Clip } from '../types/clip'
import type { Job } from '../types/job'

function ProjectDetailPage() {
  const { id } = useParams()
  const projectId = Number(id)

  const [project, setProject] = useState<Project | null>(null)
  const [clips, setClips] = useState<Clip[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [count, setCount] = useState(10)
  const [activities, setActivities] = useState<string[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  const [addingClips, setAddingClips] = useState(false)
  const [addClipsError, setAddClipsError] = useState<string | null>(null)

  const [promptGeneratingId, setPromptGeneratingId] = useState<number | null>(null)
  const [promptErrors, setPromptErrors] = useState<Record<number, string>>({})

  const [imageGenerating, setImageGenerating] = useState<Set<number>>(new Set())
  const [imageErrors, setImageErrors] = useState<Record<number, string>>({})
  const [assetUrls, setAssetUrls] = useState<Record<number, string>>({})

  const [approvingId, setApprovingId] = useState<number | null>(null)
  const [approveErrors, setApproveErrors] = useState<Record<number, string>>({})

  const [videoPromptGeneratingId, setVideoPromptGeneratingId] = useState<number | null>(null)
  const [videoPromptErrors, setVideoPromptErrors] = useState<Record<number, string>>({})

  const [videoUploadingId, setVideoUploadingId] = useState<number | null>(null)
  const [videoUploadErrors, setVideoUploadErrors] = useState<Record<number, string>>({})

  useEffect(() => {
    Promise.all([getProject(projectId), listClips(projectId)])
      .then(([proj, clipList]) => {
        setProject(proj)
        setClips(clipList)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [projectId])

  useEffect(() => {
    clips.forEach((clip) => {
      const assetIds = [clip.image_asset_id, clip.video_asset_id].filter(
        (assetId): assetId is number => assetId !== null && !(assetId in assetUrls),
      )
      assetIds.forEach((assetId) => {
        getAsset(assetId)
          .then((asset) => {
            setAssetUrls((prev) => ({ ...prev, [assetId]: `${API_URL}/media/${asset.file_path}` }))
          })
          .catch(() => {
            // Non-critical: thumbnail/player just won't render.
          })
      })
    })
  }, [clips, assetUrls])

  async function handleGenerate() {
    setGenerateError(null)
    setGenerating(true)
    try {
      const result = await generateActivities(projectId, count)
      setActivities(result.activities)
      setSelected(new Set())
    } catch (err) {
      setGenerateError((err as Error).message)
    } finally {
      setGenerating(false)
    }
  }

  function toggleSelected(activity: string) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(activity)) {
        next.delete(activity)
      } else {
        next.add(activity)
      }
      return next
    })
  }

  async function handleAddSelected() {
    if (selected.size === 0) return
    setAddClipsError(null)
    setAddingClips(true)
    try {
      const newClips = await createClips(projectId, Array.from(selected))
      setClips((prev) => [...prev, ...newClips])
      setActivities((prev) => prev.filter((a) => !selected.has(a)))
      setSelected(new Set())
    } catch (err) {
      setAddClipsError((err as Error).message)
    } finally {
      setAddingClips(false)
    }
  }

  async function handleGenerateImagePrompt(clipId: number) {
    setPromptGeneratingId(clipId)
    setPromptErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await generateImagePrompt(clipId)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
    } catch (err) {
      setPromptErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setPromptGeneratingId(null)
    }
  }

  async function pollJob(jobId: number): Promise<Job> {
    for (;;) {
      const job = await getJob(jobId)
      if (job.status === 'COMPLETED' || job.status === 'FAILED') {
        return job
      }
      await new Promise((resolve) => setTimeout(resolve, 1500))
    }
  }

  async function handleGenerateImage(clipId: number, force: boolean) {
    setImageGenerating((prev) => new Set(prev).add(clipId))
    setImageErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const job = await generateClipImage(clipId, force)
      const finalJob = await pollJob(job.id)
      if (finalJob.status === 'FAILED') {
        setImageErrors((prev) => ({
          ...prev,
          [clipId]: finalJob.error_message ?? 'Image generation failed',
        }))
      } else {
        const updatedClips = await listClips(projectId)
        setClips(updatedClips)
      }
    } catch (err) {
      setImageErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setImageGenerating((prev) => {
        const next = new Set(prev)
        next.delete(clipId)
        return next
      })
    }
  }

  async function handleToggleApproved(clip: Clip) {
    setApprovingId(clip.id)
    setApproveErrors((prev) => {
      const next = { ...prev }
      delete next[clip.id]
      return next
    })
    try {
      const updatedClip = await updateClip(clip.id, !clip.approved)
      setClips((prev) => prev.map((c) => (c.id === clip.id ? updatedClip : c)))
    } catch (err) {
      setApproveErrors((prev) => ({ ...prev, [clip.id]: (err as Error).message }))
    } finally {
      setApprovingId(null)
    }
  }

  async function handleGenerateVideoPrompt(clipId: number) {
    setVideoPromptGeneratingId(clipId)
    setVideoPromptErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await generateVideoPrompt(clipId)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
    } catch (err) {
      setVideoPromptErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setVideoPromptGeneratingId(null)
    }
  }

  async function handleUploadVideo(clipId: number, file: File | undefined) {
    if (!file) return
    setVideoUploadingId(clipId)
    setVideoUploadErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await uploadClipVideo(clipId, file)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
    } catch (err) {
      setVideoUploadErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setVideoUploadingId(null)
    }
  }

  if (loading) return <div className="page">Loading...</div>
  if (error) return <div className="page error">{error}</div>
  if (!project) return null

  return (
    <div className="page">
      <div className="page-header">
        <h1>{project.name}</h1>
        <Link to="/projects">Back to Projects</Link>
      </div>

      <p>
        Target duration: {project.target_duration}s &middot; Clips: {clips.length}/
        {project.clip_count} &middot; Images approved: {clips.filter((c) => c.approved).length}/
        {clips.filter((c) => c.image_asset_id !== null).length} &middot; Status: {project.status}
      </p>

      <div className="generate-box">
        <label>
          Number of activity ideas to generate
          <input
            type="number"
            min={1}
            max={50}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>
        <button type="button" onClick={handleGenerate} disabled={generating}>
          {generating ? 'Generating...' : 'Generate Activities'}
        </button>
        {generateError && <p className="error">{generateError}</p>}
      </div>

      {activities.length > 0 && (
        <div className="checklist">
          <h2>Select activities to add as clips</h2>
          {activities.map((activity) => (
            <label key={activity} className="checklist-item">
              <input
                type="checkbox"
                checked={selected.has(activity)}
                onChange={() => toggleSelected(activity)}
              />
              {activity}
            </label>
          ))}
          <button type="button" onClick={handleAddSelected} disabled={addingClips || selected.size === 0}>
            {addingClips ? 'Adding...' : `Add Selected as Clips (${selected.size})`}
          </button>
          {addClipsError && <p className="error">{addClipsError}</p>}
        </div>
      )}

      <h2>Clips</h2>
      {clips.length === 0 && <p>No clips yet.</p>}
      {clips.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Activity</th>
              <th>Status</th>
              <th>Approved</th>
              <th>Image Prompt</th>
              <th>Image</th>
              <th>Video Prompt</th>
              <th>Video</th>
            </tr>
          </thead>
          <tbody>
            {clips.map((clip) => (
              <tr key={clip.id}>
                <td>{clip.activity}</td>
                <td>{clip.status}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={clip.approved}
                    disabled={clip.image_asset_id === null || approvingId === clip.id}
                    onChange={() => handleToggleApproved(clip)}
                    title={clip.image_asset_id === null ? 'Generate an image first' : undefined}
                  />
                  {approveErrors[clip.id] && <p className="error">{approveErrors[clip.id]}</p>}
                </td>
                <td>
                  {clip.image_prompt && (
                    <p className="image-prompt-text" title={clip.image_prompt}>
                      {clip.image_prompt}
                    </p>
                  )}
                  <button
                    type="button"
                    onClick={() => handleGenerateImagePrompt(clip.id)}
                    disabled={promptGeneratingId === clip.id}
                  >
                    {promptGeneratingId === clip.id
                      ? 'Generating...'
                      : clip.image_prompt
                        ? 'Regenerate Prompt'
                        : 'Generate Prompt'}
                  </button>
                  {promptErrors[clip.id] && <p className="error">{promptErrors[clip.id]}</p>}
                </td>
                <td>
                  {clip.image_asset_id !== null && assetUrls[clip.image_asset_id] && (
                    <a href={assetUrls[clip.image_asset_id]} target="_blank" rel="noreferrer">
                      <img
                        src={assetUrls[clip.image_asset_id]}
                        alt={clip.activity}
                        className="clip-thumbnail"
                      />
                    </a>
                  )}
                  {clip.image_prompt ? (
                    <button
                      type="button"
                      onClick={() => handleGenerateImage(clip.id, clip.image_asset_id !== null)}
                      disabled={imageGenerating.has(clip.id)}
                    >
                      {imageGenerating.has(clip.id)
                        ? 'Generating...'
                        : clip.image_asset_id
                          ? 'Regenerate Image'
                          : 'Generate Image'}
                    </button>
                  ) : (
                    <span className="hint">Generate a prompt first</span>
                  )}
                  {imageErrors[clip.id] && <p className="error">{imageErrors[clip.id]}</p>}
                </td>
                <td>
                  {clip.video_prompt && (
                    <p className="image-prompt-text" title={clip.video_prompt}>
                      {clip.video_prompt}
                    </p>
                  )}
                  {clip.approved ? (
                    <button
                      type="button"
                      onClick={() => handleGenerateVideoPrompt(clip.id)}
                      disabled={videoPromptGeneratingId === clip.id}
                    >
                      {videoPromptGeneratingId === clip.id
                        ? 'Generating...'
                        : clip.video_prompt
                          ? 'Regenerate Prompt'
                          : 'Generate Prompt'}
                    </button>
                  ) : (
                    <span className="hint">Approve the image first</span>
                  )}
                  {videoPromptErrors[clip.id] && (
                    <p className="error">{videoPromptErrors[clip.id]}</p>
                  )}
                </td>
                <td>
                  {clip.video_asset_id !== null && assetUrls[clip.video_asset_id] && (
                    <video controls className="clip-video" src={assetUrls[clip.video_asset_id]} />
                  )}
                  <button type="button" disabled title="Kling API integration is coming later">
                    Generate with Kling (coming soon)
                  </button>
                  <label className="upload-label">
                    {clip.video_asset_id ? 'Replace video:' : 'Upload video:'}
                    <input
                      type="file"
                      accept="video/*"
                      disabled={videoUploadingId === clip.id}
                      onChange={(e) => handleUploadVideo(clip.id, e.target.files?.[0])}
                    />
                  </label>
                  {videoUploadingId === clip.id && <p className="hint">Uploading...</p>}
                  {videoUploadErrors[clip.id] && (
                    <p className="error">{videoUploadErrors[clip.id]}</p>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default ProjectDetailPage
