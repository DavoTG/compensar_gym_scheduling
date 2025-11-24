import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config.config import Config
from src.models.booking import Tiquetera, Horario, Reserva

class CompensarAPI:
    """Maneja las interacciones con la API de Compensar"""
    
    def __init__(self, session: requests.Session):
        self.session = session
    
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
                except:
                    pass
            
            # Payload correcto según el usuario
            payload = {
                "idTiquetera": tiquetera.id_tiquetera if tiquetera.id_tiquetera else tiquetera.id,
                "idEscenario": tiquetera.id_escenario if tiquetera.id_escenario else tiquetera.id_centro_entrenamiento,
                "participantes": participantes_data,
                "inicioInmediato": False,
                "turnosSeguidos": 1,
                "idCentro": tiquetera.id_centro if tiquetera.id_centro else tiquetera.id_centro_entrenamiento
            }
            
            print(f"   📡 Consultando horarios con POST")
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
                raise Exception(f"Error al obtener horarios: {response.status_code}")
            
            data = response.json()
            horarios = []
            
            # El formato exacto depende de la respuesta de la API
            # Ajustar según la estructura real
            for h in data.get('horarios', []):
                horario = Horario(
                    fecha=fecha,
                    hora_inicio=h.get('hora_inicio'),
                    hora_fin=h.get('hora_fin'),
                    cupos_disponibles=h.get('cupos_disponibles', 0),
                    id_turno=h.get('id_turno')
                )
                if horario.cupos_disponibles > 0:
                    horarios.append(horario)
            
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
            print(f"📅 Reservando: {reserva}...")
            
            payload = reserva.to_api_payload()
            
            response = self.session.post(
                f"{Config.API_BASE_URL}{Config.BOOKING_ENDPOINT}",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') or result.get('estado') == 'exitoso':
                    print(f"✅ Reserva exitosa: {reserva}")
                    return True
                else:
                    error_msg = result.get('mensaje', 'Error desconocido')
                    print(f"❌ Error en reserva: {error_msg}")
                    return False
            else:
                print(f"❌ Error HTTP {response.status_code} al realizar reserva")
                return False
                
        except Exception as e:
            print(f"❌ Error realizando reserva: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
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
