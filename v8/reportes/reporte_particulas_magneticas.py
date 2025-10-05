# -*- coding: utf-8 -*-
"""
Módulo específico para generación de reportes de Partículas Magnéticas
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from .generador_pdf import GeneradorPDF

class ReporteParticulasMagneticas:
    """Clase específica para generar reportes de Partículas Magnéticas"""
    
    def __init__(self):
        self.generador = GeneradorPDF()
    
    def extraer_datos_proyecto(self) -> Dict[str, Any]:
        """Extrae datos del proyecto"""
        if 'datos_proyecto' in st.session_state:
            return st.session_state['datos_proyecto']
        elif 'bloque_1' in st.session_state:
            bloque_1 = st.session_state['bloque_1']
            return {
                'numero_informe': bloque_1.get('reporte_no', 'T1234I1005'),
                'fecha': bloque_1.get('fecha', datetime.now().strftime('%d/%m/%Y')),
                'cliente': bloque_1.get('cliente', 'Cliente'),
                'proyecto': bloque_1.get('proyecto', 'Proyecto'),
                'ubicacion': bloque_1.get('lugar', 'Lugar'),
                'inspector': bloque_1.get('elaboro', 'Ing. Andrés López'),
                'contratista': bloque_1.get('contratista', 'Contratista'),
                'subproyecto': bloque_1.get('subproyecto', 'Subproyecto')
            }
        else:
            return {
                'numero_informe': 'T1234I1005',
                'fecha': datetime.now().strftime('%d/%m/%Y'),
                'cliente': 'Cliente',
                'proyecto': 'Proyecto',
                'ubicacion': 'Lugar',
                'inspector': 'Ing. Andrés López',
                'contratista': 'Contratista',
                'subproyecto': 'Subproyecto'
            }
    
    def extraer_datos_particulas_magneticas(self) -> Dict[str, Any]:
        """Extrae datos específicos de partículas magnéticas"""
        if 'bloque_4_1' in st.session_state:
            bloque_4_1 = st.session_state['bloque_4_1']
            
            return {
                'norma': bloque_4_1.get('norma', 'AWS D1.1 2020'),
                'procedimiento': bloque_4_1.get('procedimiento', 'TLPR0027 - Inspección de Partículas Magnéticas - Rev. 1'),
                'equipos': bloque_4_1.get('equipos', 'Kit de Partículas Magnéticas'),
                'material_base': bloque_4_1.get('material_base', 'Material Base'),
                'proceso_soldadura': bloque_4_1.get('proceso_soldadura', 'Proceso de Soldadura'),
                'materiales_utilizados': bloque_4_1.get('materiales_utilizados', []),
                'tipo_y_metodo': bloque_4_1.get('tipo_y_metodo', []),
                'parametros_operacion': bloque_4_1.get('parametros_operacion', []),
                'proceso_y_corriente': bloque_4_1.get('proceso_y_corriente', []),
                'elementos': self._procesar_elementos_inspeccionados(
                    bloque_4_1.get('elementos_inspeccionados', [])
                ),
                'esquema_elementos': bloque_4_1.get('esquema_elementos', ''),
                'detalle_resultados': bloque_4_1.get('detalle_resultados', ''),
                'observaciones_generales': bloque_4_1.get('observaciones_generales', ''),
                'registros_fotograficos': bloque_4_1.get('registros_fotograficos', [])
            }
        else:
            return {
                'norma': 'AWS D1.1 2020',
                'procedimiento': 'TLPR0027 - Inspección de Partículas Magnéticas - Rev. 1',
                'equipos': 'Kit de Partículas Magnéticas',
                'material_base': 'Material Base',
                'proceso_soldadura': 'Proceso de Soldadura',
                'materiales_utilizados': [],
                'tipo_y_metodo': [],
                'parametros_operacion': [],
                'proceso_y_corriente': [],
                'elementos': [],
                'esquema_elementos': '',
                'detalle_resultados': '',
                'observaciones_generales': '',
                'registros_fotograficos': []
            }
    
    def _procesar_elementos_inspeccionados(self, elementos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa los elementos inspeccionados"""
        elementos_procesados = []
        for elemento in elementos:
            elementos_procesados.append({
                'elemento': elemento.get('descripcion', ''),
                'especificacion': elemento.get('especificacion', ''),
                'indicacion': elemento.get('indicacion', ''),
                'cal': elemento.get('calificacion', 'Satisfactorio'),
                'observaciones': elemento.get('observacion', '')
            })
        return elementos_procesados
    
    def generar_reporte(self, output_filename: str) -> str:
        """Genera el reporte de partículas magnéticas"""
        datos_proyecto = self.extraer_datos_proyecto()
        datos_inspeccion = self.extraer_datos_particulas_magneticas()
        
        return self.generador.generar_particulas_magneticas(
            datos_proyecto, 
            datos_inspeccion, 
            output_filename
        )
    
    def verificar_datos_disponibles(self) -> bool:
        """Verifica si hay datos disponibles para generar el reporte"""
        return 'bloque_4_1' in st.session_state 