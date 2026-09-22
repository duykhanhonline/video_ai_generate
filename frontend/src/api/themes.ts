import { apiRequest } from './client'
import type { MasterTheme, MasterThemeDraft, MasterThemeInput } from '../types/masterTheme'

export function listThemes(): Promise<MasterTheme[]> {
  return apiRequest('/api/themes')
}

export function getTheme(id: number): Promise<MasterTheme> {
  return apiRequest(`/api/themes/${id}`)
}

export function createTheme(input: MasterThemeInput): Promise<MasterTheme> {
  return apiRequest('/api/themes', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateTheme(id: number, input: Partial<MasterThemeInput>): Promise<MasterTheme> {
  return apiRequest(`/api/themes/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function deleteTheme(id: number): Promise<void> {
  return apiRequest(`/api/themes/${id}`, { method: 'DELETE' })
}

export function generateTheme(idea: string): Promise<MasterThemeDraft> {
  return apiRequest('/api/themes/generate', {
    method: 'POST',
    body: JSON.stringify({ idea }),
  })
}
