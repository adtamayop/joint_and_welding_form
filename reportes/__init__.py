# -*- coding: utf-8 -*-
"""
Módulo interno dedicado a la generación de reportes PDF
"""

from .generador_pdf import GeneradorPDF
from .reporte_inspeccion_visual import ReporteInspeccionVisual
from .reporte_liquidos_penetrantes import ReporteLiquidosPenetrantes
from .reporte_particulas_magneticas import ReporteParticulasMagneticas
from .reporte_ultrasonido import ReporteUltrasonido

__all__ = [
    'GeneradorPDF',
    'ReporteInspeccionVisual',
    'ReporteLiquidosPenetrantes',
    'ReporteParticulasMagneticas',
    'ReporteUltrasonido'
] 