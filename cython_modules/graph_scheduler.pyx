# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

"""
Cython wrapper para el Scheduler de Graph Coloring en C++.
Permite usar los algoritmos DSatur y Welsh-Powell desde Python.
"""

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool

# Declaración de estructuras C++
cdef extern from "../include/scheduler.h":
    cdef cppclass Evento:
        int id
        string materia
        string profesor
        string grupo
        int horas_necesarias
        int color
        Evento() except +
        Evento(int, string, string, string, int) except +
    
    cdef cppclass Asignacion:
        int evento_id
        int timeslot
        string dia
        string hora
        Asignacion() except +
    
    cdef cppclass Metricas:
        double tiempo_ejecucion_ms
        int iteraciones
        int colores_usados
        int conflictos_totales
        int penalizacion_huecos
        double calidad_solucion
        Metricas() except +
    
    cdef cppclass Conflicto:
        int evento1_id
        int evento2_id
        string razon
        Conflicto(int, int, string) except +
    
    cdef cppclass GrafoEventos:
        int num_nodos() const
        int grado(int) const
        bool existe_arista(int, int) const
        vector[vector[int]] obtener_matriz_adyacencia() const
    
    cdef cppclass Scheduler:
        Scheduler(int, int, string) except +
        void agregar_evento(int, string, string, string, int)
        bool ejecutar()
        const vector[Asignacion]& obtener_asignaciones() const
        const vector[Conflicto]& obtener_conflictos() const
        const Metricas& obtener_metricas() const
        const GrafoEventos* obtener_grafo() const
        void limpiar()
        
        @staticmethod
        string timeslot_a_dia(int)
        
        @staticmethod
        string timeslot_a_hora(int, int)


# Clase Python que envuelve el Scheduler C++
cdef class PyScheduler:
    cdef Scheduler* scheduler
    
    def __cinit__(self, int peso_continuidad=10, int max_iteraciones=1000, str estrategia="DSatur"):
        """
        Inicializa el scheduler de Graph Coloring.
        
        Args:
            peso_continuidad: Penalización por cada hueco entre clases
            max_iteraciones: Máximo de iteraciones para el algoritmo
            estrategia: "DSatur" o "Welsh-Powell"
        """
        cdef string estrat = estrategia.encode('utf-8')
        self.scheduler = new Scheduler(peso_continuidad, max_iteraciones, estrat)
    
    def __dealloc__(self):
        if self.scheduler is not NULL:
            del self.scheduler
    
    def agregar_evento(self, int evento_id, str materia, str profesor, str grupo, int horas):
        """
        Agrega un evento (clase) al scheduler.
        
        Args:
            evento_id: ID único del evento
            materia: Nombre de la materia
            profesor: Nombre del profesor
            grupo: Nombre del grupo (ej: "ITI 5-1")
            horas: Horas semanales necesarias
        """
        cdef string mat = materia.encode('utf-8')
        cdef string prof = profesor.encode('utf-8')
        cdef string grp = grupo.encode('utf-8')
        
        self.scheduler.agregar_evento(evento_id, mat, prof, grp, horas)
    
    def ejecutar(self):
        """
        Ejecuta el algoritmo de coloreado de grafos.
        
        Returns:
            bool: True si se ejecutó correctamente
        """
        return self.scheduler.ejecutar()
    
    def obtener_asignaciones(self):
        """
        Obtiene las asignaciones de timeslots a eventos.
        
        Returns:
            list: Lista de diccionarios con asignaciones
        """
        cdef vector[Asignacion] asignaciones = self.scheduler.obtener_asignaciones()
        cdef list resultado = []
        cdef size_t i
        
        for i in range(asignaciones.size()):
            resultado.append({
                'evento_id': asignaciones[i].evento_id,
                'timeslot': asignaciones[i].timeslot,
                'dia': asignaciones[i].dia.decode('utf-8'),
                'hora': asignaciones[i].hora.decode('utf-8')
            })
        
        return resultado
    
    def obtener_conflictos(self):
        """
        Obtiene los conflictos detectados en el grafo.
        
        Returns:
            list: Lista de diccionarios con conflictos
        """
        cdef vector[Conflicto] conflictos = self.scheduler.obtener_conflictos()
        cdef list resultado = []
        cdef size_t i
        
        for i in range(conflictos.size()):
            resultado.append({
                'evento1_id': conflictos[i].evento1_id,
                'evento2_id': conflictos[i].evento2_id,
                'razon': conflictos[i].razon.decode('utf-8')
            })
        
        return resultado
    
    def obtener_metricas(self):
        """
        Obtiene las métricas de ejecución del algoritmo.
        
        Returns:
            dict: Diccionario con métricas
        """
        cdef Metricas metricas = self.scheduler.obtener_metricas()
        
        return {
            'tiempo_ejecucion_ms': metricas.tiempo_ejecucion_ms,
            'iteraciones': metricas.iteraciones,
            'colores_usados': metricas.colores_usados,
            'conflictos_totales': metricas.conflictos_totales,
            'penalizacion_huecos': metricas.penalizacion_huecos,
            'calidad_solucion': metricas.calidad_solucion
        }
    
    def obtener_matriz_adyacencia(self):
        """
        Obtiene la matriz de adyacencia del grafo de conflictos.
        
        Returns:
            list: Matriz de adyacencia como lista de listas
        """
        cdef const GrafoEventos* grafo = self.scheduler.obtener_grafo()
        if grafo is NULL:
            return []
        
        cdef vector[vector[int]] matriz = grafo.obtener_matriz_adyacencia()
        cdef list resultado = []
        cdef size_t i, j
        
        for i in range(matriz.size()):
            fila = []
            for j in range(matriz[i].size()):
                fila.append(matriz[i][j])
            resultado.append(fila)
        
        return resultado
    
    def obtener_info_grafo(self):
        """
        Obtiene información básica del grafo.
        
        Returns:
            dict: Información del grafo (nodos, aristas, grados)
        """
        cdef const GrafoEventos* grafo = self.scheduler.obtener_grafo()
        if grafo is NULL:
            return {'nodos': 0, 'aristas': 0}
        
        cdef int num_nodos = grafo.num_nodos()
        cdef list grados = []
        cdef int i
        
        for i in range(num_nodos):
            grados.append(grafo.grado(i))
        
        # Calcular número de aristas
        cdef int num_aristas = sum(grados) // 2
        
        return {
            'nodos': num_nodos,
            'aristas': num_aristas,
            'grados': grados,
            'grado_maximo': max(grados) if grados else 0,
            'grado_promedio': sum(grados) / len(grados) if grados else 0
        }
    
    def limpiar(self):
        """Limpia todos los datos del scheduler."""
        self.scheduler.limpiar()
    
    @staticmethod
    def timeslot_a_dia(int timeslot):
        """Convierte un timeslot a día de la semana."""
        return Scheduler.timeslot_a_dia(timeslot).decode('utf-8')
    
    @staticmethod
    def timeslot_a_hora(int timeslot, int duracion_bloque=55):
        """Convierte un timeslot a hora del día."""
        return Scheduler.timeslot_a_hora(timeslot, duracion_bloque).decode('utf-8')
