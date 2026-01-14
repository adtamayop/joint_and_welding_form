# -*- coding: utf-8 -*-
"""
Módulo específico para generación de reportes de Líquidos Penetrantes
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from .generador_pdf import GeneradorPDF

class ReporteLiquidosPenetrantes:
    """Clase específica para generar reportes de Líquidos Penetrantes"""
    
    def __init__(self):
        self.generador = GeneradorPDF()
    
    def extraer_datos_proyecto(self) -> Dict[str, Any]:
        """Extrae datos del proyecto"""
        from utils import generar_numero_informe
        
        if 'datos_proyecto' in st.session_state:
            dp = st.session_state['datos_proyecto']
            # Generar número de informe para líquidos penetrantes (offset 1)
            numero_orden = dp.get('numero_orden', '1234')
            consecutivo_inicial = dp.get('consecutivo_inicial', '100')
            fecha_obj = dp.get('fecha_obj', datetime.now())
            year = fecha_obj.year if hasattr(fecha_obj, 'year') else datetime.now().year
            numero_informe = generar_numero_informe(numero_orden, consecutivo_inicial, year, 1)
            
            dp_copy = dp.copy()
            dp_copy['numero_informe'] = numero_informe
            # Asegurar que 'ubicacion' esté presente (puede estar como 'ubicacion' o necesitar formateo)
            if 'ubicacion' not in dp_copy or not dp_copy.get('ubicacion') or dp_copy.get('ubicacion') == 'Lugar':
                # Intentar obtener de 'lugar' si existe
                if 'lugar' in dp_copy and dp_copy.get('lugar') and dp_copy.get('lugar') != 'Lugar':
                    dp_copy['ubicacion'] = dp_copy['lugar']
            return dp_copy
            
        elif 'bloque_1' in st.session_state:
            bloque_1 = st.session_state['bloque_1']
            numero_orden = bloque_1.get('numero_orden', '1234')
            consecutivo_inicial = bloque_1.get('consecutivo_inicial', '100')
            fecha = bloque_1.get('fecha', datetime.now())
            year = fecha.year if hasattr(fecha, 'year') else datetime.now().year
            numero_informe = generar_numero_informe(numero_orden, consecutivo_inicial, year, 1)
            
            return {
                'numero_informe': numero_informe,
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
                'numero_informe': 'T1234I1015',
                'fecha': datetime.now().strftime('%d/%m/%Y'),
                'cliente': 'Cliente',
                'proyecto': 'Proyecto',
                'ubicacion': 'Lugar',
                'inspector': 'Ing. Andrés López',
                'contratista': 'Contratista',
                'subproyecto': 'Subproyecto'
            }
    
    def extraer_datos_liquidos_penetrantes(self) -> Dict[str, Any]:
        """Extrae datos específicos de líquidos penetrantes"""
        if 'bloque_3_1' in st.session_state:
            bloque_3_1 = st.session_state['bloque_3_1']
            
            return {
                'norma': bloque_3_1.get('norma', 'AWS D1.1 2020'),
                'especificacion': bloque_3_1.get('especificacion', 'Material Base'),
                'proceso': bloque_3_1.get('proceso', 'Proceso de Soldadura'),
                'equipos': bloque_3_1.get('equipos', 'Kit de Líquidos Penetrantes'),
                'materiales': bloque_3_1.get('materiales', []),
                'estandares_astm': bloque_3_1.get('estandares_astm', [
                    'ASTM E 165: Standard Test Method for Liquid Penetrant Examination',
                    'ASTM E 1417: Standard Practice for Liquid Penetrant Examination'
                ]),
                'tipo': bloque_3_1.get('tipo', 'II - Líquidos Penetrantes Visibles'),
                'metodo': bloque_3_1.get('metodo', 'C - Removible con Solvente'),
                'procedimiento': bloque_3_1.get('procedimiento', 'TLPR0026 - Inspección de Líquidos Penetrantes - Rev. 1'),
                'pasos_procedimiento': bloque_3_1.get('pasos_procedimiento', ''),
                'parametros': bloque_3_1.get('parametros', []),
                'elementos': self._procesar_elementos_inspeccionados(
                    bloque_3_1.get('elementos_inspeccionados', [])
                ),
                'esquema_elementos': bloque_3_1.get('esquema_elementos', ''),
                'detalle_resultados': bloque_3_1.get('detalle_resultados', ''),
                'observaciones_generales': bloque_3_1.get('observaciones_generales', ''),
                'registros_fotograficos': bloque_3_1.get('registros_fotograficos', [])
            }
        else:
            return {
                'norma': 'AWS D1.1 2020',
                'especificacion': 'Material Base',
                'proceso': 'Proceso de Soldadura',
                'equipos': 'Kit de Líquidos Penetrantes',
                'materiales': [],
                'estandares_astm': [
                    'ASTM E 165: Standard Test Method for Liquid Penetrant Examination',
                    'ASTM E 1417: Standard Practice for Liquid Penetrant Examination'
                ],
                'tipo': 'II-Líquidos Penetrantes',
                'metodo': 'C - Removible con Solvente',
                'procedimiento': 'TLPR0026 - Inspección de Líquidos Penetrantes - Rev. 1',
                'pasos_procedimiento': '',
                'parametros': [],
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
                'numero': elemento.get('numero', ''),
                'descripcion': elemento.get('descripcion', ''),
                'indicacion': elemento.get('indicacion', ''),
                'calificacion': elemento.get('calificacion', 'Satisfactorio'),
                'observacion': elemento.get('observacion', '')
            })
        return elementos_procesados
    
    def generar_reporte(self, output_filename: str) -> str:
        """Genera el reporte de líquidos penetrantes"""
        datos_proyecto = self.extraer_datos_proyecto()
        datos_inspeccion = self.extraer_datos_liquidos_penetrantes()
        
        return self.generador.generar_liquidos_penetrantes(
            datos_proyecto, 
            datos_inspeccion, 
            output_filename
        )
    
    def verificar_datos_disponibles(self) -> bool:
        """Verifica si hay datos disponibles para generar el reporte"""
        return 'bloque_3_1' in st.session_state 