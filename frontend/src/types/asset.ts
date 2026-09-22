export interface Asset {
  id: number
  project_id: number
  clip_id: number | null
  asset_type: string
  provider: string
  provider_model: string
  file_path: string
  mime_type: string
  metadata_json: Record<string, unknown> | null
  created_at: string
}
