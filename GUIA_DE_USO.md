# Guía de Uso - Sistema de Horarios Universitarios

## 📋 Descripción General

Sistema completo de generación de horarios universitarios utilizando algoritmos de coloración de grafos (DSatur y Welsh-Powell). El sistema genera horarios sin conflictos y los exporta en múltiples formatos.

## ✅ Funcionalidades Implementadas

### 1. Generación de Horarios
- **Algoritmos**: DSatur (por defecto) y Welsh-Powell
- **Sin conflictos duros**: Garantiza que no haya profesores o grupos con clases simultáneas
- **Calidad 100%**: Optimiza la distribución de horarios
- **Visualización del grafo**: Muestra gráficamente los conflictos detectados

### 2. Exportación de Horarios

#### Excel (📊)
- Un archivo con TODOS los grupos
- Una hoja por grupo con horario semanal
- Hoja resumen con estadísticas
- Formato profesional con colores

#### HTML (🌐)
- Diseño responsive
- Tablas para todos los grupos
- Métricas del algoritmo
- Listo para compartir

#### Otros Formatos
- **JSON**: Resultados completos con métricas
- **CSV**: Matriz de adyacencia del grafo
- **PNG**: Visualización del grafo de conflictos

## 🚀 Instalación

### Requisitos
- Python 3.8 o superior
- Compilador C++ (g++)
- Sistema operativo: Linux, macOS, Windows

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/bazbalderas/SAIDTIMETRAVELING.git
cd SAIDTIMETRAVELING

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Compilar módulos Cython
python setup.py build_ext --inplace

# 4. Verificar instalación
python test_complete_validation.py
```

## 💻 Uso del Sistema

### Opción 1: Interfaz Gráfica (Qt)

```bash
python main_qt.py
```

**Flujo de trabajo:**
1. Hacer clic en **"📂 Cargar Datos"**
2. Seleccionar archivo JSON con los datos (ej: `data/datos_completos.json`)
3. Ajustar configuración si es necesario (algoritmo, peso continuidad, etc.)
4. Hacer clic en **"🚀 Generar Horarios"**
5. Explorar resultados en las pestañas:
   - **📊 Grafo**: Visualización del grafo de conflictos
   - **🔢 Matriz**: Matriz de adyacencia
   - **📅 Calendario**: Vista de horarios semanales
6. Exportar resultados:
   - **📊 Exportar Excel**: Genera archivo .xlsx con todos los grupos
   - **🌐 Exportar HTML**: Genera archivo .html responsive
   - **💾 Guardar Resultados JSON**: Exporta datos completos
   - **💾 Exportar Matriz CSV**: Exporta matriz de adyacencia

### Opción 2: Línea de Comandos

```bash
python sistema_horarios.py
```

### Opción 3: Como Módulo Python

```python
from sistema_horarios_qt import SistemaHorarios

# Crear sistema
sistema = SistemaHorarios("config.json")

# Cargar datos
sistema.cargar_datos("data/datos_completos.json")

# Generar horarios
if sistema.ejecutar_algoritmo():
    # Exportar
    sistema.exportar_excel_completo("horarios.xlsx")
    sistema.exportar_html_completo("horarios.html")
    sistema.generar_visualizacion_grafo("grafo.png")
    sistema.exportar_resultados_json("resultados.json")
```

## 📁 Formato de Datos de Entrada

El sistema requiere un archivo JSON con la siguiente estructura:

```json
{
  "profesores": [
    {
      "id": 0,
      "nombre": "Dr. Juan Pérez",
      "max_horas": 12
    }
  ],
  "grupos": [
    {
      "id": 0,
      "nombre": "ITI 1-1",
      "num_estudiantes": 30,
      "turno": "Matutino"
    }
  ],
  "materias": [
    {
      "grupo": "ITI 1-1",
      "materia": "Matemáticas",
      "horas": 6,
      "profesor": "Dr. Juan Pérez"
    }
  ]
}
```

Ver `data/datos_completos.json` para un ejemplo completo.

## ⚙️ Configuración

### Archivo `config.json`

```json
{
  "Estrategia_Coloreado": "DSatur",
  "Peso_Continuidad": 10,
  "Max_Iteraciones": 1000,
  "Dias_Habiles": ["L", "M", "Mi", "J", "V"],
  "Horario_Inicio": "07:00",
  "Horario_Fin": "19:50"
}
```

### Parámetros Configurables

- **Estrategia_Coloreado**: "DSatur" o "Welsh-Powell"
- **Peso_Continuidad**: Penalización por huecos en horarios (1-100)
- **Max_Iteraciones**: Máximo de iteraciones del algoritmo (100-10000)

## 📊 Interpretación de Resultados

### Métricas

- **Calidad de Solución**: Porcentaje de calidad (100% = perfecto)
- **Conflictos Totales**: Número de conflictos detectados en el grafo
- **Conflictos Duros**: DEBE ser 0 (profesor/grupo con clases simultáneas)
- **Timeslots Usados**: Número de franjas horarias utilizadas
- **Tiempo de Ejecución**: Milisegundos que tomó generar el horario

### Grafo de Conflictos

- **Nodos**: Cada clase/evento
- **Aristas**: Conflictos entre clases (mismo profesor o grupo)
- **Colores**: Diferentes colores = diferentes timeslots
- **Densidad**: Porcentaje de conflictos vs. total posible

## 🔧 Solución de Problemas

### Error al compilar módulos Cython

```bash
# Asegurarse de tener las herramientas de compilación
sudo apt-get install build-essential python3-dev  # Ubuntu/Debian
# o
brew install gcc  # macOS
```

### Error al importar módulos

```bash
# Verificar que los módulos se compilaron
ls cython_modules/*.so

# Si no existen, recompilar
python setup.py build_ext --inplace
```

### Conflictos duros en los horarios

Si el sistema reporta conflictos duros (>0):
1. Verificar datos de entrada (profesores duplicados, grupos duplicados)
2. Aumentar Max_Iteraciones en config.json
3. Probar con estrategia diferente (DSatur ↔ Welsh-Powell)

## 📝 Archivos Importantes

### Código Principal
- `main_qt.py` - Interfaz gráfica Qt
- `sistema_horarios_qt.py` - Lógica del sistema
- `src/scheduler.cpp` - Algoritmos de coloración en C++

### Módulos de Exportación
- `exportador_horarios.py` - Exportación Excel y HTML
- `visualizacion_grafo.py` - Visualización del grafo
- `config_horarios.py` - Configuración centralizada

### Datos
- `data/datos_completos.json` - Datos de ejemplo
- `config.json` - Configuración del sistema

## 🎯 Validación

El sistema incluye un script de validación completo:

```bash
python test_complete_validation.py
```

Verifica:
- ✅ Carga de datos
- ✅ Generación de horarios
- ✅ Ausencia de conflictos duros
- ✅ Exportación a todos los formatos
- ✅ Visualización del grafo

## 📞 Soporte

Para reportar problemas o sugerencias:
- GitHub Issues: https://github.com/bazbalderas/SAIDTIMETRAVELING/issues

## 📄 Licencia

Ver archivo LICENSE en el repositorio.

---

**Desarrollado por**: Carlos Vargas, Eliezer Mores, Mauricio Garcia, Carlos Moncada
**Universidad**: Politécnica de Victoria
