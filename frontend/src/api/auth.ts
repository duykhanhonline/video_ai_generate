import { apiRequest } from './client'
import type { LoginResponse, User, UserRole } from '../types/user'

export function register(
  email: string,
  name: string,
  password: string,
  role: UserRole,
): Promise<User> {
  return apiRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, name, password, role }),
  })
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function getCurrentUser(): Promise<User> {
  return apiRequest('/api/auth/me')
}
