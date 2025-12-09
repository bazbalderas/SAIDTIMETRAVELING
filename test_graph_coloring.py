#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar los algoritmos de Graph Coloring.
Prueba DSatur y Welsh-Powell con datos de ejemplo.
"""

from cython_modules.graph_scheduler import PyScheduler
import json

def test_graph_coloring():
    print("=" * 70)
    print("TEST: Graph Coloring Algorithms (DSatur & Welsh-Powell)")
    print("=" * 70)
    
    # Test 1: DSatur
    print("\n📊 Test 1: DSatur Algorithm")
    print("-" * 70)
    
    scheduler = PyScheduler(peso_continuidad=10, max_iteraciones=1000, estrategia="DSatur")
    
    # Agregar eventos de prueba (ITI 5-1)
    scheduler.agregar_evento(0, "Estructura de Datos", "Dr. Said Polanco", "ITI 5-1", 6)
    scheduler.agregar_evento(1, "Diseño BD", "Omar Jasso", "ITI 5-1", 5)
    scheduler.agregar_evento(2, "Probabilidad", "Maribel", "ITI 5-1", 6)
    scheduler.agregar_evento(3, "Ing. Requerimientos", "Alma Amaya", "ITI 5-1", 4)
    
    # Agregar eventos de ITI 8-1 (mismo profesor - conflicto)
    scheduler.agregar_evento(4, "Programación WEB", "Arturo Mascorro", "ITI 8-1", 5)
    scheduler.agregar_evento(5, "Minería Datos", "Jean-Michael", "ITI 8-1", 5)
    scheduler.agregar_evento(6, "Graficación", "Marco Nuño", "ITI 8-1", 6)
    
    # Ejecutar algoritmo
    print("Ejecutando DSatur...")
    success = scheduler.ejecutar()
    
    if success:
        print("✓ Ejecución exitosa")
        
        # Métricas
        metricas = scheduler.obtener_metricas()
        print(f"\n📈 Métricas:")
        print(f"  • Tiempo: {metricas['tiempo_ejecucion_ms']:.2f} ms")
        print(f"  • Iteraciones: {metricas['iteraciones']}")
        print(f"  • Colores usados: {metricas['colores_usados']} timeslots")
        print(f"  • Conflictos totales: {metricas['conflictos_totales']}")
        print(f"  • Penalización huecos: {metricas['penalizacion_huecos']}")
        print(f"  • Calidad: {metricas['calidad_solucion']:.2f}%")
        
        # Asignaciones
        asignaciones = scheduler.obtener_asignaciones()
        print(f"\n📅 Asignaciones (primeras 5):")
        for asig in asignaciones[:5]:
            print(f"  Evento {asig['evento_id']}: {asig['dia']} a las {asig['hora']} (slot {asig['timeslot']})")
        
        # Conflictos
        conflictos = scheduler.obtener_conflictos()
        print(f"\n⚠️  Conflictos detectados: {len(conflictos)}")
        for conf in conflictos[:3]:
            print(f"  • Eventos {conf['evento1_id']} y {conf['evento2_id']}: {conf['razon']}")
        
        # Información del grafo
        info_grafo = scheduler.obtener_info_grafo()
        print(f"\n🔗 Grafo de Conflictos:")
        print(f"  • Nodos: {info_grafo['nodos']}")
        print(f"  • Aristas: {info_grafo['aristas']}")
        print(f"  • Grado máximo: {info_grafo['grado_maximo']}")
        print(f"  • Grado promedio: {info_grafo['grado_promedio']:.2f}")
        
        # Matriz de adyacencia (muestra parcial)
        matriz = scheduler.obtener_matriz_adyacencia()
        print(f"\n📊 Matriz de Adyacencia (parcial):")
        for i in range(min(5, len(matriz))):
            fila = ' '.join(str(matriz[i][j]) for j in range(min(5, len(matriz[i]))))
            print(f"  {fila}")
    else:
        print("✗ Error en ejecución")
    
    # Test 2: Welsh-Powell
    print("\n" + "=" * 70)
    print("📊 Test 2: Welsh-Powell Algorithm")
    print("-" * 70)
    
    scheduler2 = PyScheduler(peso_continuidad=10, max_iteraciones=1000, estrategia="Welsh-Powell")
    
    # Agregar los mismos eventos
    scheduler2.agregar_evento(0, "Estructura de Datos", "Dr. Said Polanco", "ITI 5-1", 6)
    scheduler2.agregar_evento(1, "Diseño BD", "Omar Jasso", "ITI 5-1", 5)
    scheduler2.agregar_evento(2, "Probabilidad", "Maribel", "ITI 5-1", 6)
    scheduler2.agregar_evento(3, "Ing. Requerimientos", "Alma Amaya", "ITI 5-1", 4)
    scheduler2.agregar_evento(4, "Programación WEB", "Arturo Mascorro", "ITI 8-1", 5)
    scheduler2.agregar_evento(5, "Minería Datos", "Jean-Michael", "ITI 8-1", 5)
    scheduler2.agregar_evento(6, "Graficación", "Marco Nuño", "ITI 8-1", 6)
    
    print("Ejecutando Welsh-Powell...")
    success2 = scheduler2.ejecutar()
    
    if success2:
        print("✓ Ejecución exitosa")
        metricas2 = scheduler2.obtener_metricas()
        print(f"\n📈 Métricas:")
        print(f"  • Tiempo: {metricas2['tiempo_ejecucion_ms']:.2f} ms")
        print(f"  • Iteraciones: {metricas2['iteraciones']}")
        print(f"  • Colores usados: {metricas2['colores_usados']} timeslots")
        print(f"  • Calidad: {metricas2['calidad_solucion']:.2f}%")
    
    # Comparación
    print("\n" + "=" * 70)
    print("📊 Comparación DSatur vs Welsh-Powell")
    print("-" * 70)
    print(f"Algoritmo       | Tiempo (ms) | Colores | Calidad")
    print(f"DSatur          | {metricas['tiempo_ejecucion_ms']:>11.2f} | {metricas['colores_usados']:>7} | {metricas['calidad_solucion']:>6.2f}%")
    print(f"Welsh-Powell    | {metricas2['tiempo_ejecucion_ms']:>11.2f} | {metricas2['colores_usados']:>7} | {metricas2['calidad_solucion']:>6.2f}%")
    
    print("\n✅ Todos los tests completados exitosamente!")
    print("=" * 70)

if __name__ == "__main__":
    test_graph_coloring()
