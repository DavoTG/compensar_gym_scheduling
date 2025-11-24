import { useState, useEffect } from 'react'
import './ActivityCard.css'

function ActivityCard({ tiquetera, cart, onAddToCart }) {
    const [expanded, setExpanded] = useState(false)
    const [selectedDate, setSelectedDate] = useState('')
    const [horarios, setHorarios] = useState([])
    const [loadingHorarios, setLoadingHorarios] = useState(false)
    const [error, setError] = useState(null)

    const toggleExpand = () => {
        setExpanded(!expanded)
        if (!expanded && !selectedDate) {
            // Set default date to tomorrow
            const tomorrow = new Date()
            tomorrow.setDate(tomorrow.getDate() + 1)
            setSelectedDate(tomorrow.toISOString().split('T')[0])
        }
    }

    useEffect(() => {
        if (expanded && selectedDate) {
            loadHorarios()
        }
    }, [expanded, selectedDate])

    const loadHorarios = async () => {
        setLoadingHorarios(true)
        setError(null)
        setHorarios([])
        try {
            const response = await fetch('/api/horarios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tiquetera_id: tiquetera.id,
                    fecha: selectedDate
                })
            })
            const data = await response.json()

            if (data.error) throw new Error(data.error)

            setHorarios(data.horarios || [])
        } catch (err) {
            console.error(err)
            setError('No hay horarios disponibles para esta fecha')
        } finally {
            setLoadingHorarios(false)
        }
    }

    const handleDateChange = (e) => {
        setSelectedDate(e.target.value)
    }

    const handleTimeSelect = (horario) => {
        onAddToCart({
            tiquetera,
            horario,
            fecha: selectedDate
        })
    }

    const isReserved = (horario) => {
        if (!cart) return false
        return cart.some(item =>
            item.tiquetera.id === tiquetera.id &&
            item.fecha === selectedDate &&
            item.horario.hora_inicio === horario.hora_inicio
        )
    }

    return (
        <div className={`activity-card ${expanded ? 'expanded' : ''}`}>
            <div className="card-header" onClick={toggleExpand}>
                <div className="header-content">
                    <h3>{tiquetera.nombre_centro_entrenamiento}</h3>
                    <div className="badges">
                        <span className="badge sede">📍 {tiquetera.nombre_sede}</span>
                        {tiquetera.ilimitado ? (
                            <span className="badge ilimitado">♾️ Ilimitado</span>
                        ) : (
                            <span className="badge entradas">🎫 {tiquetera.entradas} entradas</span>
                        )}
                    </div>
                </div>
                <button className="expand-btn">
                    {expanded ? '▲' : '◀'}
                </button>
            </div>

            {expanded && (
                <div className="card-body">
                    <div className="date-selector">
                        <label>Selecciona una fecha:</label>
                        <input
                            type="date"
                            value={selectedDate}
                            onChange={handleDateChange}
                            min={new Date().toISOString().split('T')[0]}
                        />
                    </div>

                    {loadingHorarios ? (
                        <div className="loading-horarios">
                            <div className="spinner-small"></div>
                            <p>Buscando horarios...</p>
                        </div>
                    ) : error ? (
                        <div className="error-message">
                            <p>😔 {error}</p>
                        </div>
                    ) : (
                        <div className="horarios-grid">
                            {horarios.map((h, index) => {
                                const reserved = isReserved(h)
                                return (
                                    <button
                                        key={index}
                                        className={`time-slot ${reserved ? 'reserved' : ''}`}
                                        onClick={() => !reserved && handleTimeSelect(h)}
                                        disabled={reserved}
                                    >
                                        <span className="time">{h.hora_inicio} - {h.hora_fin}</span>
                                        {h.nombre_clase && <span className="class-name">{h.nombre_clase}</span>}
                                        <span className="cupos">{reserved ? 'Añadido' : `${h.cupos_disponibles} cupos`}</span>
                                    </button>
                                )
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default ActivityCard
