#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <vector>
#include <map>
#include <set>
#include <string>
#include <algorithm>
#include <ctime>

using namespace std;

// ==================== ESTRUCTURAS PARA SCHEDULING ====================

struct Evento {
    int id;
    string materia;
    string profesor;
    string grupo;
    int horas_necesarias;
    int color;  // Timeslot asignado (-1 si no asignado)
    
    Evento() : id(0), horas_necesarias(0), color(-1) {}
    Evento(int i, string m, string p, string g, int h) 
        : id(i), materia(m), profesor(p), grupo(g), horas_necesarias(h), color(-1) {}
};

struct Conflicto {
    int evento1_id;
    int evento2_id;
    string razon;
    
    Conflicto(int e1, int e2, string r) : evento1_id(e1), evento2_id(e2), razon(r) {}
};

struct Asignacion {
    int evento_id;
    int timeslot;
    string dia;
    string hora;
    
    Asignacion() : evento_id(0), timeslot(0) {}
};

struct Metricas {
    double tiempo_ejecucion_ms;
    int iteraciones;
    int colores_usados;
    int conflictos_totales;
    int penalizacion_huecos;
    double calidad_solucion;
    
    Metricas() : tiempo_ejecucion_ms(0), iteraciones(0), colores_usados(0), 
                 conflictos_totales(0), penalizacion_huecos(0), calidad_solucion(0) {}
};

// ==================== GRAFO DE CONFLICTOS ====================

class GrafoEventos {
private:
    int num_vertices;
    vector<set<int>> lista_adyacencia;  // Conjunto de vecinos para cada nodo
    
public:
    GrafoEventos(int n);
    void agregar_arista(int u, int v);
    bool existe_arista(int u, int v) const;
    const set<int>& obtener_vecinos(int vertice) const;
    int grado(int vertice) const;
    int num_nodos() const { return num_vertices; }
    
    // Para exportar matriz de adyacencia
    vector<vector<int>> obtener_matriz_adyacencia() const;
};

// ==================== SCHEDULER PRINCIPAL ====================

class Scheduler {
private:
    // Datos de entrada
    vector<Evento> eventos;
    GrafoEventos* grafo;
    
    // Parámetros de configuración
    int peso_continuidad;
    int max_iteraciones;
    string estrategia;  // "DSatur" o "Welsh-Powell"
    
    // Mapas para rastrear asignaciones
    map<int, set<int>> profesor_timeslots;     // profesor -> conjunto de timeslots ocupados
    map<int, set<int>> grupo_timeslots;        // grupo -> conjunto de timeslots ocupados
    
    // Mapas de nombres a IDs
    map<string, int> profesor_id_map;
    map<string, int> grupo_id_map;
    
    // Resultados
    vector<Asignacion> asignaciones;
    vector<Conflicto> conflictos_detectados;
    Metricas metricas;
    
    // Funciones auxiliares
    void construir_grafo_conflictos();
    bool hay_conflicto(const Evento& e1, const Evento& e2) const;
    int calcular_saturacion(int evento_id, const vector<int>& colores) const;
    int calcular_penalizacion_huecos(const vector<int>& colores) const;
    bool es_valido_asignar(int evento_id, int color, const vector<int>& colores) const;
    
    // Algoritmos de coloreado
    vector<int> dsatur();
    vector<int> welsh_powell();
    
    int obtener_profesor_id(const string& nombre);
    int obtener_grupo_id(const string& nombre);
    
public:
    Scheduler(int peso_cont = 10, int max_iter = 1000, string estrat = "DSatur");
    ~Scheduler();
    
    // Métodos públicos
    void agregar_evento(const Evento& evento);
    void agregar_evento(int id, string materia, string profesor, string grupo, int horas);
    
    bool ejecutar();  // Ejecuta el algoritmo seleccionado
    
    // Getters de resultados
    const vector<Asignacion>& obtener_asignaciones() const { return asignaciones; }
    const vector<Conflicto>& obtener_conflictos() const { return conflictos_detectados; }
    const Metricas& obtener_metricas() const { return metricas; }
    const GrafoEventos* obtener_grafo() const { return grafo; }
    
    // Conversión de timeslot a día/hora legible
    static string timeslot_a_dia(int timeslot);
    static string timeslot_a_hora(int timeslot, int duracion_bloque = 55);
    
    void limpiar();
};

#endif // SCHEDULER_H
