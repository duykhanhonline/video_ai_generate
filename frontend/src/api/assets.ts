import { apiRequest } from './client'
import type { Asset } from '../types/asset'

export function getAsset(assetId: number): Promise<Asset> {
  return apiRequest(`/api/assets/${assetId}`)
}
