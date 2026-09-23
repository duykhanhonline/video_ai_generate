import { apiRequest } from './client'
import type { Category } from '../types/category'

export function listCategories(): Promise<Category[]> {
  return apiRequest('/api/categories')
}

export function createCategory(name: string): Promise<Category> {
  return apiRequest('/api/categories', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function deleteCategory(categoryId: number): Promise<void> {
  return apiRequest(`/api/categories/${categoryId}`, { method: 'DELETE' })
}
