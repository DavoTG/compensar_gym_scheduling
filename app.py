from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import timedelta
import os
from src.auth.compensar_auth import CompensarAuth
from src.auth.compensar_auth_selenium import CompensarAuthSelenium
from src.api.compensar_api import CompensarAPI
from src.scheduler.booking_scheduler import BookingScheduler
from src.models.booking import Reserva

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Diccionario para almacenar sesiones de usuario (en producción usar Redis o similar)
user_sessions = {}

@app.route('/')
def index():
    """Página principal"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login_page')
def login_page():
    """Página de login"""
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Redirige a login_page (para compatibilidad)"""
    return redirect(url_for('login_page'))

@app.route('/selenium_login', methods=['POST'])
def selenium_login():
    """Inicia sesión usando Selenium interactivo"""
    try:
        auth = CompensarAuthSelenium()
        if auth.login_interactive():
            # Login exitoso
            try:
                user_id = auth.get_user_id()
                
                # Guardar en sesión
                session['user_id'] = user_id
                session['document_number'] = 'Usuario'
                session.permanent = True
                
                # Crear API con la sesión autenticada de Selenium
                api = CompensarAPI(auth.get_session())
                
                # Guardar objetos de API en memoria
                user_sessions[user_id] = {
                    'auth': auth, # Guardamos el objeto Selenium por si acaso
                    'api': api,
                    'scheduler': BookingScheduler(api),
                    'reservas_pendientes': []
                }
                
                flash('¡Login exitoso!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error obteniendo datos de usuario: {str(e)}', 'error')
                return redirect(url_for('login_page'))
        else:
            flash('No se pudo iniciar sesión. Intenta de nuevo.', 'error')
            return redirect(url_for('login_page'))
            
    except Exception as e:
        flash(f'Error en el proceso de login: {str(e)}', 'error')
        return redirect(url_for('login_page'))

@app.route('/verify_session', methods=['POST'])
def verify_session():
    """Verifica si el usuario tiene una sesión activa en Compensar"""
    try:
        # Crear auth object
        auth = CompensarAuth()
        
        # Copiar cookies del navegador a la sesión de requests
        for cookie_name, cookie_value in request.cookies.items():
            auth.session.cookies.set(cookie_name, cookie_value)
        
        # Intentar obtener tiqueteras para verificar autenticación
        api = CompensarAPI(auth.session)
        tiqueteras = api.get_tiqueteras()
        
        if tiqueteras and len(tiqueteras) > 0:
            # Login exitoso
            try:
                user_id = str(tiqueteras[0].id_participacion_deportista)
                
                # Guardar en sesión
                session['user_id'] = user_id
                session['document_number'] = 'Usuario'
                session.permanent = True
                
                # Guardar objetos de API en memoria
                user_sessions[user_id] = {
                    'auth': auth,
                    'api': api,
                    'scheduler': BookingScheduler(api),
                    'reservas_pendientes': []
                }
                
                flash('¡Sesión verificada exitosamente!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error al obtener información del usuario: {str(e)}', 'error')
                return redirect(url_for('login_page'))
        else:
            flash('No se detectó una sesión activa de Compensar. Por favor inicia sesión en Compensar primero.', 'error')
            return redirect(url_for('login_page'))
            
    except Exception as e:
        flash(f'Error al verificar la sesión: {str(e)}. Asegúrate de haber iniciado sesión en Compensar.', 'error')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    user_id = session.get('user_id')
    if user_id and user_id in user_sessions:
        del user_sessions[user_id]
    
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        flash('Sesión expirada. Por favor inicia sesión nuevamente.', 'warning')
        return redirect(url_for('login_page'))
    
    api = user_sessions[user_id]['api']
    tiqueteras = api.get_tiqueteras()
    
    # Agrupar por deporte
    deportes = {}
    for t in tiqueteras:
        if t.nombre_deporte not in deportes:
            deportes[t.nombre_deporte] = []
        deportes[t.nombre_deporte].append(t)
    
    reservas_pendientes = user_sessions[user_id]['reservas_pendientes']
    
    return render_template('dashboard.html', 
                         deportes=deportes, 
                         reservas_pendientes=reservas_pendientes,
                         user_name=session.get('document_number'))

@app.route('/api/horarios', methods=['POST'])
def get_horarios():
    """API para obtener horarios de una tiquetera en una fecha"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    
    data = request.json
    tiquetera_id = data.get('tiquetera_id')
    fecha = data.get('fecha')
    
    api = user_sessions[user_id]['api']
    tiqueteras = api.get_tiqueteras()
    
    # Encontrar la tiquetera
    tiquetera = next((t for t in tiqueteras if t.id == int(tiquetera_id)), None)
    
    if not tiquetera:
        return jsonify({'error': 'Tiquetera no encontrada'}), 404
    
    horarios = api.get_horarios(tiquetera, fecha)
    
    # Convertir a dict para JSON
    horarios_dict = [{
        'fecha': h.fecha,
        'hora_inicio': h.hora_inicio,
        'hora_fin': h.hora_fin,
        'cupos_disponibles': h.cupos_disponibles,
        'id_turno': h.id_turno
    } for h in horarios]
    
    return jsonify({'horarios': horarios_dict})

@app.route('/api/agregar_reserva', methods=['POST'])
def agregar_reserva():
    """API para agregar una reserva a la lista pendiente"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    
    data = request.json
    tiquetera_id = data.get('tiquetera_id')
    horario_data = data.get('horario')
    
    api = user_sessions[user_id]['api']
    tiqueteras = api.get_tiqueteras()
    
    # Encontrar la tiquetera
    tiquetera = next((t for t in tiqueteras if t.id == int(tiquetera_id)), None)
    
    if not tiquetera:
        return jsonify({'error': 'Tiquetera no encontrada'}), 404
    
    # Crear objeto Horario
    from src.models.booking import Horario
    horario = Horario(
        fecha=horario_data['fecha'],
        hora_inicio=horario_data['hora_inicio'],
        hora_fin=horario_data['hora_fin'],
        cupos_disponibles=horario_data['cupos_disponibles'],
        id_turno=horario_data.get('id_turno')
    )
    
    # Crear reserva
    reserva = Reserva(tiquetera=tiquetera, horario=horario)
    
    # Agregar a pendientes
    user_sessions[user_id]['reservas_pendientes'].append({
        'tiquetera_nombre': tiquetera.nombre_centro_entrenamiento,
        'sede': tiquetera.nombre_sede,
        'fecha': horario.fecha,
        'hora_inicio': horario.hora_inicio,
        'hora_fin': horario.hora_fin,
        'reserva_obj': reserva
    })
    
    return jsonify({
        'success': True, 
        'total_pendientes': len(user_sessions[user_id]['reservas_pendientes'])
    })

@app.route('/api/eliminar_reserva/<int:index>', methods=['DELETE'])
def eliminar_reserva(index):
    """API para eliminar una reserva pendiente"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    
    reservas = user_sessions[user_id]['reservas_pendientes']
    
    if 0 <= index < len(reservas):
        reservas.pop(index)
        return jsonify({'success': True, 'total_pendientes': len(reservas)})
    
    return jsonify({'error': 'Índice inválido'}), 400

@app.route('/api/confirmar_reservas', methods=['POST'])
def confirmar_reservas():
    """API para confirmar y ejecutar todas las reservas pendientes"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    
    api = user_sessions[user_id]['api']
    reservas_pendientes = user_sessions[user_id]['reservas_pendientes']
    
    if not reservas_pendientes:
        return jsonify({'error': 'No hay reservas pendientes'}), 400
    
    # Extraer objetos Reserva
    reservas = [r['reserva_obj'] for r in reservas_pendientes]
    
    # Ejecutar reservas
    resultado = api.realizar_reservas_multiples(reservas)
    
    # Limpiar pendientes
    user_sessions[user_id]['reservas_pendientes'] = []
    
    return jsonify({
        'success': True,
        'exitosas': resultado['exitosas'],
        'fallidas': resultado['fallidas'],
        'total': resultado['total']
    })

@app.route('/api/limpiar_reservas', methods=['POST'])
def limpiar_reservas():
    """API para limpiar todas las reservas pendientes"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    
    user_sessions[user_id]['reservas_pendientes'] = []
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
