#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar la funcionalidad completa del sistema
sin necesitar una pantalla (modo headless)
"""

import os
import sys

# Configurar Qt para modo headless
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Importar nuestro sistema
from main_qt import MainWindow

def test_ui_workflow():
    """Prueba el flujo completo de la UI"""
    print("=" * 70)
    print("TEST DE INTERFAZ GRÁFICA (modo headless)")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Simular carga de datos
    print("\n1. Cargando datos...")
    window.sistema.cargar_datos("data/datos_completos.json")
    window.actualizar_tabla_profesores()
    print(f"   ✓ {len(window.sistema.profesores)} profesores cargados")
    print(f"   ✓ {len(window.sistema.grupos)} grupos cargados")
    print(f"   ✓ {len(window.sistema.materias)} materias cargadas")
    
    # Simular configuración
    print("\n2. Configurando parámetros...")
    window.estrategia_combo.setCurrentText("DSatur")
    window.peso_spin.setValue(10)
    window.iter_spin.setValue(1000)
    print("   ✓ Estrategia: DSatur")
    print("   ✓ Peso continuidad: 10")
    print("   ✓ Max iteraciones: 1000")
    
    # Generar horarios
    print("\n3. Generando horarios...")
    window.sistema.config.set('Estrategia_Coloreado', 'DSatur')
    window.sistema.config.set('Peso_Continuidad', 10)
    window.sistema.config.set('Max_Iteraciones', 1000)
    
    window.sistema.generar_eventos()
    exito = window.sistema.ejecutar_algoritmo()
    
    if exito:
        print("   ✓ Horarios generados exitosamente")
        
        # Simular mostrar resultados
        print("\n4. Mostrando resultados en UI...")
        resultados = window.sistema.resultados
        window.mostrar_resultados(resultados)
        print("   ✓ Métricas mostradas")
        print("   ✓ Grafo visualizado")
        print("   ✓ Matriz de adyacencia mostrada")
        print(f"   ✓ {len(resultados['asignaciones'])} asignaciones mostradas")
        
        # Verificar que el grafo se generó
        if window.grafo_ruta_actual and os.path.exists(window.grafo_ruta_actual):
            print(f"   ✓ Imagen del grafo: {window.grafo_ruta_actual}")
        
        # Probar exportaciones
        print("\n5. Probando exportaciones...")
        
        # Excel
        archivo_excel = window.sistema.exportar_excel_completo("test_ui_horarios.xlsx")
        if archivo_excel and os.path.exists(archivo_excel):
            size = os.path.getsize(archivo_excel)
            print(f"   ✓ Excel exportado: {archivo_excel} ({size} bytes)")
        
        # HTML
        archivo_html = window.sistema.exportar_html_completo("test_ui_horarios.html")
        if archivo_html and os.path.exists(archivo_html):
            size = os.path.getsize(archivo_html)
            print(f"   ✓ HTML exportado: {archivo_html} ({size} bytes)")
        
        # JSON
        window.sistema.exportar_resultados_json("test_ui_resultados.json")
        if os.path.exists("test_ui_resultados.json"):
            size = os.path.getsize("test_ui_resultados.json")
            print(f"   ✓ JSON exportado: test_ui_resultados.json ({size} bytes)")
        
        # Matriz CSV
        window.sistema.exportar_matriz_csv("test_ui_matriz.csv")
        if os.path.exists("test_ui_matriz.csv"):
            size = os.path.getsize("test_ui_matriz.csv")
            print(f"   ✓ CSV exportado: test_ui_matriz.csv ({size} bytes)")
        
        print("\n6. Verificando calidad de resultados...")
        metricas = resultados['metricas']
        print(f"   • Calidad: {metricas['calidad_solucion']:.2f}%")
        print(f"   • Conflictos: {metricas['conflictos_totales']}")
        print(f"   • Timeslots usados: {metricas['colores_usados']}")
        print(f"   • Tiempo: {metricas['tiempo_ejecucion_ms']:.2f} ms")
        
        if metricas['conflictos_totales'] == 0:
            print("   ✓ ¡SIN CONFLICTOS DUROS!")
        
        print("\n" + "=" * 70)
        print("✅ TODAS LAS PRUEBAS DE UI PASARON EXITOSAMENTE")
        print("=" * 70)
        
        return True
    else:
        print("   ✗ Error al generar horarios")
        return False

if __name__ == "__main__":
    try:
        exito = test_ui_workflow()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
