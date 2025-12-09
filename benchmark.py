#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark de rendimiento para algoritmos de Graph Coloring.
Prueba con diferentes tamaños de dataset.
"""

import time
import random
from cython_modules.graph_scheduler import PyScheduler


def generar_dataset_aleatorio(num_grupos, num_profesores, materias_por_grupo):
    """Genera un dataset aleatorio para testing"""
    eventos = []
    evento_id = 0
    
    profesores = [f"Profesor {i}" for i in range(num_profesores)]
    grupos = [f"Grupo {i}" for i in range(num_grupos)]
    materias_base = ["Matemáticas", "Programación", "Física", "Química", "Historia",
                     "Inglés", "Estructuras", "Base de Datos", "Redes", "IA"]
    
    for grupo in grupos:
        for _ in range(materias_por_grupo):
            materia = random.choice(materias_base)
            profesor = random.choice(profesores)
            horas = random.randint(3, 6)
            
            eventos.append({
                'id': evento_id,
                'grupo': grupo,
                'materia': f"{materia} {evento_id}",
                'profesor': profesor,
                'horas': horas
            })
            evento_id += 1
    
    return eventos


def ejecutar_benchmark(eventos, estrategia="DSatur"):
    """Ejecuta benchmark con un dataset"""
    scheduler = PyScheduler(peso_continuidad=10, max_iteraciones=1000, estrategia=estrategia)
    
    # Agregar eventos
    for evento in eventos:
        scheduler.agregar_evento(
            evento['id'],
            evento['materia'],
            evento['profesor'],
            evento['grupo'],
            evento['horas']
        )
    
    # Medir tiempo
    inicio = time.time()
    exito = scheduler.ejecutar()
    fin = time.time()
    
    tiempo_python = (fin - inicio) * 1000  # ms
    
    if exito:
        metricas = scheduler.obtener_metricas()
        info_grafo = scheduler.obtener_info_grafo()
        
        return {
            'exito': True,
            'tiempo_python_ms': tiempo_python,
            'tiempo_cpp_ms': metricas['tiempo_ejecucion_ms'],
            'eventos': len(eventos),
            'colores': metricas['colores_usados'],
            'conflictos': metricas['conflictos_totales'],
            'calidad': metricas['calidad_solucion'],
            'nodos': info_grafo['nodos'],
            'aristas': info_grafo['aristas']
        }
    else:
        return {'exito': False}


def main():
    print("=" * 80)
    print("BENCHMARK DE RENDIMIENTO - GRAPH COLORING ALGORITHMS")
    print("=" * 80)
    print()
    
    # Configuraciones de prueba
    tests = [
        {"nombre": "Pequeño", "grupos": 3, "profesores": 5, "materias_por_grupo": 5},
        {"nombre": "Mediano", "grupos": 8, "profesores": 15, "materias_por_grupo": 6},
        {"nombre": "Grande", "grupos": 15, "profesores": 30, "materias_por_grupo": 8},
        {"nombre": "Muy Grande", "grupos": 20, "profesores": 40, "materias_por_grupo": 10},
    ]
    
    resultados = []
    
    for test in tests:
        print(f"\n{'='*80}")
        print(f"📊 Test: {test['nombre']}")
        print(f"   Grupos: {test['grupos']}, Profesores: {test['profesores']}, "
              f"Materias/Grupo: {test['materias_por_grupo']}")
        print('='*80)
        
        # Generar dataset
        eventos = generar_dataset_aleatorio(
            test['grupos'],
            test['profesores'],
            test['materias_por_grupo']
        )
        
        print(f"   Eventos generados: {len(eventos)}")
        
        # Test DSatur
        print("\n   🔵 DSatur:")
        resultado_dsatur = ejecutar_benchmark(eventos, "DSatur")
        if resultado_dsatur['exito']:
            print(f"      ⏱️  Tiempo (Python): {resultado_dsatur['tiempo_python_ms']:.2f} ms")
            print(f"      ⏱️  Tiempo (C++): {resultado_dsatur['tiempo_cpp_ms']:.2f} ms")
            print(f"      🎨 Colores usados: {resultado_dsatur['colores']}")
            print(f"      ⚠️  Conflictos: {resultado_dsatur['conflictos']}")
            print(f"      ✨ Calidad: {resultado_dsatur['calidad']:.2f}%")
        
        # Test Welsh-Powell
        print("\n   🟢 Welsh-Powell:")
        resultado_wp = ejecutar_benchmark(eventos, "Welsh-Powell")
        if resultado_wp['exito']:
            print(f"      ⏱️  Tiempo (Python): {resultado_wp['tiempo_python_ms']:.2f} ms")
            print(f"      ⏱️  Tiempo (C++): {resultado_wp['tiempo_cpp_ms']:.2f} ms")
            print(f"      🎨 Colores usados: {resultado_wp['colores']}")
            print(f"      ⚠️  Conflictos: {resultado_wp['conflictos']}")
            print(f"      ✨ Calidad: {resultado_wp['calidad']:.2f}%")
        
        resultados.append({
            'test': test['nombre'],
            'eventos': len(eventos),
            'dsatur': resultado_dsatur,
            'welsh_powell': resultado_wp
        })
    
    # Tabla resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 80)
    print()
    print(f"{'Test':<15} | {'Eventos':<8} | {'Algoritmo':<12} | {'Tiempo (ms)':<12} | {'Colores':<8} | {'Calidad'}")
    print("-" * 80)
    
    for res in resultados:
        # DSatur
        if res['dsatur']['exito']:
            print(f"{res['test']:<15} | {res['eventos']:<8} | {'DSatur':<12} | "
                  f"{res['dsatur']['tiempo_python_ms']:<12.2f} | {res['dsatur']['colores']:<8} | "
                  f"{res['dsatur']['calidad']:.2f}%")
        
        # Welsh-Powell
        if res['welsh_powell']['exito']:
            print(f"{'':15} | {'':8} | {'Welsh-Powell':<12} | "
                  f"{res['welsh_powell']['tiempo_python_ms']:<12.2f} | {res['welsh_powell']['colores']:<8} | "
                  f"{res['welsh_powell']['calidad']:.2f}%")
        print()
    
    print("=" * 80)
    print("✅ Benchmark completado")
    print("=" * 80)
    
    # Análisis de speedup
    print("\n📈 ANÁLISIS DE RENDIMIENTO:")
    for res in resultados:
        if res['dsatur']['exito']:
            speedup = res['dsatur']['tiempo_python_ms'] / max(res['dsatur']['tiempo_cpp_ms'], 0.001)
            print(f"   {res['test']}: Speedup C++ vs Python overhead = {speedup:.1f}x")


if __name__ == "__main__":
    main()
