from typing import List
from datetime import datetime, timedelta
from src.models.booking import Tiquetera, Horario, Reserva
from src.api.compensar_api import CompensarAPI

class BookingScheduler:
    """Maneja la lógica de selección y agendamiento de reservas"""
    
    def __init__(self, api: CompensarAPI):
        self.api = api
        self.reservas_pendientes: List[Reserva] = []
    
    def mostrar_tiqueteras(self, tiqueteras: List[Tiquetera]):
        """Muestra las tiqueteras disponibles de forma organizada"""
        print("\n" + "="*80)
        print("📋 TIQUETERAS DISPONIBLES")
        print("="*80)
        
        # Agrupar por tipo de deporte
        deportes = {}
        for t in tiqueteras:
            if t.nombre_deporte not in deportes:
                deportes[t.nombre_deporte] = []
            deportes[t.nombre_deporte].append(t)
        
        for deporte, lista in deportes.items():
            print(f"\n🏃 {deporte.upper()}")
            print("-" * 80)
            for i, t in enumerate(lista, 1):
                entradas = "♾️  Ilimitadas" if t.ilimitado else f"🎫 {t.entradas} entradas"
                print(f"  [{i}] {t.nombre_centro_entrenamiento}")
                print(f"      📍 {t.nombre_sede}")
                print(f"      {entradas}")
    
    def seleccionar_tiquetera(self, tiqueteras: List[Tiquetera]) -> Tiquetera:
        """Permite al usuario seleccionar una tiquetera"""
        self.mostrar_tiqueteras(tiqueteras)
        
        while True:
            try:
                print("\n" + "="*80)
                seleccion = input("Selecciona el número de tiquetera (0 para cancelar): ").strip()
                
                if seleccion == '0':
                    return None
                
                idx = int(seleccion) - 1
                if 0 <= idx < len(tiqueteras):
                    return tiqueteras[idx]
                else:
                    print("❌ Número inválido. Intenta de nuevo.")
            except ValueError:
                print("❌ Por favor ingresa un número válido.")
    
    def seleccionar_fechas(self, dias_adelante: int = 7) -> List[str]:
        """Permite seleccionar fechas para buscar horarios"""
        print("\n" + "="*80)
        print("📅 SELECCIÓN DE FECHAS")
        print("="*80)
        
        fechas = []
        hoy = datetime.now()
        
        print("\nFechas disponibles:")
        for i in range(dias_adelante):
            fecha = hoy + timedelta(days=i)
            fecha_str = fecha.strftime("%Y-%m-%d")
            dia_semana = fecha.strftime("%A")
            print(f"  [{i+1}] {fecha_str} ({dia_semana})")
        
        print("\nIngresa los números de las fechas separados por comas (ej: 1,3,5)")
        print("O presiona Enter para seleccionar todas")
        
        seleccion = input("Fechas: ").strip()
        
        if not seleccion:
            # Seleccionar todas
            for i in range(dias_adelante):
                fecha = hoy + timedelta(days=i)
                fechas.append(fecha.strftime("%Y-%m-%d"))
        else:
            # Seleccionar específicas
            try:
                indices = [int(x.strip()) for x in seleccion.split(',')]
                for idx in indices:
                    if 1 <= idx <= dias_adelante:
                        fecha = hoy + timedelta(days=idx-1)
                        fechas.append(fecha.strftime("%Y-%m-%d"))
            except ValueError:
                print("❌ Formato inválido. Usando solo hoy.")
                fechas.append(hoy.strftime("%Y-%m-%d"))
        
        return fechas
    
    def seleccionar_horarios(self, horarios: List[Horario], tiquetera: Tiquetera, fecha: str) -> List[Horario]:
        """Permite seleccionar horarios de una lista"""
        if not horarios:
            print(f"❌ No hay horarios disponibles para {fecha}")
            return []
        
        print(f"\n📅 Horarios disponibles para {tiquetera.nombre_centro_entrenamiento} - {fecha}")
        print("-" * 80)
        
        for i, h in enumerate(horarios, 1):
            print(f"  [{i}] {h.hora_inicio} - {h.hora_fin} ({h.cupos_disponibles} cupos)")
        
        print("\nIngresa los números de los horarios separados por comas (ej: 1,3,5)")
        print("O presiona Enter para omitir esta fecha")
        
        seleccion = input("Horarios: ").strip()
        
        if not seleccion:
            return []
        
        horarios_seleccionados = []
        try:
            indices = [int(x.strip()) for x in seleccion.split(',')]
            for idx in indices:
                if 1 <= idx <= len(horarios):
                    horarios_seleccionados.append(horarios[idx-1])
        except ValueError:
            print("❌ Formato inválido. Omitiendo esta fecha.")
        
        return horarios_seleccionados
    
    def agregar_reserva(self, tiquetera: Tiquetera, horario: Horario):
        """Agrega una reserva a la lista de pendientes"""
        reserva = Reserva(tiquetera=tiquetera, horario=horario)
        self.reservas_pendientes.append(reserva)
        print(f"✅ Agregada: {reserva}")
    
    def mostrar_reservas_pendientes(self):
        """Muestra las reservas pendientes"""
        if not self.reservas_pendientes:
            print("\n📭 No hay reservas pendientes")
            return
        
        print("\n" + "="*80)
        print(f"📋 RESERVAS PENDIENTES ({len(self.reservas_pendientes)})")
        print("="*80)
        
        for i, reserva in enumerate(self.reservas_pendientes, 1):
            print(f"\n[{i}] {reserva.tiquetera.nombre_centro_entrenamiento}")
            print(f"    📍 {reserva.tiquetera.nombre_sede}")
            print(f"    📅 {reserva.horario.fecha}")
            print(f"    🕐 {reserva.horario.hora_inicio} - {reserva.horario.hora_fin}")
    
    def confirmar_y_ejecutar(self) -> bool:
        """Muestra las reservas y pide confirmación antes de ejecutar"""
        self.mostrar_reservas_pendientes()
        
        if not self.reservas_pendientes:
            return False
        
        print("\n" + "="*80)
        confirmacion = input("¿Deseas confirmar estas reservas? (s/n): ").strip().lower()
        
        if confirmacion == 's':
            self.api.realizar_reservas_multiples(self.reservas_pendientes)
            self.reservas_pendientes.clear()
            return True
        else:
            print("❌ Reservas canceladas")
            return False
    
    def limpiar_reservas(self):
        """Limpia la lista de reservas pendientes"""
        self.reservas_pendientes.clear()
        print("🗑️  Reservas pendientes eliminadas")
