import requests
import json
import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from config.config import Config
from src.models.booking import Tiquetera, Horario, Reserva

# Configure logging
logging.basicConfig(
    filename='server_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

class CompensarAPI:
    """Maneja las interacciones con la API de Compensar"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.participantes_data = []

    def get_tiqueteras(self) -> List[Tiquetera]:
        """
        Obtiene todas las tiqueteras (membresías) disponibles del usuario
        
        Returns:
            Lista de objetos Tiquetera
        """
        try:
            print("📋 Obteniendo tiqueteras disponibles...")
            
            # NO usar cache - siempre obtener datos frescos de la API
            print("   📡 No hay cache, consultando API...")
            
            # Endpoint correcto descubierto en el JS de la página
            # url_tiqueteras: '/sistema.php/entrenamiento/reserva/tiqueteras'
            api_url = f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/tiqueteras"
            
            # Sincronizar headers para parecer una petición AJAX de Angular
            self.session.headers.update({
                'Referer': f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/practica/libre",
                'Origin': Config.API_BASE_URL,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # 1. Obtener ID de deportista primero (ya que este endpoint sí funciona)
            deportistas_url = f"{Config.API_BASE_URL}/sistema.php/grupofamiliar/lista/json"
            print(f"   📡 Consultando ID deportista: {deportistas_url}")
            
            resp_dep = self.session.get(
                deportistas_url, 
                params={'autenticador': 'compensar'},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            
            id_participacion = None
            if resp_dep.status_code == 200:
                try:
                    data_dep = resp_dep.json()
                    if data_dep.get('personas') and len(data_dep['personas']) > 0:
                        id_participacion = data_dep['personas'][0]['id_participacion']
                        print(f"   👤 ID Deportista encontrado: {id_participacion}")
                except:
                    print("   ⚠️ No se pudo extraer ID de deportista")
            
            if not id_participacion:
                raise Exception("No se pudo obtener el ID de participante")
            
            # 2. Usar el endpoint correcto con el payload correcto
            api_url = f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/tiqueteras"
            
            # Payload correcto según lo que proporcionó el usuario
            payload = {
                "idParticipante": id_participacion,
                "historico": False
            }
            
            print(f"   🔄 Consultando tiqueteras con POST: {api_url}")
            response = self.session.post(
                api_url,
                json=payload,  # Enviar como JSON
                params={'autenticador': 'compensar'},
                headers={
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                allow_redirects=True
            )
            
            if response.status_code != 200:
                # Si falla, guardar debug
                with open('debug_api_error.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                raise Exception(f"Error al obtener tiqueteras: {response.status_code}")
            
            
            # Intentar parsear JSON
            try:
                data = response.json()
            except Exception as e:
                # Si no es JSON, guardar respuesta para debug
                with open('debug_response_content.txt', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                raise Exception(f"La respuesta no es JSON válido: {str(e)}")

            tiqueteras = []
            
            # Verificar estructura de respuesta (puede estar anidada)
            items = data.get('tiqueteras', []) if isinstance(data, dict) else []
            
            for t in items:
                tiquetera = Tiquetera(
                    id=t.get('id'),
                    nombre_centro_entrenamiento=t.get('nombre_centro_entrenamiento', 'Desconocido'),
                    nombre_sede=t.get('nombre_sede', 'Desconocida'),
                    nombre_deporte=t.get('nombre_deporte', 'Desconocido'),
                    id_centro_entrenamiento=t.get('id_centro_entrenamiento'),
                    id_participacion_deportista=t.get('id_participacion_deportista'),
                    entradas=t.get('entradas', 0),
                    ilimitado=t.get('ilimitado', False),
                    id_tiquetera=t.get('id_tiquetera', t.get('id', 0)),
                    id_escenario=t.get('id_escenario', t.get('id_centro_entrenamiento', 0)),
                    id_centro=t.get('id_centro', t.get('id_centro_entrenamiento', 0))
                )
                tiqueteras.append(tiquetera)
            
            print(f"✅ Se encontraron {len(tiqueteras)} tiqueteras")
            return tiqueteras
            
        except Exception as e:
            print(f"❌ Error obteniendo tiqueteras: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return []
    
    def get_horarios(self, tiquetera: Tiquetera, fecha: str) -> List[Horario]:
        """
        Obtiene los horarios disponibles para una tiquetera en una fecha específica
        
        Args:
            tiquetera: Objeto Tiquetera
            fecha: Fecha en formato 'YYYY-MM-DD'
            
        Returns:
            Lista de objetos Horario
        """
        try:
            print(f"🕐 Obteniendo horarios para {tiquetera.nombre_centro_entrenamiento} - {fecha}...")
            
            # Obtener datos del deportista primero
            deportistas_url = f"{Config.API_BASE_URL}/sistema.php/grupofamiliar/lista/json"
            resp_dep = self.session.get(
                deportistas_url,
                params={'autenticador': 'compensar'},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            
            participantes_data = []
            if resp_dep.status_code == 200:
                try:
                    data_dep = resp_dep.json()
                    if data_dep.get('personas') and len(data_dep['personas']) > 0:
                        participantes_data = data_dep['personas']
                        self.participantes_data = participantes_data
                except:
                    pass
            
            # Payload correcto según el usuario
            payload = {
                "idTiquetera": tiquetera.id_tiquetera if tiquetera.id_tiquetera else tiquetera.id,
                "idEscenario": tiquetera.id_escenario if tiquetera.id_escenario else tiquetera.id_centro_entrenamiento,
                "participantes": participantes_data,
                "inicioInmediato": False,
                "turnosSeguidos": 1,
                "idCentro": tiquetera.id_centro if tiquetera.id_centro else tiquetera.id_centro_entrenamiento,
                "fecha": fecha  # Agregamos la fecha
            }
            
            print(f"   📡 Consultando horarios con POST: {payload}")
            response = self.session.post(
                f"{Config.API_BASE_URL}{Config.SCHEDULE_ENDPOINT}",
                json=payload,
                params={'autenticador': 'compensar'},
                headers={
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Error API Horarios ({response.status_code}): {response.text}")
                raise Exception(f"Error al obtener horarios: {response.status_code}")
            
            data = response.json()
            print(f"   📥 Respuesta Horarios: {str(data)[:500]}...") # Debug respuesta
            
            horarios = []
            
            # Parsear respuesta compleja
            # Estructura: { "YYYY-MM-DD": { "HH:MM - HH:MM": { "ID": { ... } } } }
            
            horarios_fecha = data.get(fecha, {})
            if not horarios_fecha and isinstance(data, dict):
                # Intentar buscar la fecha en las claves
                for k in data.keys():
                    if k == fecha:
                        horarios_fecha = data[k]
                        break
            
            for rango_horario, detalles in horarios_fecha.items():
                try:
                    # rango_horario es tipo "06:00 - 07:00"
                    partes = rango_horario.split(' - ')
                    if len(partes) != 2:
                        continue
                        
                    hora_inicio = partes[0].strip()
                    hora_fin = partes[1].strip()
                    
                    # Iterar sobre los detalles (pueden haber múltiples zonas/IDs)
                    for id_zona, info in detalles.items():
                        if not isinstance(info, dict):
                            continue
                            
                        cupos = info.get('conteo', 0)
                        total_turnos = info.get('totalTurnos', 0)
                        
                        # ID del turno para reservar
                        # Preferimos 'ids' (numérico) o 'turnos' (string)
                        id_turno = None
                        if info.get('ids') and len(info['ids']) > 0:
                            id_turno = info['ids'][0]
                        elif info.get('turnos') and len(info['turnos']) > 0:
                            id_turno = info['turnos'][0]
                            
                        # Intentar obtener el nombre de la clase
                        nombre_clase = ""
                        caracteristicas = info.get('caracteristicas', {})
                        # El ID de la característica suele coincidir con el id_zona (la clave del dict superior)
                        if id_zona in caracteristicas:
                            nombre_clase = caracteristicas[id_zona].get('nombre', '')
                        else:
                            # Si no coincide, tomamos el primero que encontremos
                            for k, v in caracteristicas.items():
                                if isinstance(v, dict) and 'nombre' in v:
                                    nombre_clase = v['nombre']
                                    break
                            
                        horario = Horario(
                            fecha=fecha,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin,
                            cupos_disponibles=cupos,
                            id_turno=id_turno,
                            nombre_clase=nombre_clase,
                            raw_data=info
                        )
                        
                        # Solo agregar si hay cupos o si queremos mostrar todo
                        horarios.append(horario)
                        
                except Exception as e:
                    print(f"⚠️ Error parseando horario {rango_horario}: {e}")
                    continue
            
            print(f"✅ Se encontraron {len(horarios)} horarios disponibles")
            return horarios
            
        except Exception as e:
            print(f"❌ Error obteniendo horarios: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return []
    
    def realizar_reserva(self, reserva: Reserva) -> bool:
        """
        Realiza una reserva
        
        Args:
            reserva: Objeto Reserva con los datos de la reserva
            
        Returns:
            True si la reserva fue exitosa, False en caso contrario
        """
        try:
            logging.info(f"📅 Reservando: {reserva}...")
            
            # Construir payload complejo requerido por Compensar
            if not reserva.horario.raw_data:
                logging.error("❌ Error: No hay datos crudos del horario para realizar la reserva")
                return False
                
            # Obtener datos del centro/escenario desde el raw_data del horario
            centro_info = reserva.horario.raw_data.get('centroEntrenamiento', {})
            id_centro = centro_info.get('id', reserva.tiquetera.id_centro)
            id_escenario = centro_info.get('idEscenario', reserva.tiquetera.id_escenario)
            
            # Usar participantes cacheados o intentar obtenerlos si no existen
            participantes = self.participantes_data
            if not participantes:
                logging.warning("⚠️ No hay participantes cacheados, intentando obtenerlos...")
                # Aquí podríamos llamar a un método para obtener participantes si fuera necesario
                # Por ahora usaremos una lista vacía o lo que tenga la tiquetera
                pass
            
            # Agregar campos requeridos a cada participante
            for p in participantes:
                p['usos'] = 1
                p['turno'] = 1

            payload = {
                "idTiquetera": reserva.tiquetera.id_tiquetera if reserva.tiquetera.id_tiquetera else reserva.tiquetera.id,
                "arregloTurnos": {"1": 1},
                "horario": reserva.horario.raw_data,
                "idEscenario": id_escenario,
                "idCentro": id_centro,
                "participantes": participantes,
                "turnosSeguidos": 1
            }
            
            # Debug payload
            import json
            payload_str = json.dumps(payload, indent=2)
            logging.info(f"📦 Payload Reserva: {payload_str}")
            
            # Save payload to file for inspection
            try:
                with open('last_reservation_payload.json', 'w', encoding='utf-8') as f:
                    f.write(payload_str)
            except Exception as e:
                logging.error(f"Error saving payload: {e}")
            
            response = self.session.post(
                f"{Config.API_BASE_URL}{Config.BOOKING_ENDPOINT}",
                json=payload,
                params={'autenticador': 'compensar'},
                headers={
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/practica/libre"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') or result.get('estado') == 'exitoso':
                    logging.info(f"✅ Reserva exitosa: {reserva}")
                    return True
                else:
                    error_msg = result.get('mensaje', 'Error desconocido')
                    logging.error(f"❌ Error en reserva: {error_msg}")
                    logging.error(f"   Respuesta completa: {result}")
                    return False
            else:
                logging.error(f"❌ Error HTTP {response.status_code} al realizar reserva")
                logging.error(f"   URL: {response.url}")
                logging.error(f"   Respuesta: {response.text[:200]}...")
                
                # Guardar HTML de error para debug
                try:
                    with open('debug_reservation_error.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                except Exception as e:
                    logging.error(f"Error guardando debug html: {e}")
                    
                return False
                
        except Exception as e:
            logging.error(f"❌ Error crítico en realizar_reserva: {str(e)}")
            if Config.DEBUG:
                import traceback
                logging.error(traceback.format_exc())
            return False
                

    
    def realizar_reservas_multiples(self, reservas: List[Reserva]) -> Dict[str, int]:
        """
        Realiza múltiples reservas
        
        Args:
            reservas: Lista de objetos Reserva
            
        Returns:
            Diccionario con estadísticas de las reservas
        """
        print(f"\n🚀 Iniciando {len(reservas)} reservas...\n")
        
        exitosas = 0
        fallidas = 0
        
        for i, reserva in enumerate(reservas, 1):
            print(f"[{i}/{len(reservas)}] ", end="")
            if self.realizar_reserva(reserva):
                exitosas += 1
            else:
                fallidas += 1
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Exitosas: {exitosas}")
        print(f"   ❌ Fallidas: {fallidas}")
        print(f"   📈 Total: {len(reservas)}")
        
        return {
            'exitosas': exitosas,
            'fallidas': fallidas,
            'total': len(reservas)
        }
