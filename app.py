from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
from datetime import timedelta
import os
from src.auth.compensar_auth import CompensarAuth
from src.auth.compensar_auth_selenium import CompensarAuthSelenium
from src.api.compensar_api import CompensarAPI
from src.scheduler.booking_scheduler import BookingScheduler
from src.models.booking import Reserva, Tiquetera, Horario

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Diccionario para almacenar sesiones de usuario (en producción usar Redis o similar)
user_sessions = {}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirige a login_page (para compatibilidad)
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
                    'auth': auth,
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
                session['user_id'] = user_id
                session['document_number'] = 'Usuario'
                session.permanent = True
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
        deportes.setdefault(t.nombre_deporte, []).append(t)
    reservas_pendientes = user_sessions[user_id]['reservas_pendientes']
    return render_template('dashboard.html',
                           deportes=deportes,
                           reservas_pendientes=reservas_pendientes,
                           user_name=session.get('document_number'))

@app.route('/api/tiqueteras', methods=['GET'])
def api_tiqueteras():
    """API para obtener tiqueteras"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    try:
        api = user_sessions[user_id]['api']
        tiqueteras = api.get_tiqueteras()
        tiqueteras_json = []
        for t in tiqueteras:
            tiqueteras_json.append({
                'id': t.id_tiquetera,
                'nombre': t.nombre_centro_entrenamiento,
                'nombre_centro_entrenamiento': t.nombre_centro_entrenamiento,
                'nombre_sede': t.nombre_sede,
                'nombre_deporte': t.nombre_deporte,
                'ilimitado': t.ilimitado,
                'entradas': t.entradas,
                'id_escenario': t.id_escenario,
                'id_centro': t.id_centro
            })
        return jsonify({'tiqueteras': tiqueteras_json})
    except Exception as e:
        print(f'Error en api_tiqueteras: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/horarios', methods=['POST'])
def api_horarios():
    """API para obtener horarios disponibles"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    try:
        data = request.json
        tiquetera_id = data.get('tiquetera_id')
        fecha = data.get('fecha')
        if not tiquetera_id or not fecha:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        api = user_sessions[user_id]['api']
        tiqueteras = api.get_tiqueteras()
        tiquetera_obj = next((t for t in tiqueteras if str(t.id_tiquetera) == str(tiquetera_id)), None)
        if not tiquetera_obj:
            return jsonify({'error': 'Tiquetera no encontrada'}), 404
        horarios = api.get_horarios(tiquetera_obj, fecha)
        horarios_dict = [{
            'fecha': h.fecha,
            'hora_inicio': h.hora_inicio,
            'hora_fin': h.hora_fin,
            'cupos_disponibles': h.cupos_disponibles,
            'id_turno': h.id_turno,
            'nombre_clase': h.nombre_clase,
            'raw_data': h.raw_data
        } for h in horarios]
        return jsonify({'horarios': horarios_dict})
    except Exception as e:
        print(f'Error en api_horarios: {e}')
        return jsonify({'error': str(e)}), 500

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
    tiquetera = next((t for t in tiqueteras if t.id == int(tiquetera_id)), None)
    if not tiquetera:
        return jsonify({'error': 'Tiquetera no encontrada'}), 404
    horario = Horario(
        fecha=horario_data['fecha'],
        hora_inicio=horario_data['hora_inicio'],
        hora_fin=horario_data['hora_fin'],
        cupos_disponibles=horario_data['cupos_disponibles'],
        id_turno=horario_data.get('id_turno')
    )
    reserva = Reserva(tiquetera=tiquetera, horario=horario)
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
    """API para confirmar y ejecutar todas las reservas pendientes, una por una"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    api = user_sessions[user_id]['api']
    data = request.json
    reservas_to_process = []
    if data and isinstance(data.get('cart'), list):
        for item in data['cart']:
            try:
                t_data = item.get('tiquetera', {})
                tiquetera = Tiquetera(
                    id=t_data.get('id'),
                    nombre_centro_entrenamiento=t_data.get('nombre_centro_entrenamiento', ''),
                    nombre_sede=t_data.get('nombre_sede', ''),
                    nombre_deporte=t_data.get('nombre_deporte', ''),
                    id_centro_entrenamiento=t_data.get('id_centro_entrenamiento', 0),
                    id_participacion_deportista=t_data.get('id_participacion_deportista', 0),
                    entradas=t_data.get('entradas', 0),
                    ilimitado=t_data.get('ilimitado', False),
                    id_tiquetera=t_data.get('id_tiquetera', 0),
                    id_escenario=t_data.get('id_escenario', 0),
                    id_centro=t_data.get('id_centro', 0)
                )
                h_data = item.get('horario', {})
                horario = Horario(
                    fecha=item.get('fecha'),
                    hora_inicio=h_data.get('hora_inicio'),
                    hora_fin=h_data.get('hora_fin'),
                    cupos_disponibles=h_data.get('cupos_disponibles'),
                    id_turno=h_data.get('id_turno'),
                    nombre_clase=h_data.get('nombre_clase', ''),
                    raw_data=h_data.get('raw_data')
                )
                reservas_to_process.append(Reserva(tiquetera, horario))
            except Exception as e:
                print(f"Error reconstruyendo reserva: {e}")
                continue
    else:
        pendientes = user_sessions[user_id].get('reservas_pendientes', [])
        if not pendientes:
            return jsonify({'error': 'No hay reservas pendientes'}), 400
        reservas_to_process = [r['reserva_obj'] for r in pendientes]
    if not reservas_to_process:
        return jsonify({'error': 'No se pudieron procesar las reservas'}), 400
    exitosas = 0
    fallidas = 0
    for reserva in reservas_to_process:
        if api.realizar_reserva(reserva):
            exitosas += 1
        else:
            fallidas += 1
    # Limpiar pendientes
    user_sessions[user_id]['reservas_pendientes'] = []
    return jsonify({
        'success': True,
        'exitosas': exitosas,
        'fallidas': fallidas,
        'total': exitosas + fallidas
    })

@app.route('/api/limpiar_reservas', methods=['POST'])
def limpiar_reservas():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    user_id = session['user_id']
    if user_id not in user_sessions:
        return jsonify({'error': 'Sesión expirada'}), 401
    user_sessions[user_id]['reservas_pendientes'] = []
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
