import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { generateActivities, getProject, listClips, createClips } from '../api/projects'
import {
  generateImagePrompt,
  generateClipImage,
  generateVideoPrompt,
  uploadClipVideo,
  updateClip,
  updateClipImagePrompt,
  updateClipImageRatio,
  updateClipReferenceImage,
  listClipImages,
  selectClipImage,
  deleteClip,
  exportClipManifest,
  uploadCompletedVideo,
  listCompletedVideos,
  deleteCompletedVideo,
} from '../api/clips'
import { getJob } from '../api/jobs'
import { getAsset } from '../api/assets'
import { listProjectMusic, uploadMusicTrack, deleteMusicTrack, updateMusicTrack } from '../api/music'
import { listRenderJobs } from '../api/render'
import { API_URL } from '../api/client'
import type { Project } from '../types/project'
import type { Clip, ImageRatio } from '../types/clip'
import type { Job } from '../types/job'
import type { Asset } from '../types/asset'
import type { MusicTrack } from '../types/musicTrack'
import type { RenderManifest } from '../types/renderManifest'
import type { CompletedVideo } from '../types/completedVideo'

const IMAGE_RATIO_OPTIONS: { value: ImageRatio; label: string }[] = [
  { value: '1024x1024', label: 'Square (1:1)' },
  { value: '1536x1024', label: '16:9 (YouTube)' },
  { value: '1024x1536', label: 'Portrait (2:3)' },
]

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

  const [promptDrafts, setPromptDrafts] = useState<Record<number, string>>({})
  const [promptSavingId, setPromptSavingId] = useState<number | null>(null)
  const [promptSaveErrors, setPromptSaveErrors] = useState<Record<number, string>>({})

  const [imageGenerating, setImageGenerating] = useState<Set<number>>(new Set())
  const [imageErrors, setImageErrors] = useState<Record<number, string>>({})
  const [assetUrls, setAssetUrls] = useState<Record<number, string>>({})

  const [ratioSavingId, setRatioSavingId] = useState<number | null>(null)
  const [ratioErrors, setRatioErrors] = useState<Record<number, string>>({})

  const [referenceDrafts, setReferenceDrafts] = useState<Record<number, string>>({})
  const [referenceSavingId, setReferenceSavingId] = useState<number | null>(null)
  const [referenceErrors, setReferenceErrors] = useState<Record<number, string>>({})

  const [imageHistory, setImageHistory] = useState<Record<number, Asset[]>>({})
  const [historyOpenId, setHistoryOpenId] = useState<number | null>(null)
  const [historyLoadingId, setHistoryLoadingId] = useState<number | null>(null)
  const [historyErrors, setHistoryErrors] = useState<Record<number, string>>({})
  const [selectingImageId, setSelectingImageId] = useState<number | null>(null)

  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const [approvingId, setApprovingId] = useState<number | null>(null)
  const [approveErrors, setApproveErrors] = useState<Record<number, string>>({})

  const [videoPromptGeneratingId, setVideoPromptGeneratingId] = useState<number | null>(null)
  const [videoPromptErrors, setVideoPromptErrors] = useState<Record<number, string>>({})

  const [videoUploadingId, setVideoUploadingId] = useState<number | null>(null)
  const [videoUploadErrors, setVideoUploadErrors] = useState<Record<number, string>>({})

  const [completedVideos, setCompletedVideos] = useState<Record<number, CompletedVideo[]>>({})
  const [completedVideosOpenId, setCompletedVideosOpenId] = useState<number | null>(null)
  const [completedVideosLoadingId, setCompletedVideosLoadingId] = useState<number | null>(null)
  const [completedVideoErrors, setCompletedVideoErrors] = useState<Record<number, string>>({})
  const [completedVideoUploadingId, setCompletedVideoUploadingId] = useState<number | null>(null)
  const [deletingCompletedVideoId, setDeletingCompletedVideoId] = useState<number | null>(null)

  const [deletingClipId, setDeletingClipId] = useState<number | null>(null)
  const [deleteClipErrors, setDeleteClipErrors] = useState<Record<number, string>>({})

  const [musicTracks, setMusicTracks] = useState<MusicTrack[]>([])
  const [musicLoading, setMusicLoading] = useState(true)
  const [musicError, setMusicError] = useState<string | null>(null)

  const [newMusicTitle, setNewMusicTitle] = useState('')
  const [newMusicFile, setNewMusicFile] = useState<File | null>(null)
  const [uploadingMusic, setUploadingMusic] = useState(false)
  const [uploadMusicError, setUploadMusicError] = useState<string | null>(null)

  const [deletingMusicId, setDeletingMusicId] = useState<number | null>(null)
  const [deleteMusicErrors, setDeleteMusicErrors] = useState<Record<number, string>>({})

  const [togglingMusicId, setTogglingMusicId] = useState<number | null>(null)
  const [toggleMusicErrors, setToggleMusicErrors] = useState<Record<number, string>>({})

  const [clipManifests, setClipManifests] = useState<Record<number, RenderManifest>>({})
  const [exportingManifestId, setExportingManifestId] = useState<number | null>(null)
  const [exportManifestErrors, setExportManifestErrors] = useState<Record<number, string>>({})

  const [renderJobs, setRenderJobs] = useState<Job[]>([])
  const [renderJobsLoading, setRenderJobsLoading] = useState(true)
  const [renderJobsError, setRenderJobsError] = useState<string | null>(null)

  useEffect(() => {
    if (!previewUrl) return
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setPreviewUrl(null)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [previewUrl])

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
    listProjectMusic(projectId)
      .then(setMusicTracks)
      .catch((err) => setMusicError(err.message))
      .finally(() => setMusicLoading(false))
  }, [projectId])

  function loadRenderJobs() {
    setRenderJobsLoading(true)
    listRenderJobs(projectId)
      .then(setRenderJobs)
      .catch((err) => setRenderJobsError(err.message))
      .finally(() => setRenderJobsLoading(false))
  }

  useEffect(() => {
    loadRenderJobs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      setPromptDrafts((prev) => {
        const next = { ...prev }
        delete next[clipId]
        return next
      })
    } catch (err) {
      setPromptErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setPromptGeneratingId(null)
    }
  }

  function handlePromptDraftChange(clipId: number, value: string) {
    setPromptDrafts((prev) => ({ ...prev, [clipId]: value }))
  }

  async function handleSavePrompt(clipId: number, prompt: string) {
    setPromptSavingId(clipId)
    setPromptSaveErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await updateClipImagePrompt(clipId, prompt)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
      setPromptDrafts((prev) => {
        const next = { ...prev }
        delete next[clipId]
        return next
      })
    } catch (err) {
      setPromptSaveErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setPromptSavingId(null)
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
        setImageHistory((prev) => {
          const next = { ...prev }
          delete next[clipId]
          return next
        })
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

  async function toggleImageHistory(clipId: number) {
    if (historyOpenId === clipId) {
      setHistoryOpenId(null)
      return
    }
    setHistoryOpenId(clipId)
    if (imageHistory[clipId]) return

    setHistoryLoadingId(clipId)
    setHistoryErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const images = await listClipImages(clipId)
      setImageHistory((prev) => ({ ...prev, [clipId]: images }))
    } catch (err) {
      setHistoryErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setHistoryLoadingId(null)
    }
  }

  async function handleSelectImage(clipId: number, assetId: number) {
    setSelectingImageId(assetId)
    setHistoryErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await selectClipImage(clipId, assetId)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
    } catch (err) {
      setHistoryErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setSelectingImageId(null)
    }
  }

  async function handleChangeRatio(clipId: number, ratio: ImageRatio) {
    setRatioSavingId(clipId)
    setRatioErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await updateClipImageRatio(clipId, ratio)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
    } catch (err) {
      setRatioErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setRatioSavingId(null)
    }
  }

  async function handleDeleteClip(clipId: number) {
    if (
      !confirm(
        'Delete this clip? This permanently removes its prompts, prompt history, reference setting, generated images, generated video, and jobs. This cannot be undone.',
      )
    ) {
      return
    }
    setDeletingClipId(clipId)
    setDeleteClipErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      await deleteClip(clipId)
      setClips((prev) => prev.filter((c) => c.id !== clipId))
    } catch (err) {
      setDeleteClipErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setDeletingClipId(null)
    }
  }

  async function handleUploadMusic(e: React.FormEvent) {
    e.preventDefault()
    if (!newMusicFile || !newMusicTitle.trim()) return

    setUploadingMusic(true)
    setUploadMusicError(null)
    try {
      const track = await uploadMusicTrack(projectId, newMusicFile, newMusicTitle.trim())
      setMusicTracks((prev) => [track, ...prev])
      setNewMusicTitle('')
      setNewMusicFile(null)
    } catch (err) {
      setUploadMusicError((err as Error).message)
    } finally {
      setUploadingMusic(false)
    }
  }

  async function handleToggleMusicIncluded(trackId: number, approved: boolean) {
    setTogglingMusicId(trackId)
    setToggleMusicErrors((prev) => {
      const next = { ...prev }
      delete next[trackId]
      return next
    })
    try {
      const updated = await updateMusicTrack(trackId, approved)
      setMusicTracks((prev) => prev.map((t) => (t.id === trackId ? updated : t)))
    } catch (err) {
      setToggleMusicErrors((prev) => ({ ...prev, [trackId]: (err as Error).message }))
    } finally {
      setTogglingMusicId(null)
    }
  }

  async function handleDeleteMusic(trackId: number) {
    if (!confirm('Delete this music track? This cannot be undone.')) return

    setDeletingMusicId(trackId)
    setDeleteMusicErrors((prev) => {
      const next = { ...prev }
      delete next[trackId]
      return next
    })
    try {
      await deleteMusicTrack(trackId)
      setMusicTracks((prev) => prev.filter((t) => t.id !== trackId))
    } catch (err) {
      setDeleteMusicErrors((prev) => ({ ...prev, [trackId]: (err as Error).message }))
    } finally {
      setDeletingMusicId(null)
    }
  }

  async function handleExportClipManifest(clipId: number) {
    setExportingManifestId(clipId)
    setExportManifestErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const result = await exportClipManifest(clipId)
      setClipManifests((prev) => ({ ...prev, [clipId]: result }))
    } catch (err) {
      setExportManifestErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setExportingManifestId(null)
    }
  }

  function handleReferenceDraftChange(clipId: number, value: string) {
    setReferenceDrafts((prev) => ({ ...prev, [clipId]: value }))
  }

  async function handleSaveReference(clipId: number, path: string) {
    setReferenceSavingId(clipId)
    setReferenceErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const updatedClip = await updateClipReferenceImage(clipId, path)
      setClips((prev) => prev.map((c) => (c.id === clipId ? updatedClip : c)))
      setReferenceDrafts((prev) => {
        const next = { ...prev }
        delete next[clipId]
        return next
      })
    } catch (err) {
      setReferenceErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setReferenceSavingId(null)
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

  async function toggleCompletedVideos(clipId: number) {
    if (completedVideosOpenId === clipId) {
      setCompletedVideosOpenId(null)
      return
    }
    setCompletedVideosOpenId(clipId)
    if (completedVideos[clipId]) return

    setCompletedVideosLoadingId(clipId)
    setCompletedVideoErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const videos = await listCompletedVideos(clipId)
      setCompletedVideos((prev) => ({ ...prev, [clipId]: videos }))
    } catch (err) {
      setCompletedVideoErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setCompletedVideosLoadingId(null)
    }
  }

  async function handleUploadCompletedVideo(clipId: number, file: File | undefined) {
    if (!file) return
    setCompletedVideoUploadingId(clipId)
    setCompletedVideoErrors((prev) => {
      const next = { ...prev }
      delete next[clipId]
      return next
    })
    try {
      const video = await uploadCompletedVideo(clipId, file)
      setCompletedVideos((prev) => ({
        ...prev,
        [clipId]: [video, ...(prev[clipId] ?? [])],
      }))
      setCompletedVideosOpenId(clipId)
    } catch (err) {
      setCompletedVideoErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setCompletedVideoUploadingId(null)
    }
  }

  async function handleDeleteCompletedVideo(clipId: number, videoId: number) {
    if (!confirm('Delete this completed video? This cannot be undone.')) return

    setDeletingCompletedVideoId(videoId)
    try {
      await deleteCompletedVideo(videoId)
      setCompletedVideos((prev) => ({
        ...prev,
        [clipId]: (prev[clipId] ?? []).filter((v) => v.id !== videoId),
      }))
    } catch (err) {
      setCompletedVideoErrors((prev) => ({ ...prev, [clipId]: (err as Error).message }))
    } finally {
      setDeletingCompletedVideoId(null)
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
              <th>Actions</th>
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
                    disabled={
                      (clip.image_asset_id === null && clip.video_asset_id === null) ||
                      approvingId === clip.id
                    }
                    onChange={() => handleToggleApproved(clip)}
                    title={
                      clip.image_asset_id === null && clip.video_asset_id === null
                        ? 'Generate an image or upload a video first'
                        : undefined
                    }
                  />
                  {approveErrors[clip.id] && <p className="error">{approveErrors[clip.id]}</p>}
                </td>
                <td>
                  <textarea
                    className="image-prompt-input"
                    rows={3}
                    value={promptDrafts[clip.id] ?? clip.image_prompt ?? ''}
                    onChange={(e) => handlePromptDraftChange(clip.id, e.target.value)}
                    placeholder="No prompt yet. Generate one or type your own."
                  />
                  <div className="row-actions">
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
                    <button
                      type="button"
                      onClick={() => handleSavePrompt(clip.id, promptDrafts[clip.id] ?? '')}
                      disabled={
                        promptSavingId === clip.id ||
                        !(clip.id in promptDrafts) ||
                        promptDrafts[clip.id] === (clip.image_prompt ?? '')
                      }
                    >
                      {promptSavingId === clip.id ? 'Saving...' : 'Save Prompt'}
                    </button>
                  </div>
                  {promptErrors[clip.id] && <p className="error">{promptErrors[clip.id]}</p>}
                  {promptSaveErrors[clip.id] && <p className="error">{promptSaveErrors[clip.id]}</p>}
                </td>
                <td>
                  {clip.image_asset_id !== null && assetUrls[clip.image_asset_id] && (
                    <button
                      type="button"
                      className="thumbnail-button"
                      onClick={() => setPreviewUrl(assetUrls[clip.image_asset_id!])}
                    >
                      <img
                        src={assetUrls[clip.image_asset_id]}
                        alt={clip.activity}
                        className="clip-thumbnail"
                      />
                    </button>
                  )}
                  <label className="ratio-label">
                    Reference image path:
                    <input
                      type="text"
                      className="reference-input"
                      value={referenceDrafts[clip.id] ?? clip.reference_image_path ?? ''}
                      onChange={(e) => handleReferenceDraftChange(clip.id, e.target.value)}
                      placeholder="projects/3/images/clip_3_xyz.png"
                    />
                  </label>
                  <div className="row-actions">
                    <button
                      type="button"
                      onClick={() =>
                        handleSaveReference(clip.id, referenceDrafts[clip.id] ?? '')
                      }
                      disabled={
                        referenceSavingId === clip.id ||
                        !(clip.id in referenceDrafts) ||
                        referenceDrafts[clip.id] === (clip.reference_image_path ?? '')
                      }
                    >
                      {referenceSavingId === clip.id ? 'Saving...' : 'Save Reference'}
                    </button>
                  </div>
                  {referenceErrors[clip.id] && <p className="error">{referenceErrors[clip.id]}</p>}
                  <label className="ratio-label">
                    Ratio:
                    <select
                      value={clip.image_ratio}
                      disabled={ratioSavingId === clip.id}
                      onChange={(e) => handleChangeRatio(clip.id, e.target.value as ImageRatio)}
                    >
                      {IMAGE_RATIO_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  {ratioErrors[clip.id] && <p className="error">{ratioErrors[clip.id]}</p>}
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

                  <button
                    type="button"
                    className="history-toggle"
                    onClick={() => toggleImageHistory(clip.id)}
                  >
                    {historyOpenId === clip.id ? 'Hide Previous Images' : 'Previous Images'}
                  </button>
                  {historyOpenId === clip.id && (
                    <div className="image-history">
                      {historyLoadingId === clip.id && <p className="hint">Loading...</p>}
                      {historyErrors[clip.id] && <p className="error">{historyErrors[clip.id]}</p>}
                      {imageHistory[clip.id]?.length === 0 && (
                        <p className="hint">No previous images.</p>
                      )}
                      {imageHistory[clip.id]?.map((asset) => (
                        <button
                          key={asset.id}
                          type="button"
                          className={
                            asset.id === clip.image_asset_id
                              ? 'image-history-item selected'
                              : 'image-history-item'
                          }
                          onClick={() => handleSelectImage(clip.id, asset.id)}
                          disabled={asset.id === clip.image_asset_id || selectingImageId === asset.id}
                          title={
                            asset.id === clip.image_asset_id ? 'Currently selected' : 'Use this image'
                          }
                        >
                          <img src={`${API_URL}/media/${asset.file_path}`} alt="" />
                        </button>
                      ))}
                    </div>
                  )}
                </td>
                <td>
                  {clip.video_prompt && (
                    <textarea
                      className="image-prompt-input"
                      rows={3}
                      value={clip.video_prompt}
                      readOnly
                    />
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

                  <label className="upload-label">
                    Upload completed video:
                    <input
                      type="file"
                      accept="video/*"
                      disabled={completedVideoUploadingId === clip.id}
                      onChange={(e) => handleUploadCompletedVideo(clip.id, e.target.files?.[0])}
                    />
                  </label>
                  {completedVideoUploadingId === clip.id && <p className="hint">Uploading...</p>}

                  <button
                    type="button"
                    className="history-toggle"
                    onClick={() => toggleCompletedVideos(clip.id)}
                  >
                    {completedVideosOpenId === clip.id
                      ? 'Hide Completed Videos'
                      : 'Completed Videos'}
                  </button>
                  {completedVideoErrors[clip.id] && (
                    <p className="error">{completedVideoErrors[clip.id]}</p>
                  )}
                  {completedVideosOpenId === clip.id && (
                    <div className="completed-videos-list">
                      {completedVideosLoadingId === clip.id && <p className="hint">Loading...</p>}
                      {completedVideos[clip.id]?.length === 0 && (
                        <p className="hint">No completed videos yet.</p>
                      )}
                      {completedVideos[clip.id]?.map((video) => (
                        <div key={video.id} className="completed-video-item">
                          <video
                            controls
                            className="clip-video"
                            src={`${API_URL}/media/${video.file_path}`}
                          />
                          <button
                            type="button"
                            className="delete-clip-button"
                            onClick={() => handleDeleteCompletedVideo(clip.id, video.id)}
                            disabled={deletingCompletedVideoId === video.id}
                          >
                            {deletingCompletedVideoId === video.id ? 'Deleting...' : 'Delete'}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </td>
                <td>
                  <button
                    type="button"
                    onClick={() => handleExportClipManifest(clip.id)}
                    disabled={
                      !clip.approved ||
                      clip.video_asset_id === null ||
                      exportingManifestId === clip.id
                    }
                    title={
                      !clip.approved || clip.video_asset_id === null
                        ? 'Approve a generated video first'
                        : undefined
                    }
                  >
                    {exportingManifestId === clip.id ? 'Exporting...' : 'Export Manifest'}
                  </button>
                  {exportManifestErrors[clip.id] && (
                    <p className="error">{exportManifestErrors[clip.id]}</p>
                  )}
                  {clipManifests[clip.id] && (
                    <p className="hint">
                      Saved to{' '}
                      <code>
                        manifest/{clipManifests[clip.id].project_id}_
                        {clipManifests[clip.id].clip_id}_manifest.json
                      </code>
                    </p>
                  )}

                  <button
                    type="button"
                    className="delete-clip-button"
                    onClick={() => handleDeleteClip(clip.id)}
                    disabled={deletingClipId === clip.id}
                  >
                    {deletingClipId === clip.id ? 'Deleting...' : 'Delete Clip'}
                  </button>
                  {deleteClipErrors[clip.id] && (
                    <p className="error">{deleteClipErrors[clip.id]}</p>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Music</h2>
      <p className="hint">
        Music is independent of individual clips and forms a shared, reusable pool for this
        project.
      </p>

      <form onSubmit={handleUploadMusic} className="music-upload-form">
        <label>
          Title
          <input
            type="text"
            value={newMusicTitle}
            onChange={(e) => setNewMusicTitle(e.target.value)}
            placeholder="Rainy atmosphere"
            required
          />
        </label>
        <label>
          Audio file
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setNewMusicFile(e.target.files?.[0] ?? null)}
            required
          />
        </label>
        <button type="submit" disabled={uploadingMusic || !newMusicFile || !newMusicTitle.trim()}>
          {uploadingMusic ? 'Uploading...' : 'Upload Track'}
        </button>
        {uploadMusicError && <p className="error">{uploadMusicError}</p>}
      </form>

      {musicError && <p className="error">{musicError}</p>}
      {musicLoading && <p>Loading music...</p>}
      {!musicLoading && musicTracks.length === 0 && <p>No music tracks yet.</p>}

      {musicTracks.length > 0 && (
        <ul className="music-list">
          {musicTracks.map((track) => (
            <li key={track.id} className="music-list-item">
              <label className="music-include-label">
                <input
                  type="checkbox"
                  checked={track.approved}
                  disabled={togglingMusicId === track.id}
                  onChange={(e) => handleToggleMusicIncluded(track.id, e.target.checked)}
                />
                Include in manifest
              </label>
              <span className="music-title">{track.title}</span>
              <audio controls src={`${API_URL}/media/${track.file_path}`} />
              {toggleMusicErrors[track.id] && (
                <p className="error">{toggleMusicErrors[track.id]}</p>
              )}
              <button
                type="button"
                className="delete-clip-button"
                onClick={() => handleDeleteMusic(track.id)}
                disabled={deletingMusicId === track.id}
              >
                {deletingMusicId === track.id ? 'Deleting...' : 'Delete'}
              </button>
              {deleteMusicErrors[track.id] && (
                <p className="error">{deleteMusicErrors[track.id]}</p>
              )}
            </li>
          ))}
        </ul>
      )}

      <h2>Render</h2>
      <p className="hint">
        Use the "Export Manifest" button on an approved clip (in the Clips table above) to write
        a manifest for that clip's video, then run your host-side render agent (outside this app)
        to build the video with your existing Python + FFmpeg pipeline.
      </p>

      <h3>Render Jobs</h3>
      <button type="button" onClick={loadRenderJobs} disabled={renderJobsLoading}>
        {renderJobsLoading ? 'Refreshing...' : 'Refresh'}
      </button>
      {renderJobsError && <p className="error">{renderJobsError}</p>}
      {!renderJobsLoading && renderJobs.length === 0 && (
        <p className="hint">
          No render jobs yet. Export a manifest, then run your render agent on the host.
        </p>
      )}

      {renderJobs.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Progress</th>
              <th>Started</th>
              <th>Completed</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {renderJobs.map((job) => (
              <tr key={job.id}>
                <td>{job.status}</td>
                <td>{job.progress}%</td>
                <td>{job.started_at ? new Date(job.started_at).toLocaleString() : '-'}</td>
                <td>{job.completed_at ? new Date(job.completed_at).toLocaleString() : '-'}</td>
                <td>{job.error_message && <span className="error">{job.error_message}</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {previewUrl && (
        <div className="modal-overlay" onClick={() => setPreviewUrl(null)}>
          <button
            type="button"
            className="modal-close"
            onClick={() => setPreviewUrl(null)}
            aria-label="Close preview"
          >
            &times;
          </button>
          <img
            src={previewUrl}
            alt="Full size preview"
            className="modal-image"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  )
}

export default ProjectDetailPage
