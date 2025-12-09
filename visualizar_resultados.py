#!/usr/bin/env python3
import json
import sys
import os

def main():
    file_path = 'resultados.json'
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")
        return

    print("\n" + "="*60)
    print("VISUALIZADOR DE RESULTADOS DE HORARIOS")
    print("="*60)

    # Mostrar Configuración
    config = data.get('configuracion', {})
    print("\n[CONFIGURACIÓN]")
    for k, v in config.items():
        print(f"  {k}: {v}")

    # Mostrar Métricas
    metricas = data.get('metricas', {})
    print("\n[MÉTRICAS]")
    for k, v in metricas.items():
        print(f"  {k}: {v}")

    # Mostrar Conflictos
    conflictos = data.get('conflictos', [])
    print(f"\n[CONFLICTOS] Total: {len(conflictos)}")
    if conflictos:
        print("  Mostrando primeros 5 conflictos:")
        for i, c in enumerate(conflictos[:5]):
            print(f"  {i+1}. {c.get('razon', 'Sin razón')} (Eventos: {c.get('evento1_id')}, {c.get('evento2_id')})")
        if len(conflictos) > 5:
            print(f"  ... y {len(conflictos)-5} más.")

    # Mostrar Asignaciones
    asignaciones = data.get('asignaciones', [])
    print(f"\n[ASIGNACIONES] Total: {len(asignaciones)}")
    
    # Agrupar por grupo para mostrar mejor
    por_grupo = {}
    for a in asignaciones:
        g = a.get('grupo', 'Sin Grupo')
        if g not in por_grupo:
            por_grupo[g] = []
        por_grupo[g].append(a)

    for grupo, items in por_grupo.items():
        print(f"\n  >> GRUPO: {grupo}")
        print(f"  {'MATERIA':<25} | {'PROFESOR':<30} | {'DIA':<3} | {'HORA'}")
        print("  " + "-"*75)
        for item in sorted(items, key=lambda x: (x.get('dia'), x.get('hora'))):
            materia = item.get('materia', '')[:25]
            profesor = item.get('profesor', '')[:30]
            dia = item.get('dia', '')
            hora = item.get('hora', '')
            print(f"  {materia:<25} | {profesor:<30} | {dia:<3} | {hora}")

    print("\n" + "="*60)
    print("FIN DEL REPORTE")
    print("="*60)

if __name__ == "__main__":
    main()
