# -*- coding: utf-8 -*-
"""
Módulo específico para generación de reportes de Ultrasonido
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from .generador_pdf import GeneradorPDF

class ReporteUltrasonido:
    """Clase específica para generar reportes de Ultrasonido"""
    
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
    
    def extraer_datos_ultrasonido(self) -> Dict[str, Any]:
        """Extrae datos específicos de ultrasonido"""
        if 'bloque_5_1' in st.session_state:
            bloque_5_1 = st.session_state['bloque_5_1']
            
            return {
                'equipo': bloque_5_1.get('equipo', 'Equipo de Ultrasonido'),
                'palpador': bloque_5_1.get('palpador', 'Palpador'),
                'soldadura': bloque_5_1.get('soldadura', 'Proceso de Soldadura'),
                'material_base': bloque_5_1.get('material_base', 'Material Base'),
                'norma': bloque_5_1.get('norma', 'AWS D1.1 2020'),
                'procedimiento': bloque_5_1.get('procedimiento', 'Procedimiento de Inspección'),
                'elementos': self._procesar_elementos_inspeccionados(
                    bloque_5_1.get('elementos_inspeccionados', [])
                ),
                'juntas': bloque_5_1.get('juntas', ''),
                'detalle_resultados': bloque_5_1.get('detalle_resultados', ''),
                'esquema_inspeccion': bloque_5_1.get('esquema_inspeccion', ''),
                'observaciones_generales': bloque_5_1.get('observaciones_generales', ''),
                'registros_fotograficos': bloque_5_1.get('registros_fotograficos', [])
            }
        else:
            return {
                'equipo': 'Equipo de Ultrasonido',
                'palpador': 'Palpador',
                'soldadura': 'Proceso de Soldadura',
                'material_base': 'Material Base',
                'norma': 'AWS D1.1 2020',
                'procedimiento': 'Procedimiento de Inspección',
                'elementos': [],
                'juntas': '',
                'detalle_resultados': '',
                'esquema_inspeccion': '',
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
        """Genera el reporte de ultrasonido"""
        datos_proyecto = self.extraer_datos_proyecto()
        datos_inspeccion = self.extraer_datos_ultrasonido()
        
        return self.generador.generar_ultrasonido(
            datos_proyecto, 
            datos_inspeccion, 
            output_filename
        )
    
    def verificar_datos_disponibles(self) -> bool:
        """Verifica si hay datos disponibles para generar el reporte"""
        return 'bloque_5_1' in st.session_state 