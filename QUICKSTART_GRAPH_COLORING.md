# 🚀 QUICK START - Sistema de Horarios con Graph Coloring

## Instalación Rápida (5 minutos)

### Linux/Mac

```bash
# 1. Clonar repositorio
git clone https://github.com/bazbalderas/SAIDTIMETRAVELING.git
cd SAIDTIMETRAVELING

# 2. Instalar dependencias
pip3 install -r requirements.txt

# 3. Compilar módulos
python3 setup.py build_ext --inplace

# 4. Ejecutar
./run.sh
```

### Windows

```powershell
# 1. Clonar repositorio
git clone https://github.com/bazbalderas/SAIDTIMETRAVELING.git
cd SAIDTIMETRAVELING

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Compilar módulos
python setup.py build_ext --inplace

# 4. Ejecutar interfaz gráfica
python main_qt.py
```

## Uso Básico

### Interfaz Gráfica Qt6

1. **Cargar Datos**
   - Click en "📂 Cargar Datos"
   - Selecciona `data/datos_completos.json`

2. **Configurar Parámetros** (opcional)
   - Estrategia: DSatur o Welsh-Powell
   - Peso Continuidad: 10 (default)
   - Max Iteraciones: 1000 (default)

3. **Generar Horario**
   - Click en "🚀 Generar Horarios"
   - Espera 1-2 segundos
   - Revisa resultados en las pestañas

4. **Exportar Resultados**
   - JSON: Botón "💾 Exportar Resultados JSON"
   - CSV: Botón "💾 Exportar Matriz CSV"

### Línea de Comandos

```bash
python3 sistema_horarios_qt.py
```

Esto ejecutará el algoritmo y generará:
- `resultados.json` - Resultados completos
- `matriz_adyacencia.csv` - Matriz de conflictos

### Tests

```bash
python3 test_graph_coloring.py    # Tests de algoritmos
python3 benchmark.py                # Benchmarks de rendimiento
```

## Estructura de Datos

### Archivo JSON de Entrada

```json
{
  "profesores": [
    {"id": 0, "nombre": "Dr. Said Polanco", "max_horas": 6}
  ],
  "grupos": [
    {"id": 0, "nombre": "ITI 5-1", "num_estudiantes": 35, "turno": "Matutino"}
  ],
  "materias": [
    {
      "grupo": "ITI 5-1",
      "materia": "Estructura de Datos",
      "horas": 6,
      "profesor": "Dr. Said Polanco"
    }
  ]
}
```

## Solución de Problemas Comunes

### Error: "No module named 'cython_modules.graph_scheduler'"

```bash
python3 setup.py build_ext --inplace --force
```

### Error: "gcc: command not found"

**Linux:**
```bash
sudo apt-get install build-essential
```

**Windows:**
Instala MinGW o Visual Studio Build Tools

### Error: "libEGL.so.1: cannot open shared object"

**Linux:**
```bash
sudo apt-get install libgl1-mesa-glx libegl1-mesa
```

### La interfaz Qt6 no se ve correctamente

Asegúrate de tener instalados los paquetes Qt6:
```bash
pip3 install --upgrade PyQt6
```

## Configuración Avanzada

Edita `config.json`:

```json
{
  "Horas_Bloque": 55,              // Cambiar duración de bloques
  "Peso_Continuidad": 10,          // Aumentar para penalizar más los huecos
  "Estrategia_Coloreado": "DSatur" // O "Welsh-Powell"
}
```

## Siguiente Paso

Lee la documentación completa: [README_GRAPH_COLORING.md](README_GRAPH_COLORING.md)

---

¿Problemas? Abre un issue en GitHub o consulta con los autores.
