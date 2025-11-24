import { useState } from 'react'
import './Login.css'

function Login({ onLoginSuccess }) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleLogin = async () => {
        setLoading(true)
        setError('')

        try {
            const response = await fetch('/selenium_login', {
                method: 'POST',
                credentials: 'include'
            })

            if (response.ok) {
                onLoginSuccess()
            } else {
                setError('Error al iniciar sesión. Por favor, intenta de nuevo.')
            }
        } catch (err) {
            setError('Error de conexión. Verifica que el servidor esté corriendo.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>🏋️ Compensar Gym</h1>
                    <p>Sistema de Reservas</p>
                </div>

                <div className="login-content">
                    <p className="login-description">
                        Haz clic en el botón para iniciar sesión con tu cuenta de Compensar.
                        Se abrirá una ventana del navegador donde podrás ingresar tus credenciales.
                    </p>

                    {error && (
                        <div className="alert alert-error">
                            {error}
                        </div>
                    )}

                    <button
                        className="btn btn-primary btn-large"
                        onClick={handleLogin}
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="spinner-small"></span>
                                Esperando login...
                            </>
                        ) : (
                            '🔐 Iniciar Sesión'
                        )}
                    </button>

                    <div className="login-footer">
                        <p>✓ Inicio de sesión seguro</p>
                        <p>✓ Tus credenciales no se almacenan</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login
