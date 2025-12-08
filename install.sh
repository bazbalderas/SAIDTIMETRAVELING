#!/bin/bash

# Script de instalación rápida para Sistema de Horarios ITI

echo "========================================"
echo "Sistema de Horarios ITI - UPV"
echo "Script de Instalación"
echo "========================================"
echo ""

# Verificar Python
echo "[1/4] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    exit 1
fi
echo "✓ Python 3 encontrado: $(python3 --version)"
echo ""

# Verificar GCC
echo "[2/4] Verificando compilador GCC..."
if ! command -v gcc &> /dev/null; then
    echo "ERROR: GCC no está instalado"
    echo "Instala con: sudo apt-get install build-essential"
    exit 1
fi
echo "✓ GCC encontrado: $(gcc --version | head -n 1)"
echo ""

# Instalar dependencias
echo "[3/4] Instalando dependencias Python..."
pip3 install cython numpy --user
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo al instalar dependencias"
    exit 1
fi
echo "✓ Dependencias instaladas"
echo ""

# Compilar módulos Cython
echo "[4/4] Compilando módulos Cython..."
python3 setup.py build_ext --inplace
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo al compilar módulos Cython"
    exit 1
fi
echo "✓ Módulos compilados"
echo ""

# Verificar instalación
echo "Verificando instalación..."
python3 -c "from cython_modules.busqueda_tabu import BusquedaTabu; print('✓ Módulo Cython cargado correctamente')"
if [ $? -ne 0 ]; then
    echo "ERROR: El módulo Cython no se pudo cargar"
    exit 1
fi
echo ""

echo "========================================"
echo "✓ INSTALACIÓN COMPLETADA"
echo "========================================"
echo ""
echo "Para ejecutar el sistema:"
echo "  python3 sistema_horarios.py"
echo ""
echo "Para abrir la interfaz web:"
echo "  xdg-open web/index.html"
echo ""
echo "Para ver ayuda:"
echo "  make help"
echo ""
