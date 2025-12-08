#include "../include/estructuras.h"
#include <iostream>

using namespace std;

// ==================== IMPLEMENTACIÓN GRAFO DE CONFLICTOS ====================

GrafoConflictos::GrafoConflictos(int n) : num_vertices(n) {
    lista_adyacencia = new Arista*[num_vertices];
    for (int i = 0; i < num_vertices; i++) {
        lista_adyacencia[i] = nullptr;
    }
}

GrafoConflictos::~GrafoConflictos() {
    for (int i = 0; i < num_vertices; i++) {
        Arista* actual = lista_adyacencia[i];
        while (actual != nullptr) {
            Arista* temp = actual;
            actual = actual->siguiente;
            delete temp;
        }
    }
    delete[] lista_adyacencia;
}

void GrafoConflictos::agregar_arista(int u, int v) {
    // Grafo no dirigido, agregamos en ambas direcciones
    if (u >= num_vertices || v >= num_vertices) return;
    
    // Agregar v a la lista de u
    Arista* nueva = new Arista(v);
    nueva->siguiente = lista_adyacencia[u];
    lista_adyacencia[u] = nueva;
    
    // Agregar u a la lista de v
    nueva = new Arista(u);
    nueva->siguiente = lista_adyacencia[v];
    lista_adyacencia[v] = nueva;
}

bool GrafoConflictos::existe_conflicto(int u, int v) {
    if (u >= num_vertices) return false;
    
    Arista* actual = lista_adyacencia[u];
    while (actual != nullptr) {
        if (actual->destino == v) return true;
        actual = actual->siguiente;
    }
    return false;
}

vector<int> GrafoConflictos::obtener_vecinos(int vertice) {
    vector<int> vecinos;
    if (vertice >= num_vertices) return vecinos;
    
    Arista* actual = lista_adyacencia[vertice];
    while (actual != nullptr) {
        vecinos.push_back(actual->destino);
        actual = actual->siguiente;
    }
    return vecinos;
}

void GrafoConflictos::mostrar_grafo() {
    cout << "\n=== GRAFO DE CONFLICTOS ===" << endl;
    for (int i = 0; i < num_vertices; i++) {
        cout << "Evento " << i << " -> ";
        Arista* actual = lista_adyacencia[i];
        while (actual != nullptr) {
            cout << actual->destino << " ";
            actual = actual->siguiente;
        }
        cout << endl;
    }
}

// ==================== IMPLEMENTACIÓN LISTA TABÚ ====================

ListaTabu::ListaTabu(int cap_max) : inicio(nullptr), tamano(0), capacidad_maxima(cap_max) {}

ListaTabu::~ListaTabu() {
    while (inicio != nullptr) {
        NodoTabu* temp = inicio;
        inicio = inicio->siguiente;
        delete temp;
    }
}

void ListaTabu::agregar(Movimiento mov) {
    NodoTabu* nuevo = new NodoTabu(mov);
    nuevo->siguiente = inicio;
    inicio = nuevo;
    tamano++;
    
    // Si excedemos capacidad, eliminamos el último (FIFO)
    if (tamano > capacidad_maxima) {
        if (inicio == nullptr || inicio->siguiente == nullptr) return;
        
        NodoTabu* actual = inicio;
        while (actual->siguiente->siguiente != nullptr) {
            actual = actual->siguiente;
        }
        delete actual->siguiente;
        actual->siguiente = nullptr;
        tamano--;
    }
}

bool ListaTabu::es_tabu(int evento_id, Slot slot_dest, int iteracion_actual) {
    NodoTabu* actual = inicio;
    while (actual != nullptr) {
        if (actual->movimiento.evento_id == evento_id &&
            actual->movimiento.slot_destino.get_id() == slot_dest.get_id() &&
            actual->movimiento.iteracion_tabu >= iteracion_actual) {
            return true;
        }
        actual = actual->siguiente;
    }
    return false;
}

void ListaTabu::limpiar_expirados(int iteracion_actual) {
    // Eliminar movimientos cuyo tenor tabú haya expirado
    while (inicio != nullptr && inicio->movimiento.iteracion_tabu < iteracion_actual) {
        NodoTabu* temp = inicio;
        inicio = inicio->siguiente;
        delete temp;
        tamano--;
    }
    
    if (inicio == nullptr) return;
    
    NodoTabu* actual = inicio;
    while (actual->siguiente != nullptr) {
        if (actual->siguiente->movimiento.iteracion_tabu < iteracion_actual) {
            NodoTabu* temp = actual->siguiente;
            actual->siguiente = actual->siguiente->siguiente;
            delete temp;
            tamano--;
        } else {
            actual = actual->siguiente;
        }
    }
}

void ListaTabu::mostrar() {
    cout << "\n=== LISTA TABÚ (Tamaño: " << tamano << ") ===" << endl;
    NodoTabu* actual = inicio;
    int pos = 0;
    while (actual != nullptr) {
        cout << "[" << pos++ << "] Evento " << actual->movimiento.evento_id 
             << " - Slot " << actual->movimiento.slot_destino.get_id()
             << " (Expira iter: " << actual->movimiento.iteracion_tabu << ")" << endl;
        actual = actual->siguiente;
    }
}

