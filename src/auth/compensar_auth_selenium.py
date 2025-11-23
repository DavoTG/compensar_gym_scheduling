import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.config import Config
import time

class CompensarAuthSelenium:
    """Maneja la autenticación con Compensar usando Selenium (navegador real)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.user_id = None
        self.driver = None
    
    def login_interactive(self) -> bool:
        """
        Abre un navegador para que el usuario inicie sesión manualmente.
        Monitorea las cookies hasta detectar una sesión válida.
        """
        try:
            print("🔐 Iniciando login interactivo...")
            
            # Configurar Chrome (CON interfaz gráfica esta vez)
            chrome_options = Options()
            # chrome_options.add_argument('--headless')  # Comentado para que sea visible
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--start-maximized')
            
            print("   Iniciando navegador...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navegar a la página de login
            login_url = f"{Config.LOGIN_URL}?serviceProviderName=HER-SP&protocol=SAML"
            print(f"   Navegando a {login_url}...")
            self.driver.get(login_url)
            
            print("   ⏳ Esperando a que el usuario inicie sesión...")
            
            # Loop de espera (máximo 5 minutos)
            start_time = time.time()
            max_wait = 300  # 5 minutos
            
            # Sincronizar User-Agent
            user_agent = self.driver.execute_script("return navigator.userAgent;")
            self.session.headers.update({'User-Agent': user_agent})
            print(f"   ℹ️ User-Agent sincronizado: {user_agent[:50]}...")
            
            last_print_time = 0
            
            while (time.time() - start_time) < max_wait:
                # Verificar si el navegador sigue abierto
                try:
                    current_url = self.driver.current_url
                    # print(f"   📍 URL actual: {current_url[:60]}...")
                except:
                    print("   ⚠️ El navegador fue cerrado por el usuario")
                    return False
                
                # Copiar cookies actuales a la sesión
                cookies = self.driver.get_cookies()
                
                # Imprimir estado cada 5 segundos para no saturar
                if time.time() - last_print_time > 5:
                    print(f"   📍 URL: {current_url[:80]}")
                    domains = set(c.get('domain', '') for c in cookies)
                    print(f"   🍪 Cookies: {len(cookies)} | Dominios: {domains}")
                    last_print_time = time.time()
                
                for cookie in cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                # Sincronizar headers
                self.session.headers.update({
                    'Referer': 'https://sistemaplanbienestar.deportescompensar.com/',
                    'Origin': 'https://sistemaplanbienestar.deportescompensar.com',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
                })

                # Intentar verificar autenticación con múltiples endpoints
                endpoints_to_try = [
                    # URL del screenshot (más probable)
                    "https://sistemaplanbienestar.deportescompensar.com/sistema.php/entrenamiento/reserva/practica/libre",
                    # URL provista por usuario
                    f"{Config.API_BASE_URL}{Config.TIQUETERAS_ENDPOINT}",
                    # Base URL
                    "https://sistemaplanbienestar.deportescompensar.com/sistema.php",
                    "https://sistemaplanbienestar.deportescompensar.com/"
                ]

                for check_url in endpoints_to_try:
                    try:
                        response = self.session.get(
                            check_url,
                            params={'autenticador': 'compensar'},
                            timeout=5,
                            allow_redirects=True
                        )
                        
                        # Si devuelve 200 OK y NO es la página de login (verificar contenido)
                        if response.status_code == 200:
                            # Verificar que no nos redirigió al login de seguridad
                            if "seguridad.compensar.com" not in response.url:
                                self.authenticated = True
                                print(f"   ✅ ¡Login detectado exitosamente en {check_url}!")
                                print(f"   📍 Final URL: {response.url}")
                                
                                self.user_id = "usuario_compensar"
                                
                                # Antes de cerrar, intentar obtener datos de tiqueteras
                                print("   📦 Obteniendo datos de tiqueteras desde el navegador...")
                                self._fetch_tiqueteras_data()
                                
                                # Cerrar navegador
                                self.driver.quit()
                                self.driver = None
                                return True
                        
                        elif time.time() - last_print_time < 2:
                             print(f"   ⚠️ Falló {check_url}: {response.status_code}")

                    except Exception:
                        pass
                
                # Esperar antes del siguiente intento
                time.sleep(2)
            
            print("   ❌ Tiempo de espera agotado")
            if self.driver:
                self.driver.quit()
            return False
            
        except Exception as e:
            print(f"❌ Error en login interactivo: {str(e)}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            return False
    
    def get_user_id(self) -> str:
        """Obtiene el ID de usuario"""
        if not self.authenticated:
            raise Exception("No estás autenticado. Ejecuta login() primero.")
        
        if self.user_id:
            return str(self.user_id)
            
        # Fallback: intentar obtenerlo de la API si no está seteado
        try:
            response = self.session.get(
                f"{Config.API_BASE_URL}{Config.TIQUETERAS_ENDPOINT}",
                params={'autenticador': 'compensar'}
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('tiqueteras') and len(data['tiqueteras']) > 0:
                        self.user_id = data['tiqueteras'][0]['id_participacion_deportista']
                        return str(self.user_id)
                except:
                    pass
            
            # Si fallamos en obtener el ID real, retornamos un default para permitir el acceso
            # ya que la autenticación fue exitosa
            print("⚠️ No se pudo obtener ID real, usando default")
            self.user_id = "usuario_compensar"
            return self.user_id
            
        except Exception as e:
            print(f"❌ Error obteniendo ID de usuario: {str(e)}")
            # Si ya estamos autenticados, permitir acceso
            self.user_id = "usuario_compensar"
            return self.user_id
    
    def is_authenticated(self) -> bool:
        """Verifica si la sesión está autenticada"""
        return self.authenticated
    
    def get_session(self) -> requests.Session:
        """Retorna la sesión autenticada"""
        if not self.authenticated:
            raise Exception("No estás autenticado. Ejecuta login() primero.")
        return self.session
    
    def __del__(self):
        """Asegurar que el navegador se cierre"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
