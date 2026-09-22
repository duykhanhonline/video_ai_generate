export interface MasterTheme {
  id: number
  name: string
  concept: string
  character_json: Record<string, unknown> | null
  environment_json: Record<string, unknown> | null
  visual_style_json: Record<string, unknown> | null
  animation_rules_json: Record<string, unknown> | null
  music_style_json: Record<string, unknown> | null
  reference_image: string | null
  created_at: string
  updated_at: string
}

export interface MasterThemeInput {
  name: string
  concept: string
  character_json?: Record<string, unknown> | null
  environment_json?: Record<string, unknown> | null
  visual_style_json?: Record<string, unknown> | null
  animation_rules_json?: Record<string, unknown> | null
  music_style_json?: Record<string, unknown> | null
  reference_image?: string | null
}

export interface MasterThemeDraft {
  name: string
  concept: string
  character: Record<string, unknown>
  environment: Record<string, unknown>
  visual_style: Record<string, unknown>
  animation_rules: Record<string, unknown>
  music_style: Record<string, unknown>
}
