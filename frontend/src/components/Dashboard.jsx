import { useState, useEffect } from 'react'
import './Dashboard.css'
import ActivityCard from './ActivityCard'
import Cart from './Cart'

function Dashboard({ onLogout }) {
    const [tiqueteras, setTiqueteras] = useState([])
    const [cart, setCart] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedDeporte, setSelectedDeporte] = useState('all')
    const [selectedSede, setSelectedSede] = useState('all')

    useEffect(() => {
        loadTiqueteras()
    }, [])

    const loadTiqueteras = async () => {
        try {
            const response = await fetch('/api/tiqueteras', {
                credentials: 'include'
            })
            const data = await response.json()
            setTiqueteras(data.tiqueteras || [])
        } catch (error) {
            console.error('Error loading tiqueteras:', error)
        } finally {
            setLoading(false)
        }
    }

    const addToCart = (item) => {
        setCart([...cart, item])
    }

    const removeFromCart = (index) => {
        setCart(cart.filter((_, i) => i !== index))
    }

    const clearCart = () => {
        setCart([])
    }

    const confirmCart = async () => {
        if (cart.length === 0) return

        if (!confirm(`¿Confirmar ${cart.length} reservas?`)) return

        try {
            const response = await fetch('/api/confirmar_reservas', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ cart })
            })

            const data = await response.json()

            if (data.success) {
                alert(`✅ Completado!\n\nExitosas: ${data.exitosas}\nFallidas: ${data.fallidas}`)
                clearCart()
            }
        } catch (error) {
            alert('Error al confirmar reservas')
        }
    }

    // Get unique deportes and sedes
    const deportes = [...new Set(tiqueteras.map(t => t.nombre_deporte))]
    const sedes = [...new Set(tiqueteras.map(t => t.nombre_sede))]

    // Filter tiqueteras
    const filteredTiqueteras = tiqueteras.filter(t => {
        const matchDeporte = selectedDeporte === 'all' || t.nombre_deporte === selectedDeporte
        const matchSede = selectedSede === 'all' || t.nombre_sede === selectedSede
        return matchDeporte && matchSede
    })

    // Group by deporte
    const groupedTiqueteras = filteredTiqueteras.reduce((acc, t) => {
        const deporte = t.nombre_deporte
        if (!acc[deporte]) acc[deporte] = []
        acc[deporte].push(t)
        return acc
    }, {})

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="spinner"></div>
                <p>Cargando actividades...</p>
            </div>
        )
    }

    return (
        <div className="dashboard">
            <nav className="navbar">
                <h1>🏋️ Compensar Gym</h1>
                <button className="btn btn-secondary" onClick={onLogout}>
                    Cerrar Sesión
                </button>
            </nav>

            <div className="dashboard-content">
                <div className="main-section">
                    <div className="filters">
                        <select
                            value={selectedDeporte}
                            onChange={(e) => setSelectedDeporte(e.target.value)}
                            className="filter-select"
                        >
                            <option value="all">Todos los deportes</option>
                            {deportes.map(d => (
                                <option key={d} value={d}>{d}</option>
                            ))}
                        </select>

                        <select
                            value={selectedSede}
                            onChange={(e) => setSelectedSede(e.target.value)}
                            className="filter-select"
                        >
                            <option value="all">Todas las sedes</option>
                            {sedes.map(s => (
                                <option key={s} value={s}>{s}</option>
                            ))}
                        </select>
                    </div>

                    <div className="activities-grid">
                        {Object.entries(groupedTiqueteras).map(([deporte, items]) => (
                            <div key={deporte} className="deporte-group">
                                <h2 className="deporte-title">{deporte}</h2>
                                {items.map(tiquetera => (
                                    <ActivityCard
                                        key={tiquetera.id}
                                        tiquetera={tiquetera}
                                        cart={cart}
                                        onAddToCart={addToCart}
                                    />
                                ))}
                            </div>
                        ))}

                        {filteredTiqueteras.length === 0 && (
                            <div className="empty-state">
                                <div className="empty-icon">🔍</div>
                                <p>No se encontraron actividades</p>
                            </div>
                        )}
                    </div>
                </div>

                <Cart
                    items={cart}
                    onRemove={removeFromCart}
                    onClear={clearCart}
                    onConfirm={confirmCart}
                />
            </div>
        </div>
    )
}

export default Dashboard
