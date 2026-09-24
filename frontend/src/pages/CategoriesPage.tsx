import { useEffect, useState } from 'react'
import { listCategories, createCategory, deleteCategory } from '../api/categories'
import type { Category } from '../types/category'

function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [newName, setNewName] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  const [deletingId, setDeletingId] = useState<number | null>(null)

  function loadCategories() {
    setLoading(true)
    listCategories()
      .then(setCategories)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadCategories()
  }, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newName.trim()) return

    setCreating(true)
    setCreateError(null)
    try {
      const category = await createCategory(newName.trim())
      setCategories((prev) => [...prev, category].sort((a, b) => a.name.localeCompare(b.name)))
      setNewName('')
    } catch (err) {
      setCreateError((err as Error).message)
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(categoryId: number) {
    if (!confirm('Delete this category? Projects using it will keep existing, just without a category.')) {
      return
    }
    setDeletingId(categoryId)
    try {
      await deleteCategory(categoryId)
      setCategories((prev) => prev.filter((c) => c.id !== categoryId))
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="page">
      <h1>Categories</h1>

      <form onSubmit={handleCreate} className="generate-box">
        <label>
          New category name
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="e.g. Ambient, Nature, Sci-Fi"
          />
        </label>
        <button type="submit" disabled={creating || !newName.trim()}>
          {creating ? 'Adding...' : 'Add Category'}
        </button>
        {createError && <p className="error">{createError}</p>}
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}
      {!loading && categories.length === 0 && <p>No categories yet.</p>}

      {categories.length > 0 && (
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {categories.map((category) => (
                <tr key={category.id}>
                  <td>{category.name}</td>
                  <td className="row-actions">

                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default CategoriesPage
