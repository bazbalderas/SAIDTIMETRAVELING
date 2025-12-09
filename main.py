import json
import os
from datetime import datetime

def cargar_horarios_desde_json():
    """
    Carga los horarios desde datos_iti_usuario.json y los genera correctamente
    """
    archivo_json = '/home/baz/proyecto final estructura de datos 2/datos_iti_usuario.json'
    
    try:
        with open(archivo_json, 'r', encoding='utf-8') as file:
            datos = json.load(file)
        
        horarios_generados = []
        
        # Verificar si existe la estructura de materias
        if 'materias' in datos:
            for materia_info in datos['materias']:
                nombre_materia = materia_info.get('nombre', '')
                dias = materia_info.get('dias', [])
                hora_inicio = materia_info.get('hora_inicio', '')
                hora_fin = materia_info.get('hora_fin', '')
                salon = materia_info.get('salon', '')
                profesor = materia_info.get('profesor', '')
                
                # Generar horario para cada día
                for dia in dias:
                    horario = {
                        'materia': nombre_materia,
                        'dia': dia,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'salon': salon,
                        'profesor': profesor
                    }
                    horarios_generados.append(horario)
        
        # Ordenar por día y hora
        orden_dias = {'Lunes': 1, 'Martes': 2, 'Miércoles': 3, 'Jueves': 4, 'Viernes': 5, 'Sábado': 6, 'Domingo': 7}
        horarios_generados.sort(key=lambda x: (orden_dias.get(x['dia'], 8), x['hora_inicio']))
        
        return horarios_generados
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_json}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: El archivo JSON está mal formado: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado al cargar horarios: {e}")
        return []

def generar_horario_al_iniciar():
    """
    Genera los horarios automáticamente al abrir el programa
    """
    print("Cargando horarios desde datos_iti_usuario.json...")
    horarios = cargar_horarios_desde_json()
    
    if horarios:
        print(f"\n✓ Se cargaron {len(horarios)} clases correctamente\n")
        mostrar_horario_semanal(horarios)
        return horarios
    else:
        print("✗ No se pudieron cargar los horarios")
        return []

def mostrar_horario_semanal(horarios):
    """
    Muestra el horario organizado por día de la semana
    """
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    
    for dia in dias_semana:
        clases_del_dia = [h for h in horarios if h['dia'] == dia]
        
        if clases_del_dia:
            print(f"\n{'='*70}")
            print(f"  {dia.upper()}")
            print(f"{'='*70}")
            
            for clase in clases_del_dia:
                print(f"  ⏰ {clase['hora_inicio']} - {clase['hora_fin']}")
                print(f"  📚 Materia: {clase['materia']}")
                print(f"  👨‍🏫 Profesor: {clase['profesor']}")
                print(f"  🚪 Salón: {clase['salon']}")
                print(f"  {'-'*68}")

if __name__ == "__main__":
    # Generar horarios automáticamente al iniciar
    horarios = generar_horario_al_iniciar()