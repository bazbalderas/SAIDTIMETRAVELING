#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Qt6 para Sistema de Generación de Horarios
Interfaz gráfica con glassmorphism y cyberpunk styling
"""

import sys
import json
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QScrollArea,
    QTextEdit, QProgressBar, QMessageBox, QDialog, QDialogButtonBox,
    QTabWidget, QSplitter, QGroupBox, QSpinBox, QComboBox, QLineEdit,
    QFileDialog, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

from sistema_horarios_qt import SistemaHorarios


class SchedulerThread(QThread):
    """Thread para ejecutar el scheduler sin bloquear la UI"""
    progreso = pyqtSignal(int, str)
    terminado = pyqtSignal(bool, dict)
    error = pyqtSignal(str)
    
    def __init__(self, sistema):
        super().__init__()
        self.sistema = sistema
    
    def run(self):
        try:
            self.progreso.emit(10, "Generando eventos...")
            self.sistema.generar_eventos()
            
            self.progreso.emit(30, "Ejecutando algoritmo de coloreado...")
            exito = self.sistema.ejecutar_algoritmo()
            
            if exito:
                self.progreso.emit(90, "Procesando resultados...")
                resultados = self.sistema.resultados
                self.progreso.emit(100, "Completado")
                self.terminado.emit(True, resultados)
            else:
                self.error.emit("Error al ejecutar el algoritmo")
                self.terminado.emit(False, {})
        except Exception as e:
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            self.error.emit(error_msg)
            self.terminado.emit(False, {})


class ErrorDialog(QDialog):
    """Dialog para mostrar errores con stacktrace"""
    def __init__(self, error_message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Label
        label = QLabel("Ha ocurrido un error:")
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(label)
        
        # Text area con el error
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(error_message)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier", 9))
        layout.addWidget(self.text_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("Copiar al portapapeles")
        copy_button.clicked.connect(self.copiar_error)
        button_layout.addWidget(copy_button)
        
        send_button = QPushButton("Enviar log")
        send_button.clicked.connect(self.enviar_log)
        button_layout.addWidget(send_button)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Estilo
        self.setStyleSheet("""
            QDialog {
                background: rgba(20, 20, 40, 0.95);
                border: 2px solid rgba(255, 0, 255, 0.5);
                border-radius: 10px;
            }
            QLabel {
                color: #FF0080;
            }
            QTextEdit {
                background: rgba(0, 0, 0, 0.5);
                color: #00FFFF;
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(255, 0, 128, 0.8),
                                           stop:1 rgba(0, 255, 255, 0.8));
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(255, 0, 128, 1.0),
                                           stop:1 rgba(0, 255, 255, 1.0));
            }
        """)
    
    def copiar_error(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        QMessageBox.information(self, "Copiado", "Error copiado al portapapeles")
    
    def enviar_log(self):
        QMessageBox.information(self, "Enviar Log", 
                               "Funcionalidad de envío de logs no implementada.\n"
                               "Por favor, copia el error y envíalo manualmente.")


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.sistema = SistemaHorarios("config.json")
        self.scheduler_thread = None
        
        self.init_ui()
        self.aplicar_estilos()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Sistema de Horarios ITI - Graph Coloring")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Splitter para paneles redimensionables
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo: Configuración y profesores
        left_panel = self.crear_panel_izquierdo()
        splitter.addWidget(left_panel)
        
        # Panel central: Tabs (grafo, matriz, calendario)
        center_panel = self.crear_panel_central()
        splitter.addWidget(center_panel)
        
        # Panel derecho: Resultados y métricas
        right_panel = self.crear_panel_derecho()
        splitter.addWidget(right_panel)
        
        # Tamaños de los paneles
        splitter.setSizes([350, 700, 350])
        
        # Status bar
        self.statusBar().showMessage("Listo")
    
    def crear_panel_izquierdo(self):
        """Crea el panel izquierdo con configuración"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Título
        title = QLabel("⚙️ CONFIGURACIÓN")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Grupo de configuración
        config_group = QGroupBox("Parámetros del Algoritmo")
        config_layout = QVBoxLayout()
        config_group.setLayout(config_layout)
        
        # Estrategia
        estrategia_layout = QHBoxLayout()
        estrategia_layout.addWidget(QLabel("Estrategia:"))
        self.estrategia_combo = QComboBox()
        self.estrategia_combo.addItems(["DSatur", "Welsh-Powell"])
        estrategia_layout.addWidget(self.estrategia_combo)
        config_layout.addLayout(estrategia_layout)
        
        # Peso continuidad
        peso_layout = QHBoxLayout()
        peso_layout.addWidget(QLabel("Peso Continuidad:"))
        self.peso_spin = QSpinBox()
        self.peso_spin.setRange(1, 100)
        self.peso_spin.setValue(10)
        peso_layout.addWidget(self.peso_spin)
        config_layout.addLayout(peso_layout)
        
        # Max iteraciones
        iter_layout = QHBoxLayout()
        iter_layout.addWidget(QLabel("Max Iteraciones:"))
        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(100, 10000)
        self.iter_spin.setValue(1000)
        iter_layout.addWidget(self.iter_spin)
        config_layout.addLayout(iter_layout)
        
        # Botón guardar config
        save_config_btn = QPushButton("💾 Guardar Configuración")
        save_config_btn.clicked.connect(self.guardar_configuracion)
        config_layout.addWidget(save_config_btn)
        
        layout.addWidget(config_group)
        
        # Tabla de profesores con scroll
        profesores_group = QGroupBox("👨‍🏫 Profesores")
        profesores_layout = QVBoxLayout()
        profesores_group.setLayout(profesores_layout)
        
        # Crear tabla dentro de un scroll area
        self.tabla_profesores = QTableWidget()
        self.tabla_profesores.setColumnCount(2)
        self.tabla_profesores.setHorizontalHeaderLabels(["Nombre", "Horas"])
        self.tabla_profesores.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_profesores.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        profesores_layout.addWidget(self.tabla_profesores)
        
        # Botones
        btn_layout = QHBoxLayout()
        cargar_btn = QPushButton("📂 Cargar Datos")
        cargar_btn.clicked.connect(self.cargar_datos)
        btn_layout.addWidget(cargar_btn)
        
        generar_btn = QPushButton("🚀 Generar Horarios")
        generar_btn.clicked.connect(self.generar_horarios)
        generar_btn.setStyleSheet("font-weight: bold; font-size: 14px;")
        btn_layout.addWidget(generar_btn)
        
        profesores_layout.addLayout(btn_layout)
        
        layout.addWidget(profesores_group)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        return panel
    
    def crear_panel_central(self):
        """Crea el panel central con tabs"""
        tabs = QTabWidget()
        
        # Tab 1: Grafo
        grafo_widget = QWidget()
        grafo_layout = QVBoxLayout()
        grafo_widget.setLayout(grafo_layout)
        
        grafo_label = QLabel("🔗 Visualización del Grafo de Conflictos")
        grafo_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grafo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grafo_layout.addWidget(grafo_label)
        
        self.grafo_info = QTextEdit()
        self.grafo_info.setReadOnly(True)
        self.grafo_info.setPlaceholderText("El grafo se mostrará aquí después de generar horarios...")
        grafo_layout.addWidget(self.grafo_info)
        
        tabs.addTab(grafo_widget, "📊 Grafo")
        
        # Tab 2: Matriz de Adyacencia
        matriz_widget = QWidget()
        matriz_layout = QVBoxLayout()
        matriz_widget.setLayout(matriz_layout)
        
        matriz_label = QLabel("📋 Matriz de Adyacencia")
        matriz_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        matriz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        matriz_layout.addWidget(matriz_label)
        
        self.tabla_matriz = QTableWidget()
        matriz_layout.addWidget(self.tabla_matriz)
        
        export_matriz_btn = QPushButton("💾 Exportar Matriz CSV")
        export_matriz_btn.clicked.connect(self.exportar_matriz)
        matriz_layout.addWidget(export_matriz_btn)
        
        tabs.addTab(matriz_widget, "🔢 Matriz")
        
        # Tab 3: Calendario
        calendario_widget = QWidget()
        calendario_layout = QVBoxLayout()
        calendario_widget.setLayout(calendario_layout)
        
        calendario_label = QLabel("📅 Horario Semanal")
        calendario_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        calendario_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calendario_layout.addWidget(calendario_label)
        
        self.tabla_calendario = QTableWidget()
        self.tabla_calendario.setColumnCount(6)
        self.tabla_calendario.setHorizontalHeaderLabels(["Hora", "L", "M", "Mi", "J", "V"])
        calendario_layout.addWidget(self.tabla_calendario)
        
        export_btn_layout = QHBoxLayout()
        export_excel_btn = QPushButton("📊 Exportar Excel")
        export_excel_btn.clicked.connect(self.exportar_excel)
        export_btn_layout.addWidget(export_excel_btn)
        
        export_html_btn = QPushButton("🌐 Exportar HTML")
        export_html_btn.clicked.connect(self.exportar_html)
        export_btn_layout.addWidget(export_html_btn)
        
        calendario_layout.addLayout(export_btn_layout)
        
        tabs.addTab(calendario_widget, "📅 Calendario")
        
        return tabs
    
    def crear_panel_derecho(self):
        """Crea el panel derecho con métricas"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Título
        title = QLabel("📈 RESULTADOS")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Métricas
        metricas_group = QGroupBox("Métricas de Ejecución")
        metricas_layout = QVBoxLayout()
        metricas_group.setLayout(metricas_layout)
        
        self.metricas_text = QTextEdit()
        self.metricas_text.setReadOnly(True)
        self.metricas_text.setPlaceholderText("Las métricas se mostrarán aquí...")
        metricas_layout.addWidget(self.metricas_text)
        
        layout.addWidget(metricas_group)
        
        # Asignaciones
        asignaciones_group = QGroupBox("Asignaciones de Horarios")
        asignaciones_layout = QVBoxLayout()
        asignaciones_group.setLayout(asignaciones_layout)
        
        self.tabla_asignaciones = QTableWidget()
        self.tabla_asignaciones.setColumnCount(4)
        self.tabla_asignaciones.setHorizontalHeaderLabels(["Grupo", "Materia", "Día", "Hora"])
        asignaciones_layout.addWidget(self.tabla_asignaciones)
        
        layout.addWidget(asignaciones_group)
        
        # Botón exportar JSON
        export_json_btn = QPushButton("💾 Exportar Resultados JSON")
        export_json_btn.clicked.connect(self.exportar_json)
        layout.addWidget(export_json_btn)
        
        return panel
    
    def aplicar_estilos(self):
        """Aplica estilos glassmorphism y cyberpunk"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 rgba(10, 10, 30, 1),
                                           stop:1 rgba(30, 10, 50, 1));
            }
            
            QWidget {
                background: rgba(20, 20, 40, 0.7);
                color: #E0E0E0;
            }
            
            QGroupBox {
                background: rgba(40, 20, 60, 0.5);
                border: 2px solid rgba(255, 0, 255, 0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                color: #FF00FF;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(255, 0, 128, 0.7),
                                           stop:1 rgba(0, 255, 255, 0.7));
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(255, 0, 128, 1.0),
                                           stop:1 rgba(0, 255, 255, 1.0));
                box-shadow: 0 0 15px rgba(255, 0, 255, 0.8);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(200, 0, 100, 1.0),
                                           stop:1 rgba(0, 200, 200, 1.0));
            }
            
            QTableWidget {
                background: rgba(0, 0, 0, 0.3);
                color: #00FFFF;
                gridline-color: rgba(0, 255, 255, 0.2);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 5px;
            }
            
            QHeaderView::section {
                background: rgba(255, 0, 255, 0.3);
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            
            QTextEdit {
                background: rgba(0, 0, 0, 0.4);
                color: #00FFFF;
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
            }
            
            QLabel {
                color: #E0E0E0;
            }
            
            QProgressBar {
                background: rgba(0, 0, 0, 0.5);
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(255, 0, 128, 0.8),
                                           stop:1 rgba(0, 255, 255, 0.8));
                border-radius: 3px;
            }
            
            QTabWidget::pane {
                border: 2px solid rgba(255, 0, 255, 0.3);
                border-radius: 5px;
                background: rgba(20, 20, 40, 0.5);
            }
            
            QTabBar::tab {
                background: rgba(40, 20, 60, 0.5);
                color: #00FFFF;
                padding: 10px 20px;
                margin: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 rgba(255, 0, 128, 0.5),
                                           stop:1 rgba(0, 255, 255, 0.5));
                color: white;
                font-weight: bold;
            }
            
            QComboBox, QSpinBox, QLineEdit {
                background: rgba(0, 0, 0, 0.5);
                color: #00FFFF;
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
            }
            
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.3);
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(255, 0, 255, 0.5);
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 0, 255, 0.8);
            }
        """)
    
    def cargar_datos(self):
        """Carga datos desde archivo JSON"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Cargar Datos", "data/", "JSON Files (*.json)"
            )
            
            if file_name:
                self.sistema.cargar_datos(file_name)
                self.actualizar_tabla_profesores()
                self.statusBar().showMessage(f"Datos cargados desde {file_name}")
                QMessageBox.information(self, "Éxito", f"Datos cargados correctamente:\n"
                                       f"- {len(self.sistema.profesores)} profesores\n"
                                       f"- {len(self.sistema.grupos)} grupos\n"
                                       f"- {len(self.sistema.materias)} materias")
        except Exception as e:
            error_dialog = ErrorDialog(str(e) + "\n\n" + traceback.format_exc(), self)
            error_dialog.exec()
    
    def actualizar_tabla_profesores(self):
        """Actualiza la tabla de profesores"""
        self.tabla_profesores.setRowCount(len(self.sistema.profesores))
        
        for i, profesor in enumerate(self.sistema.profesores):
            nombre_item = QTableWidgetItem(profesor['nombre'])
            horas_item = QTableWidgetItem(str(profesor['max_horas']))
            
            self.tabla_profesores.setItem(i, 0, nombre_item)
            self.tabla_profesores.setItem(i, 1, horas_item)
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        self.sistema.config.set('Estrategia_Coloreado', self.estrategia_combo.currentText())
        self.sistema.config.set('Peso_Continuidad', self.peso_spin.value())
        self.sistema.config.set('Max_Iteraciones', self.iter_spin.value())
        self.sistema.config.guardar()
        
        QMessageBox.information(self, "Guardado", "Configuración guardada en config.json")
    
    def generar_horarios(self):
        """Genera horarios usando el scheduler en un thread"""
        try:
            if not self.sistema.materias:
                QMessageBox.warning(self, "Advertencia", 
                                   "Primero debes cargar los datos usando el botón 'Cargar Datos'")
                return
            
            # Actualizar configuración
            self.sistema.config.set('Estrategia_Coloreado', self.estrategia_combo.currentText())
            self.sistema.config.set('Peso_Continuidad', self.peso_spin.value())
            self.sistema.config.set('Max_Iteraciones', self.iter_spin.value())
            
            # Crear y ejecutar thread
            self.scheduler_thread = SchedulerThread(self.sistema)
            self.scheduler_thread.progreso.connect(self.actualizar_progreso)
            self.scheduler_thread.terminado.connect(self.scheduler_terminado)
            self.scheduler_thread.error.connect(self.mostrar_error)
            
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Ejecutando algoritmo...")
            self.scheduler_thread.start()
            
        except Exception as e:
            error_dialog = ErrorDialog(str(e) + "\n\n" + traceback.format_exc(), self)
            error_dialog.exec()
    
    def actualizar_progreso(self, valor, mensaje):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(valor)
        self.progress_label.setText(mensaje)
    
    def mostrar_error(self, error_msg):
        """Muestra un error en un dialog"""
        error_dialog = ErrorDialog(error_msg, self)
        error_dialog.exec()
    
    def scheduler_terminado(self, exito, resultados):
        """Callback cuando el scheduler termina"""
        if exito:
            self.statusBar().showMessage("Horario generado exitosamente!")
            self.mostrar_resultados(resultados)
            QMessageBox.information(self, "Éxito", 
                                   "Horario generado exitosamente!\n"
                                   f"Calidad: {resultados['metricas']['calidad_solucion']:.2f}%")
        else:
            self.statusBar().showMessage("Error al generar horario")
    
    def mostrar_resultados(self, resultados):
        """Muestra los resultados en la UI"""
        # Métricas
        metricas = resultados['metricas']
        metricas_text = f"""
<h3 style='color: #FF00FF;'>📈 Métricas de Ejecución</h3>
<p><b>⏱️ Tiempo:</b> {metricas['tiempo_ejecucion_ms']:.2f} ms</p>
<p><b>🔄 Iteraciones:</b> {metricas['iteraciones']}</p>
<p><b>🎨 Colores (timeslots):</b> {metricas['colores_usados']}</p>
<p><b>⚠️ Conflictos:</b> {metricas['conflictos_totales']}</p>
<p><b>📊 Penalización huecos:</b> {metricas['penalizacion_huecos']}</p>
<p><b>✨ Calidad:</b> <span style='color: #00FF00; font-size: 18px;'>{metricas['calidad_solucion']:.2f}%</span></p>
        """
        self.metricas_text.setHtml(metricas_text)
        
        # Info grafo
        info_grafo = resultados['info_grafo']
        grafo_text = f"""
<h3 style='color: #00FFFF;'>🔗 Información del Grafo</h3>
<p><b>📍 Nodos (eventos):</b> {info_grafo['nodos']}</p>
<p><b>🔗 Aristas (conflictos):</b> {info_grafo['aristas']}</p>
<p><b>📊 Grado máximo:</b> {info_grafo['grado_maximo']}</p>
<p><b>📈 Grado promedio:</b> {info_grafo['grado_promedio']:.2f}</p>

<h3 style='color: #FF00FF;'>📊 Interpretación</h3>
<p>El grafo representa los conflictos entre eventos (clases). Cada nodo es una clase,
y cada arista representa un conflicto (mismo profesor o grupo en el mismo horario).</p>

<p><b>Densidad:</b> {info_grafo['aristas'] / (info_grafo['nodos'] * (info_grafo['nodos']-1) / 2) * 100:.1f}%</p>
        """
        self.grafo_info.setHtml(grafo_text)
        
        # Matriz de adyacencia
        self.mostrar_matriz(resultados['matriz_adyacencia'])
        
        # Asignaciones
        self.mostrar_asignaciones(resultados['asignaciones'])
        
        # Calendario
        self.mostrar_calendario(resultados['asignaciones'])
    
    def mostrar_matriz(self, matriz):
        """Muestra la matriz de adyacencia"""
        n = len(matriz)
        self.tabla_matriz.setRowCount(n)
        self.tabla_matriz.setColumnCount(n)
        
        # Headers
        headers = [f"E{i}" for i in range(n)]
        self.tabla_matriz.setHorizontalHeaderLabels(headers)
        self.tabla_matriz.setVerticalHeaderLabels(headers)
        
        # Llenar matriz
        for i in range(n):
            for j in range(n):
                item = QTableWidgetItem(str(matriz[i][j]))
                if matriz[i][j] == 1:
                    item.setBackground(QColor(255, 0, 128, 100))
                self.tabla_matriz.setItem(i, j, item)
    
    def mostrar_asignaciones(self, asignaciones):
        """Muestra las asignaciones en la tabla"""
        self.tabla_asignaciones.setRowCount(len(asignaciones))
        
        for i, asig in enumerate(asignaciones):
            evento_id = asig['evento_id']
            
            # Validar que el evento_id esté en rango
            if evento_id < 0 or evento_id >= len(self.sistema.eventos):
                continue
            
            evento = self.sistema.eventos[evento_id]
            
            self.tabla_asignaciones.setItem(i, 0, QTableWidgetItem(evento['grupo']))
            self.tabla_asignaciones.setItem(i, 1, QTableWidgetItem(evento['materia']))
            self.tabla_asignaciones.setItem(i, 2, QTableWidgetItem(asig['dia']))
            self.tabla_asignaciones.setItem(i, 3, QTableWidgetItem(asig['hora']))
    
    def mostrar_calendario(self, asignaciones):
        """Muestra el calendario semanal"""
        # Por simplicidad, solo mostramos un resumen
        # En una implementación completa, se construiría una vista de calendario completa
        dias = ["L", "M", "Mi", "J", "V"]
        horas_inicio = ["07:00", "07:55", "08:50", "09:45", "10:40", "11:35", "12:30",
                       "13:25", "14:20", "15:15", "16:10", "17:05", "18:00", "18:55", "19:50"]
        
        self.tabla_calendario.setRowCount(len(horas_inicio))
        
        for i, hora in enumerate(horas_inicio):
            self.tabla_calendario.setItem(i, 0, QTableWidgetItem(hora))
            for j in range(5):
                self.tabla_calendario.setItem(i, j+1, QTableWidgetItem(""))
        
        # Llenar con asignaciones
        for asig in asignaciones:
            evento = self.sistema.eventos[asig['evento_id']]
            dia_idx = dias.index(asig['dia']) if asig['dia'] in dias else -1
            
            if dia_idx != -1 and asig['hora'] in horas_inicio:
                hora_idx = horas_inicio.index(asig['hora'])
                texto = f"{evento['grupo']}\n{evento['materia'][:15]}"
                item = QTableWidgetItem(texto)
                item.setBackground(QColor(0, 255, 255, 50))
                self.tabla_calendario.setItem(hora_idx, dia_idx + 1, item)
    
    def exportar_matriz(self):
        """Exporta la matriz de adyacencia a CSV"""
        if not self.sistema.resultados:
            QMessageBox.warning(self, "Advertencia", "Primero genera un horario")
            return
        
        self.sistema.exportar_matriz_csv()
        QMessageBox.information(self, "Exportado", "Matriz exportada a matriz_adyacencia.csv")
    
    def exportar_json(self):
        """Exporta resultados a JSON"""
        if not self.sistema.resultados:
            QMessageBox.warning(self, "Advertencia", "Primero genera un horario")
            return
        
        self.sistema.exportar_resultados_json()
        QMessageBox.information(self, "Exportado", "Resultados exportados a resultados.json")
    
    def exportar_excel(self):
        """Exporta a Excel (placeholder)"""
        QMessageBox.information(self, "Excel", 
                               "Exportación a Excel requiere librería openpyxl.\n"
                               "Por ahora usa la exportación JSON.")
    
    def exportar_html(self):
        """Exporta a HTML (placeholder)"""
        QMessageBox.information(self, "HTML", 
                               "Exportación HTML en desarrollo.\n"
                               "Por ahora usa la exportación JSON.")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette oscuro
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 40))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(15, 15, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(25, 25, 45))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(40, 20, 60))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
