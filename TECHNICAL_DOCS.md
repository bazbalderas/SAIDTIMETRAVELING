# Documentación Técnica - Graph Coloring para Horarios

## Modelado del Problema

### Definición Formal

El problema de generación de horarios universitarios se modela como un **Graph Coloring Problem**:

- **Grafo G = (V, E)** donde:
  - **V** = Conjunto de eventos (clases a programar)
  - **E** = Conjunto de aristas (conflictos entre eventos)
  
- **Colores** = Timeslots (bloques horarios disponibles)

- **Objetivo**: Asignar colores a vértices tal que:
  1. Vértices adyacentes tengan colores diferentes (hard constraint)
  2. Minimizar número de colores usados
  3. Minimizar penalizaciones por huecos (soft constraint)

### Restricciones

#### Hard Constraints (Obligatorias)

1. **No empalme de profesor**: Un profesor no puede dar dos clases simultáneamente
   ```
   Si eventos e1 y e2 tienen el mismo profesor:
   → Existe arista (e1, e2)
   → color(e1) ≠ color(e2)
   ```

2. **No empalme de grupo**: Un grupo no puede estar en dos lugares a la vez
   ```
   Si eventos e1 y e2 tienen el mismo grupo:
   → Existe arista (e1, e2)
   → color(e1) ≠ color(e2)
   ```

#### Soft Constraints (Preferencias)

1. **Continuidad**: Minimizar huecos entre clases del mismo grupo
   ```
   Penalización = Σ gaps × Peso_Continuidad
   donde gap = número de slots vacíos entre clases consecutivas
   ```

2. **Disponibilidad semafórica** (futuro):
   - Verde = Disponible
   - Rojo = Ocupado
   - Blanco = No disponible

## Algoritmos Implementados

### 1. DSatur (Degree of Saturation)

Algoritmo greedy que prioriza nodos con mayor saturación.

#### Pseudocódigo

```
DSatur(G):
    colores ← [-1, -1, ..., -1]  // n elementos
    
    while existe nodo sin colorear:
        // Seleccionar nodo con mayor saturación
        v ← nodo sin colorear con max saturación
        
        // En empate, usar grado máximo
        if empate:
            v ← nodo con max grado(v)
        
        // Asignar menor color válido
        c ← 0
        while c está usado por algún vecino de v:
            c ← c + 1
        
        colores[v] ← c
    
    return colores
```

#### Saturación

```
saturación(v) = |{colores(u) : u ∈ Vecinos(v) y colores(u) ≠ -1}|
```

Es decir, el número de **colores diferentes** usados por los vecinos de v.

#### Complejidad

- **Tiempo**: O(n² log n) en promedio
- **Espacio**: O(n + m) donde m = |E|

#### Ventajas

- Genera soluciones con pocos colores (cercano al óptimo)
- Funciona bien en grafos densos
- Determinista

#### Desventajas

- Más lento que Welsh-Powell
- No garantiza número cromático mínimo

### 2. Welsh-Powell

Algoritmo greedy que ordena nodos por grado descendente.

#### Pseudocódigo

```
Welsh-Powell(G):
    // Ordenar nodos por grado (mayor a menor)
    nodos ← sort_by_degree(V, descending=True)
    
    colores ← [-1, -1, ..., -1]
    
    for v in nodos:
        // Asignar menor color válido
        c ← 0
        while c está usado por algún vecino de v:
            c ← c + 1
        
        colores[v] ← c
    
    return colores
```

#### Complejidad

- **Tiempo**: O(n² + m)
  - Ordenamiento: O(n log n)
  - Coloreado: O(n × grado_max) ≈ O(nm)
- **Espacio**: O(n + m)

#### Ventajas

- Muy rápido en grafos grandes
- Simple de implementar
- Resultados consistentes

#### Desventajas

- Puede usar más colores que DSatur
- No considera saturación dinámica

## Construcción del Grafo

### Algoritmo de Detección de Conflictos

```cpp
void construir_grafo_conflictos() {
    for (int i = 0; i < num_eventos; i++) {
        for (int j = i + 1; j < num_eventos; j++) {
            if (hay_conflicto(eventos[i], eventos[j])) {
                grafo->agregar_arista(i, j);
                
                // Registrar tipo de conflicto
                if (eventos[i].profesor == eventos[j].profesor) {
                    conflictos.push_back({"Mismo profesor", i, j});
                } else {
                    conflictos.push_back({"Mismo grupo", i, j});
                }
            }
        }
    }
}
```

### Complejidad de Construcción

- **Tiempo**: O(n²) donde n = número de eventos
- **Espacio**: O(n + m) donde m = número de conflictos

## Mapeo de Colores a Timeslots

### Estructura de Timeslots

```
Días: L, M, Mi, J, V (5 días)
Horas: 07:00 - 19:50 (14 slots de 55 min)

Total timeslots = 5 × 14 = 70
```

### Conversión

```cpp
int slot_id = dia × 14 + hora

// Ejemplo:
Lunes 07:00    → slot_id = 0 × 14 + 0  = 0
Lunes 07:55    → slot_id = 0 × 14 + 1  = 1
Martes 09:45   → slot_id = 1 × 14 + 3  = 17
Viernes 19:50  → slot_id = 4 × 14 + 13 = 69
```

### Recuperación

```cpp
string dia = dias[slot_id / 14];
int hora_idx = slot_id % 14;
string hora = horas_inicio[hora_idx];
```

## Cálculo de Penalizaciones

### Huecos (Gaps)

Para cada grupo, calculamos huecos entre clases consecutivas:

```cpp
int calcular_penalizacion_huecos(vector<int>& colores) {
    map<string, vector<int>> horarios_grupo;
    
    // Agrupar timeslots por grupo
    for (int i = 0; i < eventos.size(); i++) {
        if (colores[i] != -1) {
            horarios_grupo[eventos[i].grupo].push_back(colores[i]);
        }
    }
    
    int penalizacion = 0;
    
    // Para cada grupo
    for (auto& [grupo, slots] : horarios_grupo) {
        sort(slots.begin(), slots.end());
        
        // Contar huecos
        for (int i = 1; i < slots.size(); i++) {
            int gap = slots[i] - slots[i-1] - 1;
            if (gap > 0) {
                penalizacion += gap × Peso_Continuidad;
            }
        }
    }
    
    return penalizacion;
}
```

**Ejemplo**:
```
Grupo ITI 5-1:
- Clase 1: slot 0  (L 07:00)
- Clase 2: slot 1  (L 07:55)
- Clase 3: slot 5  (L 11:35)

Gaps:
- Entre 1 y 2: 1 - 0 - 1 = 0 (sin hueco)
- Entre 2 y 3: 5 - 1 - 1 = 3 (3 slots de hueco)

Penalización = 3 × 10 = 30
```

### Calidad de Solución

```cpp
double calidad = 100.0 - (penalizacion_huecos × 0.1);
if (calidad < 0) calidad = 0;
```

**Interpretación**:
- **100%**: Sin huecos entre clases
- **90-99%**: Algunos huecos menores
- **80-89%**: Huecos moderados
- **< 80%**: Huecos significativos

## Optimización con Cython

### Declaraciones de Tipos

```cython
cdef class PyScheduler:
    cdef Scheduler* scheduler  # Puntero a objeto C++
    
    def ejecutar(self):
        return self.scheduler.ejecutar()
```

### Conversión de Datos

```cython
# Python → C++
cdef string mat = materia.encode('utf-8')

# C++ → Python
return asignaciones[i].dia.decode('utf-8')
```

### Speedup Esperado

| Operación | Python Puro | Cython/C++ | Speedup |
|-----------|-------------|------------|---------|
| Construcción grafo | 10 ms | 0.1 ms | 100x |
| DSatur (50 nodos) | 5 ms | 0.05 ms | 100x |
| Welsh-Powell | 2 ms | 0.02 ms | 100x |
| Total pipeline | 50 ms | 0.5 ms | 100x |

## Métricas de Rendimiento

### Densidad del Grafo

```
densidad = 2m / (n(n-1))

donde:
- n = número de nodos
- m = número de aristas
```

**Interpretación**:
- **0-20%**: Grafo disperso → Welsh-Powell mejor
- **20-60%**: Grafo medio → Ambos similares
- **60-100%**: Grafo denso → DSatur mejor

### Número Cromático

El **número cromático χ(G)** es el mínimo número de colores necesarios.

**Cotas**:
```
max_clique(G) ≤ χ(G) ≤ Δ(G) + 1

donde:
- max_clique(G) = tamaño de la mayor clique
- Δ(G) = grado máximo del grafo
```

**Nuestros algoritmos**:
- DSatur: χ_DSatur ≤ Δ(G) + 1
- Welsh-Powell: χ_WP ≤ 2 × χ(G) (en el peor caso)

## Referencias

### Papers Fundamentales

1. **Brélaz, D. (1979)**
   "New methods to color the vertices of a graph"
   *Communications of the ACM*, 22(4), 251-256.
   → Introduce DSatur

2. **Welsh, D.J.A. & Powell, M.B. (1967)**
   "An upper bound for the chromatic number of a graph and its application to timetabling problems"
   *The Computer Journal*, 10(1), 85-86.
   → Introduce Welsh-Powell

3. **Schaerf, A. (1999)**
   "A Survey of Automated Timetabling"
   *Artificial Intelligence Review*, 13, 87-127.
   → Survey completo de timetabling

### Libros

- **Diestel, R.** (2017). *Graph Theory* (5th ed.). Springer.
- **West, D.B.** (2001). *Introduction to Graph Theory* (2nd ed.). Prentice Hall.

## Extensiones Futuras

### Posibles Mejoras

1. **Backtracking**: Intentar diferentes asignaciones si falla
2. **Tabu Search**: Optimización local post-coloreado
3. **Simulated Annealing**: Escapar de óptimos locales
4. **Algoritmos exactos**: Branch & Bound para garantizar optimalidad
5. **Heurísticas híbridas**: DSatur + optimización local

### Restricciones Adicionales

1. **Aulas**: Asignar aulas específicas considerando capacidad
2. **Turnos**: Matutino vs Vespertino estricto
3. **Días preferidos**: Profesores prefieren ciertos días
4. **Bloques consecutivos**: Materias de laboratorio necesitan 2+ horas seguidas
5. **Distribución**: Evitar todos los exámenes en el mismo día

---

**Universidad Politécnica de Victoria - 2025**
