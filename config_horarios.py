#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constantes compartidas del sistema de horarios
Define valores que deben ser consistentes entre módulos
"""

# Configuración de horarios
DIAS_SEMANA = ["L", "M", "Mi", "J", "V"]
NUM_DIAS = 5

# Horarios de clases (7:00 AM a 19:50, 15 slots de 55 minutos)
HORAS_INICIO = [
    "07:00", "07:55", "08:50", "09:45", "10:40", "11:35", "12:30",
    "13:25", "14:20", "15:15", "16:10", "17:05", "18:00", "18:55", "19:50"
]

SLOTS_POR_DIA = 15  # Debe coincidir con scheduler.cpp
TOTAL_TIMESLOTS = NUM_DIAS * SLOTS_POR_DIA  # 5 días × 15 horas = 75 timeslots

DURACION_BLOQUE_MINUTOS = 55

# Configuración del algoritmo
ESTRATEGIAS_DISPONIBLES = ["DSatur", "Welsh-Powell"]
PESO_CONTINUIDAD_DEFAULT = 10
MAX_ITERACIONES_DEFAULT = 1000

# Colores para visualización
COLORES_MATERIAS_PASTEL = [
    "B4E7CE", "FFE5B4", "E5B4FF", "B4D7FF", "FFB4B4",
    "D4FFB4", "FFD4B4", "B4FFE7", "E7B4FF", "B4FFD4",
    "FFB4E7", "D4B4FF", "B4E7FF", "FFEBB4", "C4B4FF"
]

# Validación
def validar_configuracion():
    """Valida que la configuración sea consistente"""
    assert len(HORAS_INICIO) == SLOTS_POR_DIA, \
        f"Inconsistencia: HORAS_INICIO tiene {len(HORAS_INICIO)} elementos, pero SLOTS_POR_DIA={SLOTS_POR_DIA}"
    assert TOTAL_TIMESLOTS == 75, \
        f"Error: TOTAL_TIMESLOTS debe ser 75, pero es {TOTAL_TIMESLOTS}"
    print("✓ Configuración validada correctamente")

if __name__ == "__main__":
    validar_configuracion()
    print(f"Días: {NUM_DIAS}")
    print(f"Slots por día: {SLOTS_POR_DIA}")
    print(f"Total timeslots: {TOTAL_TIMESLOTS}")
    print(f"Horas: {HORAS_INICIO[0]} - {HORAS_INICIO[-1]}")
