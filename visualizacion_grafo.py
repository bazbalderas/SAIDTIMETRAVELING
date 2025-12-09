#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Visualización del Grafo de Conflictos
Genera visualización interactiva usando networkx y matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para generación de imágenes
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import List, Dict, Tuple
import os


class VisualizadorGrafo:
    """Visualiza el grafo de conflictos de eventos"""
    
    def __init__(self):
        self.grafo = None
        self.colores_nodos = []
        self.posiciones = None
        
    def crear_grafo_desde_matriz(self, matriz_adyacencia: List[List[int]], 
                                  asignaciones: List[Dict],
                                  eventos: List[Dict]) -> nx.Graph:
        """
        Crea un grafo de NetworkX desde la matriz de adyacencia
        
        Args:
            matriz_adyacencia: Matriz de adyacencia del grafo de conflictos
            asignaciones: Lista de asignaciones de timeslots
            eventos: Lista de eventos con información de materia/grupo
            
        Returns:
            Grafo de NetworkX
        """
        n = len(matriz_adyacencia)
        self.grafo = nx.Graph()
        
        # Agregar nodos con información
        for i in range(n):
            if i < len(eventos):
                evento = eventos[i]
                label = f"{evento['grupo']}\n{evento['materia'][:15]}"
                self.grafo.add_node(i, label=label, evento=evento)
            else:
                self.grafo.add_node(i, label=f"E{i}")
        
        # Agregar aristas desde la matriz
        for i in range(n):
            for j in range(i + 1, n):
                if matriz_adyacencia[i][j] == 1:
                    self.grafo.add_edge(i, j)
        
        # Asignar colores según timeslot
        self.colores_nodos = self._generar_colores_timeslots(asignaciones, n)
        
        return self.grafo
    
    def _generar_colores_timeslots(self, asignaciones: List[Dict], n: int) -> List[str]:
        """
        Genera colores para los nodos según su timeslot asignado
        
        Args:
            asignaciones: Lista de asignaciones con timeslots
            n: Número de nodos
            
        Returns:
            Lista de colores en formato hexadecimal
        """
        # Crear mapa de timeslot a color
        timeslots = set()
        for asig in asignaciones:
            timeslots.add(asig.get('timeslot', 0))
        
        num_timeslots = len(timeslots)
        
        # Generar paleta de colores distribuida
        if num_timeslots > 0:
            cmap = plt.cm.get_cmap('hsv', num_timeslots + 1)
            colores_timeslot = {}
            
            for idx, ts in enumerate(sorted(timeslots)):
                colores_timeslot[ts] = matplotlib.colors.rgb2hex(cmap(idx))
        else:
            colores_timeslot = {}
        
        # Asignar color a cada nodo
        colores = []
        for i in range(n):
            if i < len(asignaciones):
                ts = asignaciones[i].get('timeslot', 0)
                colores.append(colores_timeslot.get(ts, '#CCCCCC'))
            else:
                colores.append('#CCCCCC')
        
        return colores
    
    def visualizar(self, archivo_salida: str = "grafo_conflictos.png",
                   mostrar_etiquetas: bool = True,
                   tamaño_figura: Tuple[int, int] = (16, 12)) -> str:
        """
        Genera la visualización del grafo y la guarda en un archivo
        
        Args:
            archivo_salida: Ruta del archivo de salida
            mostrar_etiquetas: Si True, muestra etiquetas de nodos
            tamaño_figura: Tamaño de la figura (ancho, alto)
            
        Returns:
            Ruta del archivo generado
        """
        if self.grafo is None:
            raise ValueError("Primero debe crear el grafo con crear_grafo_desde_matriz()")
        
        # Crear figura
        plt.figure(figsize=tamaño_figura)
        plt.clf()
        
        # Calcular layout
        if len(self.grafo.nodes()) > 50:
            # Para grafos grandes, usar layout más rápido
            self.posiciones = nx.spring_layout(self.grafo, k=1, iterations=30, seed=42)
        else:
            # Para grafos pequeños, usar spring layout de mejor calidad
            # kamada_kawai requiere scipy, por lo que usamos spring como alternativa confiable
            self.posiciones = nx.spring_layout(self.grafo, k=1, iterations=50, seed=42)
        
        # Dibujar aristas (conflictos)
        nx.draw_networkx_edges(
            self.grafo, 
            self.posiciones,
            alpha=0.3,
            width=1.0,
            edge_color='#666666'
        )
        
        # Dibujar nodos
        nx.draw_networkx_nodes(
            self.grafo,
            self.posiciones,
            node_color=self.colores_nodos,
            node_size=800,
            alpha=0.9,
            edgecolors='black',
            linewidths=2.0
        )
        
        # Dibujar etiquetas si se requiere
        if mostrar_etiquetas and len(self.grafo.nodes()) <= 50:
            # Solo mostrar etiquetas si el grafo no es muy grande
            labels = nx.get_node_attributes(self.grafo, 'label')
            if not labels:
                labels = {i: str(i) for i in self.grafo.nodes()}
            
            nx.draw_networkx_labels(
                self.grafo,
                self.posiciones,
                labels,
                font_size=8,
                font_color='white',
                font_weight='bold'
            )
        elif mostrar_etiquetas:
            # Para grafos grandes, solo mostrar IDs
            labels = {i: str(i) for i in self.grafo.nodes()}
            nx.draw_networkx_labels(
                self.grafo,
                self.posiciones,
                labels,
                font_size=6,
                font_color='white'
            )
        
        # Información del grafo
        num_nodos = self.grafo.number_of_nodes()
        num_aristas = self.grafo.number_of_edges()
        
        # Título y metadatos
        plt.title(
            f'Grafo de Conflictos de Horarios\n'
            f'Nodos (Eventos): {num_nodos} | Aristas (Conflictos): {num_aristas}',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        
        # Agregar leyenda
        self._agregar_leyenda()
        
        plt.axis('off')
        plt.tight_layout()
        
        # Guardar
        plt.savefig(archivo_salida, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return os.path.abspath(archivo_salida)
    
    def _agregar_leyenda(self):
        """Agrega una leyenda explicativa al grafo"""
        from matplotlib.lines import Line2D
        
        # Elementos de la leyenda
        elementos = [
            Line2D([0], [0], marker='o', color='w', 
                   markerfacecolor='#FF6B6B', markersize=10, 
                   label='Nodos = Eventos/Clases'),
            Line2D([0], [0], color='#666666', linewidth=2, 
                   label='Aristas = Conflictos'),
            Line2D([0], [0], marker='o', color='w', 
                   markerfacecolor='#4ECDC4', markersize=10, 
                   label='Color = Timeslot asignado')
        ]
        
        plt.legend(handles=elementos, loc='upper right', fontsize=10,
                  framealpha=0.9, edgecolor='black')
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas del grafo
        
        Returns:
            Diccionario con estadísticas
        """
        if self.grafo is None:
            return {}
        
        grados = [self.grafo.degree(n) for n in self.grafo.nodes()]
        
        stats = {
            'num_nodos': self.grafo.number_of_nodes(),
            'num_aristas': self.grafo.number_of_edges(),
            'grado_maximo': max(grados) if grados else 0,
            'grado_minimo': min(grados) if grados else 0,
            'grado_promedio': sum(grados) / len(grados) if grados else 0,
            'densidad': nx.density(self.grafo),
            'es_conexo': nx.is_connected(self.grafo) if self.grafo.number_of_nodes() > 0 else False,
            'num_componentes': nx.number_connected_components(self.grafo)
        }
        
        return stats


def generar_visualizacion_grafo(matriz_adyacencia: List[List[int]],
                                 asignaciones: List[Dict],
                                 eventos: List[Dict],
                                 archivo_salida: str = "grafo_conflictos.png") -> Tuple[str, Dict]:
    """
    Función auxiliar para generar visualización del grafo
    
    Args:
        matriz_adyacencia: Matriz de adyacencia del grafo
        asignaciones: Lista de asignaciones
        eventos: Lista de eventos
        archivo_salida: Nombre del archivo de salida
        
    Returns:
        Tupla (ruta_archivo, estadisticas)
    """
    viz = VisualizadorGrafo()
    viz.crear_grafo_desde_matriz(matriz_adyacencia, asignaciones, eventos)
    ruta = viz.visualizar(archivo_salida)
    stats = viz.obtener_estadisticas()
    
    return ruta, stats


if __name__ == "__main__":
    # Prueba simple
    print("Módulo de Visualización del Grafo")
    print("Para usar, importar: from visualizacion_grafo import VisualizadorGrafo")
