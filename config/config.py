import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Credenciales
    DOCUMENT_TYPE = os.getenv('DOCUMENT_TYPE', 'CC')
    DOCUMENT_NUMBER = os.getenv('DOCUMENT_NUMBER')
    PASSWORD = os.getenv('PASSWORD')
    
    # URLs del sistema Compensar
    BASE_URL = "https://planbienestar.deportescompensar.com"
    LOGIN_URL = "https://seguridad.compensar.com/views/index.html"
    API_BASE_URL = "https://sistemaplanbienestar.deportescompensar.com"
    
    # Endpoints API
    TIQUETERAS_ENDPOINT = "/sistema.php/entrenamiento/reserva/practica/libre"
    SCHEDULE_ENDPOINT = "/entrenamiento/reserva/practica/libre/horarios"
    BOOKING_ENDPOINT = "/sistema.php/entrenamiento/reserva/practica/libre/guardar"
    
    # Configuración
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'  # True por defecto para debugging
    
    @classmethod
    def validate(cls):
        """Valida que las credenciales estén configuradas"""
        if not cls.DOCUMENT_NUMBER or not cls.PASSWORD:
            raise ValueError(
                "Las credenciales no están configuradas. "
                "Por favor, configura DOCUMENT_NUMBER y PASSWORD en el archivo .env"
            )
