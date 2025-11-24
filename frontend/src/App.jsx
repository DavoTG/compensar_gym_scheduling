import { useState, useEffect } from 'react'
import './App.css'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await fetch('/api/tiqueteras', {
        credentials: 'include'
      })
      setIsAuthenticated(response.ok)
    } catch (error) {
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }

  const handleLoginSuccess = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Cargando...</p>
      </div>
    )
  }

  return (
    <div className="app">
      {!isAuthenticated ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Dashboard onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App
