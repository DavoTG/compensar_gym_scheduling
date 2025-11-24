from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Tiquetera:
    """Representa una tiquetera (membresía) disponible"""
    id: int
    nombre_centro_entrenamiento: str
    nombre_sede: str
    nombre_deporte: str
    id_centro_entrenamiento: int
    id_participacion_deportista: int
    entradas: int
    ilimitado: bool
    id_tiquetera: int = 0  # ID real de la tiquetera en el sistema
    id_escenario: int = 0  # ID del escenario/sede
    id_centro: int = 0  # ID del centro
    
    def __str__(self):
        entradas_str = "Ilimitadas" if self.ilimitado else str(self.entradas)
        return f"{self.nombre_centro_entrenamiento} - {self.nombre_sede} ({self.nombre_deporte}) - Entradas: {entradas_str}"


@dataclass
class Horario:
    """Representa un horario disponible para reserva"""
    fecha: str
    hora_inicio: str
    hora_fin: str
    cupos_disponibles: int
    id_turno: Optional[int] = None
    nombre_clase: str = ""
    raw_data: dict = None
    
    def __str__(self):
        return f"{self.fecha} {self.hora_inicio}-{self.hora_fin} - {self.nombre_clase} ({self.cupos_disponibles} cupos)"


@dataclass
class Reserva:
    """Representa una reserva a realizar"""
    tiquetera: Tiquetera
    horario: Horario
    
    def __str__(self):
        return f"{self.tiquetera.nombre_centro_entrenamiento} - {self.horario}"
    
    def to_api_payload(self):
        """Convierte la reserva al formato esperado por la API"""
        return {
            "id_centro_entrenamiento": self.tiquetera.id_centro_entrenamiento,
            "id_participacion_deportista": self.tiquetera.id_participacion_deportista,
            "fecha": self.horario.fecha,
            "hora_inicio": self.horario.hora_inicio,
            "hora_fin": self.horario.hora_fin,
            "id_turno": self.horario.id_turno
        }
