import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import ThemesPage from './pages/ThemesPage'
import ThemeEditorPage from './pages/ThemeEditorPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectEditorPage from './pages/ProjectEditorPage'
import ProjectDetailPage from './pages/ProjectDetailPage'

function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">Themes</Link>
        <Link to="/projects">Projects</Link>
      </nav>
      <Routes>
        <Route path="/" element={<ThemesPage />} />
        <Route path="/themes/new" element={<ThemeEditorPage />} />
        <Route path="/themes/:id" element={<ThemeEditorPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/new" element={<ProjectEditorPage />} />
        <Route path="/projects/:id" element={<ProjectDetailPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
