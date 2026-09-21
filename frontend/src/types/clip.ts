export interface Clip {
  id: number
  project_id: number
  activity: string
  status: string
  approved: boolean
  image_prompt: string | null
  image_asset_id: number | null
  created_at: string
  updated_at: string
}
