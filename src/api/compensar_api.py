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
            
            # 2. Intentar obtener tiqueteras usando el ID si está disponible
            endpoints_to_try = []
            
            # Endpoint base descubierto en JS
            endpoints_to_try.append({
                'url': f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/tiqueteras",
                'method': 'POST',
                'data': {'id_participacion': id_participacion} if id_participacion else {}
            })
            
            # Variación con ID en URL (común en REST)
            if id_participacion:
                endpoints_to_try.append({
                    'url': f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/tiqueteras/{id_participacion}",
                    'method': 'GET',
                    'data': {}
                })
                # Variación query param
                endpoints_to_try.append({
                    'url': f"{Config.API_BASE_URL}/sistema.php/entrenamiento/reserva/tiqueteras",
                    'method': 'GET',
                    'data': {'id_participacion': id_participacion}
                })

            response = None
            success = False
            
            for endpoint in endpoints_to_try:
                try:
                    print(f"   🔄 Probando: {endpoint['url']} ({endpoint['method']})")
                    if endpoint['method'] == 'POST':
                        response = self.session.post(
                            endpoint['url'],
                            data=endpoint['data'],
                            params={'autenticador': 'compensar'},
                            allow_redirects=True
                        )
                    else:
                        response = self.session.get(
                            endpoint['url'],
                            params={'autenticador': 'compensar', **endpoint['data']},
                            allow_redirects=True
                        )
                    
                    if response.status_code == 200:
                        # Verificar si es JSON válido
                        try:
                            data = response.json()
                            success = True
                            print("   ✅ ¡Endpoint correcto encontrado!")
                            break
                        except:
                            print("   ⚠️ Respuesta no es JSON")
                    else:
                        print(f"   ⚠️ Falló con {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error probando endpoint: {str(e)}")

            if not success or not response:
                # Si todo falla, guardar último error
                if response:
                    with open('debug_api_error.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                raise Exception("No se pudieron obtener las tiqueteras en ningún endpoint conocido")
            
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
                    ilimitado=t.get('ilimitado', False)
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
            
            params = {
                'id_centro_entrenamiento': tiquetera.id_centro_entrenamiento,
                'id_participacion_deportista': tiquetera.id_participacion_deportista,
                'fecha': fecha
            }
            
            response = self.session.get(
                f"{Config.API_BASE_URL}{Config.SCHEDULE_ENDPOINT}",
                params=params
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
