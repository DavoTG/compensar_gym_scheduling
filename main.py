#!/usr/bin/env python3
"""
Compensar Gym Scheduler
Sistema automatizado para agendar múltiples clases/gimnasio/piscina en Compensar
"""

import sys
from config.config import Config
from src.auth.compensar_auth import CompensarAuth
from src.api.compensar_api import CompensarAPI
from src.scheduler.booking_scheduler import BookingScheduler

def print_banner():
    """Muestra el banner de la aplicación"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🏋️  COMPENSAR GYM SCHEDULER 🏊                            ║
║                                                                              ║
║              Sistema de Agendamiento Múltiple de Clases                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Función principal de la aplicación"""
    print_banner()
    
    try:
        # Validar configuración
        Config.validate()
        
        # Paso 1: Autenticación
        auth = CompensarAuth()
        if not auth.login(Config.DOCUMENT_TYPE, Config.DOCUMENT_NUMBER, Config.PASSWORD):
            print("\n❌ No se pudo iniciar sesión. Verifica tus credenciales en el archivo .env")
            sys.exit(1)
        
        # Obtener ID de usuario
        user_id = auth.get_user_id()
        print(f"👤 Usuario ID: {user_id}")
        
        # Paso 2: Inicializar API y Scheduler
        api = CompensarAPI(auth.get_session())
        scheduler = BookingScheduler(api)
        
        # Paso 3: Obtener tiqueteras disponibles
        tiqueteras = api.get_tiqueteras()
        
        if not tiqueteras:
            print("\n❌ No se encontraron tiqueteras disponibles")
            sys.exit(1)
        
        # Paso 4: Menú principal
        while True:
            print("\n" + "="*80)
            print("MENÚ PRINCIPAL")
            print("="*80)
            print("1. 📅 Agregar reservas")
            print("2. 👀 Ver reservas pendientes")
            print("3. ✅ Confirmar y ejecutar reservas")
            print("4. 🗑️  Limpiar reservas pendientes")
            print("5. 🚪 Salir")
            print("="*80)
            
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == '1':
                # Agregar reservas
                tiquetera = scheduler.seleccionar_tiquetera(tiqueteras)
                
                if tiquetera is None:
                    continue
                
                print(f"\n✅ Seleccionada: {tiquetera}")
                
                # Seleccionar fechas
                fechas = scheduler.seleccionar_fechas(dias_adelante=7)
                
                # Para cada fecha, obtener horarios y seleccionar
                for fecha in fechas:
                    horarios = api.get_horarios(tiquetera, fecha)
                    horarios_seleccionados = scheduler.seleccionar_horarios(horarios, tiquetera, fecha)
                    
                    for horario in horarios_seleccionados:
                        scheduler.agregar_reserva(tiquetera, horario)
                
                print(f"\n✅ Total de reservas pendientes: {len(scheduler.reservas_pendientes)}")
            
            elif opcion == '2':
                # Ver reservas pendientes
                scheduler.mostrar_reservas_pendientes()
            
            elif opcion == '3':
                # Confirmar y ejecutar
                if scheduler.confirmar_y_ejecutar():
                    print("\n✅ Proceso completado")
                    
                    continuar = input("\n¿Deseas hacer más reservas? (s/n): ").strip().lower()
                    if continuar != 's':
                        break
            
            elif opcion == '4':
                # Limpiar reservas
                scheduler.limpiar_reservas()
            
            elif opcion == '5':
                # Salir
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida")
        
    except ValueError as e:
        print(f"\n❌ Error de configuración: {str(e)}")
        print("\nAsegúrate de:")
        print("1. Copiar .env.example a .env")
        print("2. Configurar tus credenciales en .env")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        if Config.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
