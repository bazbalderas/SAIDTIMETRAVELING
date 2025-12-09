#include "../include/scheduler.h"
#include <iostream>
#include <queue>
#include <chrono>
#include <sstream>
#include <iomanip>

using namespace std;

// ==================== IMPLEMENTACIÓN GRAFO ====================

GrafoEventos::GrafoEventos(int n) : num_vertices(n) {
    lista_adyacencia.resize(n);
}

void GrafoEventos::agregar_arista(int u, int v) {
    if (u >= 0 && u < num_vertices && v >= 0 && v < num_vertices && u != v) {
        lista_adyacencia[u].insert(v);
        lista_adyacencia[v].insert(u);
    }
}

bool GrafoEventos::existe_arista(int u, int v) const {
    if (u >= 0 && u < num_vertices && v >= 0 && v < num_vertices) {
        return lista_adyacencia[u].find(v) != lista_adyacencia[u].end();
    }
    return false;
}

const set<int>& GrafoEventos::obtener_vecinos(int vertice) const {
    static set<int> vacio;
    if (vertice >= 0 && vertice < num_vertices) {
        return lista_adyacencia[vertice];
    }
    return vacio;
}

int GrafoEventos::grado(int vertice) const {
    if (vertice >= 0 && vertice < num_vertices) {
        return lista_adyacencia[vertice].size();
    }
    return 0;
}

vector<vector<int>> GrafoEventos::obtener_matriz_adyacencia() const {
    vector<vector<int>> matriz(num_vertices, vector<int>(num_vertices, 0));
    for (int i = 0; i < num_vertices; i++) {
        for (int j : lista_adyacencia[i]) {
            matriz[i][j] = 1;
        }
    }
    return matriz;
}

// ==================== IMPLEMENTACIÓN SCHEDULER ====================

Scheduler::Scheduler(int peso_cont, int max_iter, string estrat)
    : grafo(nullptr), peso_continuidad(peso_cont), max_iteraciones(max_iter), estrategia(estrat) {
}

Scheduler::~Scheduler() {
    if (grafo) {
        delete grafo;
    }
}

void Scheduler::agregar_evento(const Evento& evento) {
    eventos.push_back(evento);
}

void Scheduler::agregar_evento(int id, string materia, string profesor, string grupo, int horas) {
    Evento e(id, materia, profesor, grupo, horas);
    eventos.push_back(e);
}

int Scheduler::obtener_profesor_id(const string& nombre) {
    if (profesor_id_map.find(nombre) == profesor_id_map.end()) {
        int nuevo_id = profesor_id_map.size();
        profesor_id_map[nombre] = nuevo_id;
    }
    return profesor_id_map[nombre];
}

int Scheduler::obtener_grupo_id(const string& nombre) {
    if (grupo_id_map.find(nombre) == grupo_id_map.end()) {
        int nuevo_id = grupo_id_map.size();
        grupo_id_map[nombre] = nuevo_id;
    }
    return grupo_id_map[nombre];
}

bool Scheduler::hay_conflicto(const Evento& e1, const Evento& e2) const {
    // Hay conflicto si comparten profesor o grupo
    return (e1.profesor == e2.profesor) || (e1.grupo == e2.grupo);
}

void Scheduler::construir_grafo_conflictos() {
    if (grafo) {
        delete grafo;
    }
    
    grafo = new GrafoEventos(eventos.size());
    conflictos_detectados.clear();
    
    // Construir aristas entre eventos que tienen conflicto
    for (size_t i = 0; i < eventos.size(); i++) {
        for (size_t j = i + 1; j < eventos.size(); j++) {
            if (hay_conflicto(eventos[i], eventos[j])) {
                grafo->agregar_arista(i, j);
                
                string razon;
                if (eventos[i].profesor == eventos[j].profesor) {
                    razon = "Mismo profesor: " + eventos[i].profesor;
                } else {
                    razon = "Mismo grupo: " + eventos[i].grupo;
                }
                conflictos_detectados.push_back(Conflicto(i, j, razon));
            }
        }
    }
}

int Scheduler::calcular_saturacion(int evento_id, const vector<int>& colores) const {
    // Saturación = número de colores diferentes usados por vecinos
    set<int> colores_vecinos;
    
    const set<int>& vecinos = grafo->obtener_vecinos(evento_id);
    for (int vecino : vecinos) {
        if (colores[vecino] != -1) {
            colores_vecinos.insert(colores[vecino]);
        }
    }
    
    return colores_vecinos.size();
}

bool Scheduler::es_valido_asignar(int evento_id, int color, const vector<int>& colores) const {
    // Verificar que ningún vecino tenga el mismo color
    const set<int>& vecinos = grafo->obtener_vecinos(evento_id);
    for (int vecino : vecinos) {
        if (colores[vecino] == color) {
            return false;
        }
    }
    return true;
}

int Scheduler::calcular_penalizacion_huecos(const vector<int>& colores) const {
    int penalizacion = 0;
    
    // Para cada grupo, calcular huecos en su horario
    map<string, vector<int>> horarios_grupo;
    
    for (size_t i = 0; i < eventos.size(); i++) {
        if (colores[i] != -1) {
            horarios_grupo[eventos[i].grupo].push_back(colores[i]);
        }
    }
    
    // Contar huecos para cada grupo
    for (auto& par : horarios_grupo) {
        vector<int>& slots = par.second;
        if (slots.size() < 2) continue;
        
        sort(slots.begin(), slots.end());
        
        for (size_t i = 1; i < slots.size(); i++) {
            int gap = slots[i] - slots[i-1] - 1;
            if (gap > 0) {
                penalizacion += gap * peso_continuidad;
            }
        }
    }
    
    return penalizacion;
}

vector<int> Scheduler::dsatur() {
    int n = eventos.size();
    vector<int> colores(n, -1);  // -1 = sin colorear
    vector<bool> coloreado(n, false);
    
    int iteracion = 0;
    
    while (iteracion < max_iteraciones) {
        iteracion++;
        
        // Encontrar nodo sin colorear con mayor saturación
        // En caso de empate, usar el de mayor grado
        int max_sat = -1;
        int max_grado = -1;
        int nodo_elegido = -1;
        
        for (int i = 0; i < n; i++) {
            if (!coloreado[i]) {
                int sat = calcular_saturacion(i, colores);
                int deg = grafo->grado(i);
                
                if (sat > max_sat || (sat == max_sat && deg > max_grado)) {
                    max_sat = sat;
                    max_grado = deg;
                    nodo_elegido = i;
                }
            }
        }
        
        // Si no hay más nodos por colorear, terminar
        if (nodo_elegido == -1) {
            break;
        }
        
        // Encontrar el menor color válido para este nodo
        int color = 0;
        while (!es_valido_asignar(nodo_elegido, color, colores)) {
            color++;
        }
        
        colores[nodo_elegido] = color;
        coloreado[nodo_elegido] = true;
    }
    
    metricas.iteraciones = iteracion;
    return colores;
}

vector<int> Scheduler::welsh_powell() {
    int n = eventos.size();
    vector<int> colores(n, -1);
    
    // Crear lista de nodos ordenados por grado (descendente)
    vector<pair<int, int>> nodos_grado;
    for (int i = 0; i < n; i++) {
        nodos_grado.push_back({grafo->grado(i), i});
    }
    sort(nodos_grado.rbegin(), nodos_grado.rend());
    
    int iteracion = 0;
    
    // Colorear nodos en orden de grado
    for (auto& par : nodos_grado) {
        int nodo = par.second;
        iteracion++;
        
        if (iteracion > max_iteraciones) break;
        
        // Encontrar el menor color válido
        int color = 0;
        while (!es_valido_asignar(nodo, color, colores)) {
            color++;
        }
        
        colores[nodo] = color;
    }
    
    metricas.iteraciones = iteracion;
    return colores;
}

bool Scheduler::ejecutar() {
    auto inicio = chrono::high_resolution_clock::now();
    
    // Paso 1: Construir grafo de conflictos
    construir_grafo_conflictos();
    
    // Paso 2: Aplicar algoritmo de coloreado seleccionado
    vector<int> colores;
    if (estrategia == "Welsh-Powell") {
        colores = welsh_powell();
    } else {
        colores = dsatur();  // Por defecto DSatur
    }
    
    // Paso 3: Convertir colores a asignaciones
    asignaciones.clear();
    set<int> colores_unicos;
    
    for (size_t i = 0; i < eventos.size(); i++) {
        if (colores[i] != -1) {
            eventos[i].color = colores[i];
            colores_unicos.insert(colores[i]);
            
            Asignacion asig;
            asig.evento_id = i;
            asig.timeslot = colores[i];
            asig.dia = timeslot_a_dia(colores[i]);
            asig.hora = timeslot_a_hora(colores[i]);
            asignaciones.push_back(asig);
        }
    }
    
    // Paso 4: Calcular métricas
    auto fin = chrono::high_resolution_clock::now();
    auto duracion = chrono::duration_cast<chrono::milliseconds>(fin - inicio);
    
    metricas.tiempo_ejecucion_ms = duracion.count();
    metricas.colores_usados = colores_unicos.size();
    metricas.conflictos_totales = conflictos_detectados.size();
    metricas.penalizacion_huecos = calcular_penalizacion_huecos(colores);
    
    // Calidad: 100% si no hay conflictos, reducida por huecos
    metricas.calidad_solucion = 100.0 - (metricas.penalizacion_huecos * 0.1);
    if (metricas.calidad_solucion < 0) metricas.calidad_solucion = 0;
    
    return true;
}

string Scheduler::timeslot_a_dia(int timeslot) {
    const char* dias[] = {"L", "M", "Mi", "J", "V"};
    const int num_dias = sizeof(dias) / sizeof(dias[0]);
    int slots_por_dia = 15;  // 15 slots de 55 min por día (7:00 a 19:50)
    int dia = timeslot / slots_por_dia;
    
    if (dia >= 0 && dia < num_dias) {
        return dias[dia];
    }
    return "?";
}

string Scheduler::timeslot_a_hora(int timeslot, int duracion_bloque) {
    int slots_por_dia = 15;  // 15 slots de 55 min por día
    int slot_en_dia = timeslot % slots_por_dia;
    
    // Hora de inicio: 7:00 AM
    int minutos_inicio = 7 * 60;  // 7:00 AM en minutos
    int minutos_totales = minutos_inicio + (slot_en_dia * duracion_bloque);
    
    int hora = minutos_totales / 60;
    int minuto = minutos_totales % 60;
    
    ostringstream oss;
    oss << setfill('0') << setw(2) << hora << ":" << setw(2) << minuto;
    return oss.str();
}

void Scheduler::limpiar() {
    eventos.clear();
    asignaciones.clear();
    conflictos_detectados.clear();
    profesor_timeslots.clear();
    grupo_timeslots.clear();
    profesor_id_map.clear();
    grupo_id_map.clear();
    
    if (grafo) {
        delete grafo;
        grafo = nullptr;
    }
    
    metricas = Metricas();
}
