import './Cart.css'

function Cart({ items, onRemove, onClear, onConfirm }) {
    return (
        <div className="cart">
            <div className="cart-header">
                <h2>🛒 Carrito</h2>
                <span className="cart-badge">{items.length}</span>
            </div>

            <div className="cart-items">
                {items.length > 0 ? (
                    items.map((item, index) => (
                        <div key={index} className="cart-item">
                            <button
                                className="remove-btn"
                                onClick={() => onRemove(index)}
                            >
                                ×
                            </button>
                            <div className="cart-item-content">
                                <h4>{item.horario.nombre_clase || item.tiquetera.nombre_centro_entrenamiento}</h4>
                                <p>📍 {item.tiquetera.nombre_sede}</p>
                                <p>📅 {item.fecha}</p>
                                <p>🕐 {item.horario.hora_inicio} - {item.horario.hora_fin}</p>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="cart-empty">
                        <div className="empty-icon">🛒</div>
                        <p>Tu carrito está vacío</p>
                        <p className="empty-subtitle">Selecciona actividades y horarios</p>
                    </div>
                )}
            </div>

            {items.length > 0 && (
                <div className="cart-footer">
                    <div className="cart-summary">
                        <span>Total de reservas:</span>
                        <span className="cart-total">{items.length}</span>
                    </div>

                    <div className="cart-actions">
                        <button
                            className="btn btn-success btn-block"
                            onClick={onConfirm}
                        >
                            ✅ Confirmar Todas
                        </button>
                        <button
                            className="btn btn-secondary btn-block"
                            onClick={onClear}
                        >
                            🗑️ Limpiar Carrito
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Cart
