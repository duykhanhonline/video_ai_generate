export type UserRole = 'reviewer' | 'contributor'

export interface User {
  id: number
  email: string
  name: string | null
  role: UserRole
  created_at: string
}

export interface LoginResponse {
  access_token: string
  user: User
}
