import requests
from bs4 import BeautifulSoup
from config.config import Config

class CompensarAuth:
    """Maneja la autenticación con el sistema de Compensar"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.authenticated = False
        self.user_id = None
    
    def login(self, document_type: str, document_number: str, password: str) -> bool:
        """
        Realiza el login en el sistema de Compensar
        
        Args:
            document_type: Tipo de documento (CC, TI, etc.)
            document_number: Número de documento
            password: Contraseña
            
        Returns:
            True si el login fue exitoso, False en caso contrario
        """
        try:
            print("🔐 Iniciando sesión en Compensar...")
            print(f"   Tipo: {document_type}, Documento: {document_number}")
            
            # Actualizar headers para simular un navegador real
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'es-ES,es;q=0.9',
                'Content-Type': 'application/json',
                'Origin': 'https://www.plataformabienestar.com',
                'Referer': 'https://www.plataformabienestar.com/'
            })
            
            # Intentar con plataformabienestar.com (endpoint encontrado)
            print("   Paso 1: Intentando login con plataformabienestar.com...")
            
            login_payload = {
                "username": document_number,
                "password": password,
                "documentType": document_type
            }
            
            login_response = self.session.post(
                "https://www.plataformabienestar.com/auth/login",
                json=login_payload
            )
            
            print(f"   Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print("   ✅ Login exitoso en plataformabienestar.com")
                
                # Verificar con tiqueteras
                print("   Paso 2: Verificando acceso a tiqueteras...")
                test_response = self.session.get(
                    f"{Config.API_BASE_URL}{Config.TIQUETERAS_ENDPOINT}",
                    params={'autenticador': 'compensar'}
                )
                
                print(f"   Status tiqueteras: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    try:
                        data = test_response.json()
                        if data.get('tiqueteras'):
                            self.authenticated = True
                            print("✅ Login exitoso - Tiqueteras encontradas")
                            return True
                    except:
                        pass
            
            # Si falla, intentar con el método original pero con el formulario correcto
            print("   Paso 3: Intentando método alternativo...")
            
            # Primero obtener la página para cookies y CSRF
            initial_response = self.session.get(Config.LOGIN_URL)
            
            # Intentar POST al mismo URL (action vacío significa mismo URL)
            form_data = {
                'username': document_number,
                'password': password,
                'typeLogin': 'alias',
                'serviceProviderName': 'HER-SP'
            }
            
            login_response2 = self.session.post(
                Config.LOGIN_URL,
                data=form_data,
                allow_redirects=True
            )
            
            print(f"   Status método alternativo: {login_response2.status_code}")
            
            # Verificar con tiqueteras
            test_response2 = self.session.get(
                f"{Config.API_BASE_URL}{Config.TIQUETERAS_ENDPOINT}",
                params={'autenticador': 'compensar'}
            )
            
            if test_response2.status_code == 200:
                try:
                    data = test_response2.json()
                    if data.get('tiqueteras'):
                        self.authenticated = True
                        print("✅ Login exitoso - Método alternativo")
                        return True
                except:
                    pass
            
            print("❌ Login fallido - Verifica tus credenciales")
            if Config.DEBUG:
                print(f"   Respuesta plataformabienestar: {login_response.text[:500]}")
                print(f"   Respuesta alternativa: {login_response2.text[:500]}")
            
            return False
            
        except Exception as e:
            print(f"❌ Error durante el login: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return False
    
    def get_user_id(self) -> str:
        """
        Obtiene el ID de usuario desde las tiqueteras
        
        Returns:
            ID del usuario participante deportista
        """
        if not self.authenticated:
            raise Exception("No estás autenticado. Ejecuta login() primero.")
        
        try:
            # Hacer request al endpoint de tiqueteras
            response = self.session.get(
                f"{Config.API_BASE_URL}{Config.TIQUETERAS_ENDPOINT}",
                params={'autenticador': 'compensar'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('tiqueteras') and len(data['tiqueteras']) > 0:
                    self.user_id = data['tiqueteras'][0]['id_participacion_deportista']
                    return str(self.user_id)
            
            raise Exception("No se pudo obtener el ID de usuario")
            
        except Exception as e:
            print(f"❌ Error obteniendo ID de usuario: {str(e)}")
            raise
    
    def is_authenticated(self) -> bool:
        """Verifica si la sesión está autenticada"""
        return self.authenticated
    
    def get_session(self) -> requests.Session:
        """Retorna la sesión autenticada"""
        if not self.authenticated:
            raise Exception("No estás autenticado. Ejecuta login() primero.")
        return self.session
