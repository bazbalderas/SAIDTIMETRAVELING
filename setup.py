from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import os

# Extensiones Cython
extensions = [
    Extension(
        "cython_modules.busqueda_tabu",
        ["cython_modules/busqueda_tabu.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-O3', '-march=native'],  # Optimización máxima
    ),
    Extension(
        "cython_modules.graph_scheduler",
        ["cython_modules/graph_scheduler.pyx", "src/scheduler.cpp"],
        include_dirs=["include"],
        language="c++",
        extra_compile_args=['-O3', '-std=c++11'],
    )
]

setup(
    name='Sistema Horarios ITI',
    version='1.0',
    description='Sistema de generación de horarios universitarios con Graph Coloring (DSatur/Welsh-Powell) y Búsqueda Tabú',
    author='Carlos Vargas, Eliezer Mores, Mauricio Garcia, Carlos Moncada',
    ext_modules=cythonize(extensions, 
                         compiler_directives={
                             'language_level': "3",
                             'boundscheck': False,
                             'wraparound': False,
                             'cdivision': True,
                             'embedsignature': True
                         }),
    zip_safe=False,
)
