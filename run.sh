#!/bin/bash
# Launcher script for the University Timetabling System

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║     SISTEMA DE GENERACIÓN DE HORARIOS UNIVERSITARIOS - ITI UPV    ║"
echo "║                   Graph Coloring (DSatur/Welsh-Powell)             ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✓ Python 3 encontrado"

# Verificar dependencias
echo ""
echo "🔍 Verificando dependencias..."

if ! python3 -c "import numpy" 2>/dev/null; then
    echo "⚠️  NumPy no encontrado. Instalando..."
    pip3 install numpy
fi

if ! python3 -c "import cython" 2>/dev/null; then
    echo "⚠️  Cython no encontrado. Instalando..."
    pip3 install cython
fi

if ! python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
    echo "⚠️  PyQt6 no encontrado. Instalando..."
    pip3 install PyQt6
fi

echo "✓ Todas las dependencias están instaladas"

# Verificar si los módulos están compilados
echo ""
echo "🔨 Verificando compilación de módulos Cython..."

# Buscar archivos .so o .pyd de manera más robusta
if ! ls cython_modules/graph_scheduler*.so 2>/dev/null | grep -q .; then
    if ! ls cython_modules/graph_scheduler*.pyd 2>/dev/null | grep -q .; then
        echo "⚠️  Módulos no compilados. Compilando..."
        python3 setup.py build_ext --inplace
        
        if [ $? -ne 0 ]; then
            echo "❌ Error al compilar módulos"
            echo "   Revisa que tengas gcc/g++ instalado:"
            echo "   sudo apt-get install build-essential"
            exit 1
        fi
    fi
fi

echo "✓ Módulos compilados correctamente"

# Mostrar menú
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                       SELECCIONA UNA OPCIÓN                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "1) 🖥️  Interfaz Gráfica Qt6 (Recomendado)"
echo "2) 💻 Línea de Comandos (CLI)"
echo "3) 🧪 Ejecutar Tests"
echo "4) 🔧 Recompilar Módulos"
echo "5) 📖 Ver Documentación"
echo "6) ❌ Salir"
echo ""
read -p "Opción [1-6]: " opcion

case $opcion in
    1)
        echo ""
        echo "🚀 Iniciando interfaz gráfica Qt6..."
        python3 main_qt.py
        ;;
    2)
        echo ""
        echo "🚀 Ejecutando en modo CLI..."
        python3 sistema_horarios_qt.py
        ;;
    3)
        echo ""
        echo "🧪 Ejecutando tests..."
        python3 test_graph_coloring.py
        ;;
    4)
        echo ""
        echo "🔧 Recompilando módulos..."
        python3 setup.py build_ext --inplace --force
        echo "✓ Recompilación completada"
        ;;
    5)
        echo ""
        echo "📖 Abriendo documentación..."
        if command -v xdg-open &> /dev/null; then
            xdg-open README_GRAPH_COLORING.md
        elif command -v open &> /dev/null; then
            open README_GRAPH_COLORING.md
        else
            cat README_GRAPH_COLORING.md
        fi
        ;;
    6)
        echo ""
        echo "👋 Hasta luego!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                         PROCESO COMPLETADO                         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
