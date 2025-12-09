#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Generación de Horarios - Graph Coloring
Usa algoritmos DSatur y Welsh-Powell implementados en C++/Cython
"""

import json
import os
from typing import Dict, List, Tuple
from cython_modules.graph_scheduler import PyScheduler
from exportador_horarios import ExportadorHorarios
from visualizacion_grafo import VisualizadorGrafo


class ConfiguracionSistema:
    """Carga y gestiona la configuración desde config.json"""
    
    def __init__(self, archivo_config="config.json"):
        self.archivo = archivo_config
        self.config = self.cargar()
    
    def cargar(self) -> Dict:
        """Carga la configuración desde el archivo JSON"""
        if not os.path.exists(self.archivo):
            return self.configuracion_por_defecto()
        
        with open(self.archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def guardar(self):
        """Guarda la configuración actual al archivo"""
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def configuracion_por_defecto(self) -> Dict:
        """Devuelve la configuración por defecto"""
        return {
            "Horas_Bloque": 55,
            "Horario_Inicio": "07:00",
            "Horario_Fin": "21:00",
            "Dias_Habiles": ["L", "M", "Mi", "J", "V"],
            "Duracion_Descanso": 30,
            "Peso_Continuidad": 10,
            "Max_Iteraciones": 1000,
            "Estrategia_Coloreado": "DSatur",
            "Formato_Celda": "Materia + Profesor",
            "Color_Disponible": "#00FF00",
            "Color_Ocupado": "#ADD8E6",
            "Nombre_Archivo_Output": "Horario_Generado.xlsx"
        }
    
    def get(self, clave: str, default=None):
        """Obtiene un valor de configuración"""
        return self.config.get(clave, default)
    
    def set(self, clave: str, valor):
        """Establece un valor de configuración"""
        self.config[clave] = valor


class SistemaHorarios:
    """Sistema principal de generación de horarios usando Graph Coloring"""
    
    def __init__(self, archivo_config="config.json"):
        self.config = ConfiguracionSistema(archivo_config)
        self.scheduler = None
        self.profesores = []
        self.grupos = []
        self.materias = []
        self.eventos = []
        self.resultados = None
    
    def cargar_datos(self, archivo_datos: str):
        """Carga profesores, grupos y materias desde un archivo JSON"""
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        self.profesores = datos.get('profesores', [])
        self.grupos = datos.get('grupos', [])
        self.materias = datos.get('materias', [])
        
        print(f"✓ Cargados {len(self.profesores)} profesores")
        print(f"✓ Cargados {len(self.grupos)} grupos")
        print(f"✓ Cargadas {len(self.materias)} materias")
    
    def generar_eventos(self):
        """Genera eventos a partir de las materias"""
        self.eventos = []
        evento_id = 0
        
        for materia in self.materias:
            grupo = materia['grupo']
            nombre_materia = materia['materia']
            horas = materia['horas']
            profesor = materia.get('profesor', 'Sin asignar')
            
            # Crear un evento por cada materia
            evento = {
                'id': evento_id,
                'grupo': grupo,
                'materia': nombre_materia,
                'profesor': profesor,
                'horas': horas
            }
            self.eventos.append(evento)
            evento_id += 1
        
        print(f"✓ Generados {len(self.eventos)} eventos")
        return self.eventos
    
    def ejecutar_algoritmo(self):
        """Ejecuta el algoritmo de Graph Coloring"""
        if not self.eventos:
            self.generar_eventos()
        
        # Crear scheduler con configuración
        estrategia = self.config.get('Estrategia_Coloreado', 'DSatur')
        peso_continuidad = self.config.get('Peso_Continuidad', 10)
        max_iter = self.config.get('Max_Iteraciones', 1000)
        
        print(f"\n🔧 Configuración:")
        print(f"  • Estrategia: {estrategia}")
        print(f"  • Peso continuidad: {peso_continuidad}")
        print(f"  • Max iteraciones: {max_iter}")
        
        self.scheduler = PyScheduler(
            peso_continuidad=peso_continuidad,
            max_iteraciones=max_iter,
            estrategia=estrategia
        )
        
        # Agregar eventos al scheduler
        print(f"\n📊 Agregando {len(self.eventos)} eventos al scheduler...")
        for evento in self.eventos:
            self.scheduler.agregar_evento(
                evento['id'],
                evento['materia'],
                evento['profesor'],
                evento['grupo'],
                evento['horas']
            )
        
        # Ejecutar
        print("🚀 Ejecutando algoritmo de coloreado...")
        exito = self.scheduler.ejecutar()
        
        if exito:
            print("✓ Algoritmo ejecutado exitosamente")
            self.resultados = {
                'asignaciones': self.scheduler.obtener_asignaciones(),
                'conflictos': self.scheduler.obtener_conflictos(),
                'metricas': self.scheduler.obtener_metricas(),
                'info_grafo': self.scheduler.obtener_info_grafo(),
                'matriz_adyacencia': self.scheduler.obtener_matriz_adyacencia()
            }
            return True
        else:
            print("✗ Error al ejecutar algoritmo")
            return False
    
    def mostrar_resultados(self):
        """Muestra los resultados del algoritmo"""
        if not self.resultados:
            print("No hay resultados disponibles")
            return
        
        metricas = self.resultados['metricas']
        print("\n" + "=" * 70)
        print("📈 MÉTRICAS DE EJECUCIÓN")
        print("=" * 70)
        print(f"⏱️  Tiempo de ejecución: {metricas['tiempo_ejecucion_ms']:.2f} ms")
        print(f"🔄 Iteraciones: {metricas['iteraciones']}")
        print(f"🎨 Colores (timeslots) usados: {metricas['colores_usados']}")
        print(f"⚠️  Conflictos detectados: {metricas['conflictos_totales']}")
        print(f"📊 Penalización por huecos: {metricas['penalizacion_huecos']}")
        print(f"✨ Calidad de solución: {metricas['calidad_solucion']:.2f}%")
        
        info_grafo = self.resultados['info_grafo']
        print("\n" + "=" * 70)
        print("🔗 INFORMACIÓN DEL GRAFO")
        print("=" * 70)
        print(f"📍 Nodos (eventos): {info_grafo['nodos']}")
        print(f"🔗 Aristas (conflictos): {info_grafo['aristas']}")
        print(f"📊 Grado máximo: {info_grafo['grado_maximo']}")
        print(f"📈 Grado promedio: {info_grafo['grado_promedio']:.2f}")
        
        asignaciones = self.resultados['asignaciones']
        print("\n" + "=" * 70)
        print(f"📅 ASIGNACIONES DE HORARIOS (primeras 10 de {len(asignaciones)})")
        print("=" * 70)
        
        for i, asig in enumerate(asignaciones[:10]):
            evento = self.eventos[asig['evento_id']]
            print(f"{i+1:2d}. {evento['grupo']:10s} | {evento['materia']:25s} | "
                  f"{asig['dia']:2s} {asig['hora']:5s} (slot {asig['timeslot']:2d})")
    
    def exportar_matriz_csv(self, archivo_salida="matriz_adyacencia.csv"):
        """Exporta la matriz de adyacencia a CSV"""
        if not self.resultados:
            print("No hay resultados para exportar")
            return
        
        matriz = self.resultados['matriz_adyacencia']
        with open(archivo_salida, 'w') as f:
            for fila in matriz:
                f.write(','.join(map(str, fila)) + '\n')
        
        print(f"✓ Matriz exportada a {archivo_salida}")
    
    def exportar_resultados_json(self, archivo_salida="resultados.json"):
        """Exporta todos los resultados a JSON"""
        if not self.resultados:
            print("No hay resultados para exportar")
            return
        
        # Preparar datos para exportar
        datos_export = {
            'configuracion': self.config.config,
            'metricas': self.resultados['metricas'],
            'info_grafo': self.resultados['info_grafo'],
            'asignaciones': [],
            'conflictos': self.resultados['conflictos']
        }
        
        # Enriquecer asignaciones con información de eventos
        for asig in self.resultados['asignaciones']:
            evento = self.eventos[asig['evento_id']]
            datos_export['asignaciones'].append({
                'grupo': evento['grupo'],
                'materia': evento['materia'],
                'profesor': evento['profesor'],
                'horas': evento['horas'],
                'dia': asig['dia'],
                'hora': asig['hora'],
                'timeslot': asig['timeslot']
            })
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos_export, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Resultados exportados a {archivo_salida}")
    
    def exportar_excel_completo(self, archivo_salida: str = "horarios_completos.xlsx"):
        """Exporta TODOS los horarios a Excel"""
        if not self.resultados:
            print("No hay resultados para exportar")
            return None
        
        exportador = ExportadorHorarios()
        archivo = exportador.exportar_excel(
            self.resultados['asignaciones'],
            self.eventos,
            self.resultados['metricas'],
            archivo_salida
        )
        print(f"✓ Horarios exportados a Excel: {archivo}")
        return archivo
    
    def exportar_html_completo(self, archivo_salida: str = "horarios_completos.html"):
        """Exporta TODOS los horarios a HTML"""
        if not self.resultados:
            print("No hay resultados para exportar")
            return None
        
        exportador = ExportadorHorarios()
        archivo = exportador.exportar_html(
            self.resultados['asignaciones'],
            self.eventos,
            self.resultados['metricas'],
            self.resultados['info_grafo'],
            archivo_salida
        )
        print(f"✓ Horarios exportados a HTML: {archivo}")
        return archivo
    
    def generar_visualizacion_grafo(self, archivo_salida: str = "grafo_conflictos.png"):
        """Genera visualización del grafo de conflictos"""
        if not self.resultados:
            print("No hay resultados para visualizar")
            return None, None
        
        visualizador = VisualizadorGrafo()
        visualizador.crear_grafo_desde_matriz(
            self.resultados['matriz_adyacencia'],
            self.resultados['asignaciones'],
            self.eventos
        )
        
        ruta = visualizador.visualizar(archivo_salida)
        stats = visualizador.obtener_estadisticas()
        
        print(f"✓ Grafo visualizado en: {ruta}")
        return ruta, stats


def main():
    """Función principal de prueba"""
    print("=" * 70)
    print("SISTEMA DE GENERACIÓN DE HORARIOS - GRAPH COLORING")
    print("Universidad Politécnica de Victoria")
    print("=" * 70)
    
    # Crear sistema
    sistema = SistemaHorarios("config.json")
    
    # Cargar datos
    sistema.cargar_datos("data/datos_completos.json")
    
    # Ejecutar algoritmo
    if sistema.ejecutar_algoritmo():
        # Mostrar resultados
        sistema.mostrar_resultados()
        
        # Exportar
        sistema.exportar_matriz_csv()
        sistema.exportar_resultados_json()
    
    print("\n" + "=" * 70)
    print("✅ Proceso completado")
    print("=" * 70)


if __name__ == "__main__":
    main()
