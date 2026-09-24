import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import ThemesPage from './pages/ThemesPage'
import ThemeEditorPage from './pages/ThemeEditorPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectEditorPage from './pages/ProjectEditorPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import CategoriesPage from './pages/CategoriesPage'
import ReviewerDashboardPage from './pages/ReviewerDashboardPage'
import ReviewerProjectVideosPage from './pages/ReviewerProjectVideosPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import { AuthProvider, useAuth } from './auth/AuthContext'
import ProtectedRoute from './auth/ProtectedRoute'

function NavBar() {
  const { user, logout } = useAuth()

  return (
    <nav className="nav flex-wrap">
      {user?.role !== 'reviewer' && (
        <>
          <Link to="/">Themes</Link>
          <Link to="/projects">Projects</Link>
          <Link to="/categories">Categories</Link>
        </>
      )}
      {user?.role === 'reviewer' && <Link to="/reviewer">Review</Link>}
      {user && (
        <span className="nav-user">
          {user.name ?? user.email} ({user.role})
          <button type="button" onClick={logout}>
            Log Out
          </button>
        </span>
      )}
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <NavBar />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <ThemesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/themes/new"
            element={
              <ProtectedRoute>
                <ThemeEditorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/themes/:id"
            element={
              <ProtectedRoute>
                <ThemeEditorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/categories"
            element={
              <ProtectedRoute>
                <CategoriesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reviewer"
            element={
              <ProtectedRoute>
                <ReviewerDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reviewer/projects/:id"
            element={
              <ProtectedRoute>
                <ReviewerProjectVideosPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects"
            element={
              <ProtectedRoute>
                <ProjectsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/new"
            element={
              <ProtectedRoute>
                <ProjectEditorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <ProtectedRoute>
                <ProjectDetailPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
