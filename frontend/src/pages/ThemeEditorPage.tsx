import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createTheme, generateTheme, getTheme, updateTheme } from '../api/themes'
import type { MasterThemeInput } from '../types/masterTheme'

const JSON_FIELDS = [
  { key: 'character_json', label: 'Character' },
  { key: 'environment_json', label: 'Environment' },
  { key: 'visual_style_json', label: 'Visual Style' },
  { key: 'animation_rules_json', label: 'Animation Rules' },
  { key: 'music_style_json', label: 'Music Style' },
] as const

type JsonFieldKey = (typeof JSON_FIELDS)[number]['key']

const DEFAULT_THEME = {
  name: 'Lone Samurai',
  concept: 'A solitary samurai living peacefully in rural feudal Japan.',
  character: {
    description: 'A calm Japanese samurai',
    clothing: 'traditional indigo kimono and hakama',
  },
  environment: {
    location: 'rural feudal Japan',
    elements: ['mountains', 'bamboo', 'traditional houses', 'streams', 'cherry trees'],
  },
  visual_style: {
    style: 'cinematic realistic',
    mood: 'peaceful and contemplative',
    lighting: 'soft natural light',
  },
  animation_rules: {
    movement: 'slow and subtle',
    camera: 'mostly static',
    loop_friendly: true,
  },
  music_style: {
    mood: 'peaceful and meditative',
    instruments: ['shakuhachi', 'koto', 'soft strings'],
    vocals: false,
    tempo: '55-70 BPM',
  },
}

function ThemeEditorPage() {
  const { id } = useParams()
  const isEditing = id !== undefined
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [concept, setConcept] = useState('')
  const [jsonFields, setJsonFields] = useState<Record<JsonFieldKey, string>>({
    character_json: '',
    environment_json: '',
    visual_style_json: '',
    animation_rules_json: '',
    music_style_json: '',
  })
  const [jsonErrors, setJsonErrors] = useState<Partial<Record<JsonFieldKey, string>>>({})
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [idea, setIdea] = useState('')
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  useEffect(() => {
    if (!isEditing) return
    getTheme(Number(id))
      .then((theme) => {
        setName(theme.name)
        setConcept(theme.concept)
        setJsonFields({
          character_json: theme.character_json ? JSON.stringify(theme.character_json, null, 2) : '',
          environment_json: theme.environment_json ? JSON.stringify(theme.environment_json, null, 2) : '',
          visual_style_json: theme.visual_style_json ? JSON.stringify(theme.visual_style_json, null, 2) : '',
          animation_rules_json: theme.animation_rules_json
            ? JSON.stringify(theme.animation_rules_json, null, 2)
            : '',
          music_style_json: theme.music_style_json ? JSON.stringify(theme.music_style_json, null, 2) : '',
        })
      })
      .catch((err) => setError(err.message))
  }, [id, isEditing])

  function parseJsonFields(): Record<JsonFieldKey, Record<string, unknown> | null> | null {
    const parsed = {} as Record<JsonFieldKey, Record<string, unknown> | null>
    const errors: Partial<Record<JsonFieldKey, string>> = {}

    for (const field of JSON_FIELDS) {
      const raw = jsonFields[field.key].trim()
      if (raw === '') {
        parsed[field.key] = null
        continue
      }
      try {
        parsed[field.key] = JSON.parse(raw)
      } catch {
        errors[field.key] = 'Invalid JSON'
      }
    }

    setJsonErrors(errors)
    return Object.keys(errors).length > 0 ? null : parsed
  }

  async function handleGenerate() {
    if (!idea.trim()) return
    setGenerateError(null)
    setGenerating(true)
    try {
      const draft = await generateTheme(idea.trim())
      setName(draft.name)
      setConcept(draft.concept)
      setJsonFields({
        character_json: JSON.stringify(draft.character, null, 2),
        environment_json: JSON.stringify(draft.environment, null, 2),
        visual_style_json: JSON.stringify(draft.visual_style, null, 2),
        animation_rules_json: JSON.stringify(draft.animation_rules, null, 2),
        music_style_json: JSON.stringify(draft.music_style, null, 2),
      })
      setJsonErrors({})
    } catch (err) {
      setGenerateError((err as Error).message)
    } finally {
      setGenerating(false)
    }
  }

  function handleUseDefault() {
    setName(DEFAULT_THEME.name)
    setConcept(DEFAULT_THEME.concept)
    setJsonFields({
      character_json: JSON.stringify(DEFAULT_THEME.character, null, 2),
      environment_json: JSON.stringify(DEFAULT_THEME.environment, null, 2),
      visual_style_json: JSON.stringify(DEFAULT_THEME.visual_style, null, 2),
      animation_rules_json: JSON.stringify(DEFAULT_THEME.animation_rules, null, 2),
      music_style_json: JSON.stringify(DEFAULT_THEME.music_style, null, 2),
    })
    setJsonErrors({})
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    const parsedJson = parseJsonFields()
    if (parsedJson === null) return

    const payload: MasterThemeInput = {
      name,
      concept,
      ...parsedJson,
    }

    setSaving(true)
    try {
      if (isEditing) {
        await updateTheme(Number(id), payload)
      } else {
        await createTheme(payload)
      }
      navigate('/')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page">
      <h1>{isEditing ? 'Edit Master Theme' : 'New Master Theme'}</h1>

      {error && <p className="error">{error}</p>}

      {!isEditing && (
        <button type="button" onClick={handleUseDefault}>
          Use Default Theme (Lone Samurai)
        </button>
      )}

      {!isEditing && (
        <div className="generate-box">
          <label>
            Generate from an idea (optional)
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              rows={2}
              placeholder="A lonely wizard living in a mountain tower."
            />
          </label>
          <button type="button" onClick={handleGenerate} disabled={generating || !idea.trim()}>
            {generating ? 'Generating...' : 'Generate'}
          </button>
          {generateError && <p className="error">{generateError}</p>}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form">
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>

        <label>
          Concept
          <textarea
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            rows={3}
            required
          />
        </label>

        {JSON_FIELDS.map((field) => (
          <label key={field.key}>
            {field.label} (JSON, optional)
            <textarea
              value={jsonFields[field.key]}
              onChange={(e) =>
                setJsonFields((prev) => ({ ...prev, [field.key]: e.target.value }))
              }
              rows={4}
              placeholder="{}"
            />
            {jsonErrors[field.key] && <span className="error">{jsonErrors[field.key]}</span>}
          </label>
        ))}

        <div className="form-actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button type="button" onClick={() => navigate('/')}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default ThemeEditorPage
