# -*- coding: utf-8 -*-
"""
Módulo específico para generación de reportes de Inspección Visual
Completamente autónomo - solo usa datos del módulo 2
Estética basada en build_report.py
"""

import os
from typing import Dict, List, Any

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image, Flowable, KeepInFrame
)

# ---------------- Numeración real: "Página X de Y" (sin duplicar) -------------------------
class NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()  # evita duplicación

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(total)
            rl_canvas.Canvas.showPage(self)  # ahora sí, emite la página
        rl_canvas.Canvas.save(self)

    def _draw_page_number(self, total):
        self.setFont("Helvetica", 9)
        self.drawRightString(200*mm, 10*mm, f"Página {self._pageNumber} de {total}")

# ---------------- Caja placeholder para fotos ------------------------------
class Box(Flowable):
    def __init__(self, width, height, label=""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.label = label

    def draw(self):
        c = self.canv
        c.saveState()
        c.rect(0, 0, self.width, self.height)
        if self.label:
            c.setFont("Helvetica", 8)
            c.drawCentredString(self.width/2, self.height/2 - 4, self.label)
        c.restoreState()

class ReporteInspeccionVisual:
    """Clase específica para generar reportes de Inspección Visual - Autónoma"""
    
    def __init__(self):
        self.data = {}
        self.output_path = ""
    
    def extraer_datos_proyecto(self) -> Dict[str, Any]:
        """Extrae datos del proyecto desde el módulo 1"""
        if 'datos_proyecto' in st.session_state:
            return st.session_state['datos_proyecto']
        elif 'bloque_1' in st.session_state:
            b1 = st.session_state['bloque_1']
            return {
                'numero_informe': b1.get('reporte_no', 'T1234I1005'),
                'fecha': b1.get('fecha', '5-jun-24'),
                'cliente': b1.get('cliente', 'Cliente'),
                'proyecto': b1.get('proyecto', 'Proyecto'),
                'ubicacion': b1.get('lugar', 'Lugar'),
                'inspector': b1.get('elaboro', 'Ing. Andrés López'),
                'contratista': b1.get('contratista', 'Contratista'),
                'subproyecto': b1.get('subproyecto', 'Subproyecto')
            }
        else:
            return {
                'numero_informe': 'T1234I1005',
                'fecha': '5-jun-24',
                'cliente': 'Cliente',
                'proyecto': 'Proyecto',
                'ubicacion': 'Lugar',
                'inspector': 'Ing. Andrés López',
                'contratista': 'Contratista',
                'subproyecto': 'Subproyecto'
            }
    
    def extraer_datos_inspeccion_visual(self) -> Dict[str, Any]:
        """Extrae datos específicos de inspección visual SOLO del módulo 2"""
        self._limpiar_datos_duplicados()
        if 'bloque_2_1' in st.session_state:
            return self._procesar_datos_modulo_2(st.session_state['bloque_2_1'])
        elif 'datos_inspeccion_visual' in st.session_state:
            return self._procesar_datos_modulo_2(st.session_state['datos_inspeccion_visual'])
        else:
            return self._datos_por_defecto()
    
    def _limpiar_datos_duplicados(self):
        if 'datos_inspeccion_visual' in st.session_state and 'bloque_2_1' not in st.session_state:
            st.session_state['bloque_2_1'] = st.session_state['datos_inspeccion_visual']
            del st.session_state['datos_inspeccion_visual']
        if 'datos_inspeccion_visual' in st.session_state and 'bloque_2_1' in st.session_state:
            del st.session_state['datos_inspeccion_visual']
    
    def _procesar_datos_modulo_2(self, d: Dict[str, Any]) -> Dict[str, Any]:
        # Equipos
        eq = ""
        if 'equipos_utilizados' in d:
            kit = d['equipos_utilizados']
            if isinstance(kit, dict):
                k = kit.get('kit_seleccionado', '')
                comp = kit.get('componentes', [])
                eq = (k + (" - " + ", ".join(comp) if comp else "")) if k else ""
            else:
                eq = str(kit)
        else:
            eq = d.get('equipos', 'No especificado')
        # Materiales
        mb = d.get('materiales_base', [])
        mb_txt = ', '.join(mb) if isinstance(mb, list) and mb else (str(mb) if mb else 'No especificado')
        # Procesos
        ps = d.get('procesos_soldadura', [])
        ps_txt = ', '.join(ps) if isinstance(ps, list) and ps else (str(ps) if ps else 'No especificado')
        ts = d.get('tipos_soldadura', [])
        ts_txt = ', '.join(ts) if isinstance(ts, list) and ts else (str(ts) if ts else 'No especificado')

        fases = d.get('fases_inspeccion', [])
        fases_ok = self._procesar_fases_inspeccion(fases) if fases else {}
        elems = d.get('elementos_inspeccionados', [])
        elems_ok = self._proc_elems(elems) if elems else []
        fotos = d.get('registros_fotograficos', [])

        return {
            'norma': d.get('norma', 'No especificado'),
            'procedimiento': d.get('procedimiento', 'No especificado'),
            'equipos': eq,
            'material_base': mb_txt,
            'proceso_soldadura': ps_txt,
            'tipo_soldadura': ts_txt,
            'fases_inspeccion': fases_ok,
            'elementos_inspeccionados': elems_ok,
            'detalle_resultados': d.get('detalle_resultados', ''),
            'observaciones_generales': d.get('observaciones_generales', ''),
            'registros_fotograficos': fotos
        }
    
    def _procesar_fases_inspeccion(self, fases: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        out = {'antes_soldadura': [], 'inicio_junta': [], 'despues_soldadura': []}
        for f in fases:
            nombre = (f.get('fase', '') or '').upper()
            item = {
                'item': f.get('item', ''),
                'aplica': f.get('aplica', 'Aplica'),
                'resultado': f.get('resultado', 'Satisfactorio'),
                'observacion': f.get('observacion', '')
            }
            if 'ANTES DE INICIAR' in nombre:
                out['antes_soldadura'].append(item)
            elif 'INICIO' in nombre:
                out['inicio_junta'].append(item)
            elif 'DESPUÉS' in nombre or 'DESPUES' in nombre:
                out['despues_soldadura'].append(item)
        return out
    
    def _proc_elems(self, elems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{
            'numero': e.get('numero', ''),
            'descripcion': e.get('descripcion', ''),
            'indicacion': e.get('indicacion', ''),
            'calificacion': e.get('calificacion', 'Satisfactorio'),
            'observacion': e.get('observacion', '')
        } for e in elems]
    
    def _datos_por_defecto(self) -> Dict[str, Any]:
        return {
            'norma': 'No especificado',
            'procedimiento': 'No especificado',
            'equipos': 'No especificado',
            'material_base': 'No especificado',
            'proceso_soldadura': 'No especificado',
            'tipo_soldadura': 'No especificado',
            'fases_inspeccion': {'antes_soldadura': [], 'inicio_junta': [], 'despues_soldadura': []},
            'elementos_inspeccionados': [],
            'detalle_resultados': '',
            'observaciones_generales': '',
            'registros_fotograficos': []
        }
    
    def generar_reporte(self, output_filename: str) -> str:
        dp = self.extraer_datos_proyecto()
        di = self.extraer_datos_inspeccion_visual()
        self.data = self._formatear(dp, di)
        self.output_path = os.path.join(os.getcwd(), output_filename)
        self._generar_pdf(self.output_path)
        return self.output_path
    
    def _formatear(self, dp: Dict[str, Any], di: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'encabezado': {
                'norma': di.get('norma', 'AWS D1.1 2020'),
                'cliente': dp.get('cliente', ''),
                'proyecto': dp.get('proyecto', ''),
                'subproyecto': dp.get('subproyecto', ''),
                'contratista': dp.get('contratista', ''),
                'elaboro': dp.get('inspector', ''),
                'rep': dp.get('numero_informe', ''),
                'fecha': dp.get('fecha', ''),
                'lugar': dp.get('ubicacion', ''),
                'proceso_soldadura': di.get('proceso_soldadura', ''),
                'tipo_proceso': di.get('tipo_soldadura', '')
            },
            'procedimiento': di.get('procedimiento', 'TLPR0025 - Inspección Visual - Rev. 1'),
            'seccion_1_normas': {'criterio': di.get('norma', 'AWS D1.1 2020')},
            'seccion_2_equipos': [di.get('equipos', 'No especificado')],
            'seccion_3_material_base': di.get('material_base', 'No especificado'),
            'fases_inspeccion': di.get('fases_inspeccion', {}),
            'elementos_inspeccionados': di.get('elementos_inspeccionados', []),
            'detalle_resultados': di.get('detalle_resultados', ''),
            'observaciones_generales': di.get('observaciones_generales', ''),
            'registros_fotograficos': di.get('registros_fotograficos', [])
        }
    
    def _generar_pdf(self, out_path: str):
        data = self.data
        enc = data["encabezado"]
        doc = BaseDocTemplate(
            out_path, pagesize=letter,
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=18*mm, bottomMargin=45*mm
        )
        # Área de contenido (respeta encabezado)
        header_bottom_y = 220*mm
        padding = 6*mm
        content_top_y = header_bottom_y - padding
        content_height = content_top_y - doc.bottomMargin
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, content_height, id="main")

        template = PageTemplate(
            id="tpl_main",
            frames=[frame],
            onPage=lambda c, d: self._draw_header(c, d, enc),   # SIEMPRE pinta el bloque
            onPageEnd=lambda c, d: self._draw_footer(c, d, enc),
        )
        doc.addPageTemplates([template])

        story = self._build_story(data, doc.width)
        doc.build(story, canvasmaker=NumberedCanvas)
    
    def _draw_header(self, canv, doc, enc):
        """Encabezado con bloque de cliente en TODAS las páginas."""
        canv.saveState()

        # Títulos
        canv.setFont("Helvetica-Bold", 13)
        canv.drawCentredString(105*mm, 272*mm, "INFORME INSPECCIÓN VISUAL")
        canv.setFont("Helvetica-Bold", 11)
        canv.drawCentredString(105*mm, 265*mm, enc.get("norma", "AWS D1.1 2020"))

        # Bloque de metadatos (todas las páginas)
        x0, y0, w, h = doc.leftMargin, 220*mm, doc.width, 38*mm
        canv.setLineWidth(1)
        canv.rect(x0, y0, w, h)

        left = [
            ["Cliente:", enc.get("cliente","")],
            ["Proyecto:", enc.get("proyecto","")],
            ["Subproyecto:", enc.get("subproyecto","")],
            ["Contratista:", enc.get("contratista","")],
            ["Elaboró:", enc.get("elaboro","")],
        ]
        right = [
            ["Rep N°:", enc.get("rep","")],
            ["Fecha:", enc.get("fecha","")],
            ["Lugar:", enc.get("lugar","")],
            ["Proceso de soldadura:", enc.get("proceso_soldadura","")],
            ["Tipo:", enc.get("tipo_proceso","")],
        ]

        def draw_meta(tbl, x, y):
            col_widths = [38*mm, 46*mm]
            t = Table(tbl, colWidths=col_widths, rowHeights=7*mm)
            t.setStyle(TableStyle([
                ("FONT", (0,0), (-1,-1), "Helvetica", 9),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LINEBELOW", (1,0), (1,-1), 0.6, colors.black),
                ("RIGHTPADDING", (1,0), (1,-1), 2),
                ("LEFTPADDING", (1,0), (1,-1), 2),
            ]))
            _, h_ = t.wrapOn(canv, 0, 0)
            t.drawOn(canv, x, y - h_)

        inner = 3*mm
        tbl_w = (38+46)*mm
        left_x  = x0 + inner
        right_x = x0 + w - inner - tbl_w
        top_y = y0 + h - 3*mm

        draw_meta(left,  left_x,  top_y)
        draw_meta(right, right_x, top_y)

        # Texto vertical
        canv.setFont("Helvetica", 7)
        canv.saveState()
        canv.translate(10*mm, 140*mm)
        canv.rotate(90)
        canv.drawString(0, 0, "© Joint and Welding Ingenieros S.A.S. 2024 - Versión 6.0")
        canv.restoreState()
        canv.restoreState()

    def _draw_footer(self, canv, doc, enc):
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle

        x0, w = doc.leftMargin, doc.width
        st_small   = ParagraphStyle("small",   fontName="Helvetica", fontSize=7, leading=8)
        st_small_b = ParagraphStyle("small_b", parent=st_small, fontName="Helvetica-Bold", alignment=1)
        st_small_r = ParagraphStyle("small_r", parent=st_small, alignment=2)

        abrev_txt = ("Abreviaciones:  A: Aplica   N.A: No aplica   S: Satisfactorio   "
                     "N.S: No Satisfactorio   F.A: Fuera de Alcance")

        data = [[
            Paragraph(abrev_txt, st_small),
            Paragraph("Joint and Welding Ingenieros S.A.S.", st_small_b),
            Paragraph("Cliente", st_small_r),
        ]]

        col_left  = w - (55*mm + 25*mm)
        col_mid   = 55*mm
        col_right = 25*mm
        t = Table(data, colWidths=[col_left, col_mid, col_right])
        t.setStyle(TableStyle([
            ("BOX", (0,0), (-1,-1), 0.8, colors.black),
            ("INNERGRID", (0,0), (-1,-1), 0.8, colors.black),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("ALIGN", (1,0), (1,0), "CENTER"),
            ("ALIGN", (2,0), (2,0), "LEFT"),
        ]))
        t.wrapOn(canv, w, 0)
        t.drawOn(canv, x0, 15*mm)

    # ---------------- helpers de secciones ----------------
    def _section_box(self, title, rows, with_obs, total_w):
        cols = [total_w*0.7, total_w*0.3] if with_obs else [total_w]
        data = [[title, "OBSERVACIONES"]] if with_obs else [[title]]
        for r in rows:
            data.append([r, ""] if with_obs else [r])
        t = Table(data, colWidths=cols, rowHeights=7*mm)
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.6, colors.black),
            ("FONT", (0,0), (-1,-1), "Helvetica", 9),
            ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
            ("FONT", (0,0), (-1,0), "Helvetica-Bold", 9),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
        return t

    def _section_text_box(self, title, text, total_w):
        rows = [text] if isinstance(text, str) else text
        return self._section_box(title, rows, False, total_w)

    def _foto_cell(self, registro: Dict[str, Any], idx: int, col_w: float, styles) -> Table:
        inner_w = col_w - 8*mm
        max_img_h = 45*mm
        try:
            img = Image(registro["archivo"])
            img.hAlign = "CENTER"
            img._restrictSize(inner_w, max_img_h)
        except Exception:
            img = Box(inner_w, max_img_h, f"FOTO {idx}")
        titulo = Paragraph(f"<b>Registro Fotográfico N° {idx}</b>", styles["Body"])
        comentario = Paragraph(registro.get("comentario", ""), styles["Body"])
        col = KeepInFrame(maxWidth=inner_w, maxHeight=70*mm,
                          content=[img, Spacer(0,2*mm), titulo, comentario],
                          mode="shrink")
        cell = Table([[col]], colWidths=[col_w])
        cell.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING",(0,0), (-1,-1), 4),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ]))
        return cell

    def _build_story(self, data, total_w):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="HSection", fontName="Helvetica-Bold", fontSize=10, spaceBefore=6, spaceAfter=4))
        styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9, leading=12))

        story = []

        # 1. Procedimiento (Información General)
        procedimiento_text = f"Procedimiento: {data.get('procedimiento', 'TLPR0025 - Inspección Visual - Rev. 1')}"
        story.append(self._section_text_box("1. PROCEDIMIENTO:", procedimiento_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 2. Normas
        story.append(Spacer(0, 3*mm))
        story.append(self._section_text_box("2. NORMAS PARA EL CRITERIO DE EVALUACIÓN:", data["seccion_1_normas"]["criterio"], total_w))

        # 3. Equipos
        story.append(Spacer(0, 3*mm))
        story.append(self._section_text_box("3. EQUIPOS UTILIZADOS", ", ".join(data["seccion_2_equipos"]), total_w))

        # 4. Material base
        story.append(Spacer(0, 3*mm))
        story.append(self._section_text_box("4. MATERIAL BASE:", data["seccion_3_material_base"], total_w))

        # 5+. Fases de inspección
        fases = data.get("fases_inspeccion", {})
        seccion = 5

        if fases.get('antes_soldadura'):
            rows = [f"{x.get('item','')} - {x.get('aplica','Aplica')} - {x.get('resultado','Satisfactorio')}" for x in fases['antes_soldadura']]
            story.append(Spacer(0, 3*mm))
            story.append(self._section_box(f"{seccion}. ANTES DE INICIAR EL PROCESO DE SOLDADURA", rows, True, total_w))
            seccion += 1

        if fases.get('inicio_junta'):
            rows = [f"{x.get('item','')} - {x.get('aplica','Aplica')} - {x.get('resultado','Satisfactorio')}" for x in fases['inicio_junta']]
            story.append(Spacer(0, 3*mm))
            story.append(self._section_box(f"{seccion}. INICIO DE LA JUNTA", rows, True, total_w))
            seccion += 1

        if fases.get('despues_soldadura'):
            rows = [f"{x.get('item','')} - {x.get('aplica','Aplica')} - {x.get('resultado','Satisfactorio')}" for x in fases['despues_soldadura']]
            story.append(Spacer(0, 3*mm))
            story.append(self._section_box(f"{seccion}. DESPUÉS DE LA SOLDADURA", rows, True, total_w))
            seccion += 1

        # Elementos inspeccionados
        elems = data.get("elementos_inspeccionados", [])
        if elems:
            story.append(Spacer(0, 3*mm))
            story.append(Paragraph(f"{seccion}. ELEMENTOS INSPECCIONADOS:", styles["HSection"]))
            tabla = [["No.", "Descripción del Elemento", "Indicación", "Calificación", "Observación"]]
            for e in elems:
                tabla.append([e.get('numero',''), e.get('descripcion',''), e.get('indicacion',''),
                              e.get('calificacion','Satisfactorio'), e.get('observacion','')])
            t = Table(tabla, colWidths=[15*mm, 60*mm, 40*mm, 25*mm, 50*mm])
            t.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.6, colors.black),
                ("FONT", (0,0), (-1,-1), "Helvetica", 8),
                ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
                ("FONT", (0,0), (-1,0), "Helvetica-Bold", 8),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (-1,-1), 3),
                ("RIGHTPADDING",(0,0), (-1,-1), 3),
                ("ALIGN", (0,0), (0,-1), "CENTER"),
                ("ALIGN", (3,0), (3,-1), "CENTER"),
            ]))
            story.append(t)
            seccion += 1

        # Detalle de resultados
        detalle = data.get("detalle_resultados", "")
        if detalle and detalle.strip():
            story.append(Spacer(0, 3*mm))
            story.append(Paragraph(f"{seccion}. DETALLE DE ELEMENTOS INSPECCIONADOS Y RESULTADOS:", styles["HSection"]))
            story.append(Paragraph(detalle, styles["Body"]))
            seccion += 1

        # Observaciones generales
        obs = data.get("observaciones_generales", "")
        if obs and obs.strip():
            story.append(Spacer(0, 3*mm))
            story.append(Paragraph(f"{seccion}. OBSERVACIONES GENERALES:", styles["HSection"]))
            story.append(Paragraph(obs, styles["Body"]))
            seccion += 1

        # Registro fotográfico (cuadrícula 2xN)
        regs = data.get("registros_fotograficos", [])
        imgs = [r for r in regs if isinstance(r, dict) and r.get("archivo")]

        story.append(Spacer(0, 3*mm))
        story.append(Paragraph(f"{seccion}. REGISTRO FOTOGRÁFICO:", styles["HSection"]))

        if imgs:
            col_w = total_w / 2.0
            rows = []
            idx = 1
            for i in range(0, len(imgs), 2):
                left = self._foto_cell(imgs[i], idx, col_w, styles); idx += 1
                if i + 1 < len(imgs):
                    right = self._foto_cell(imgs[i+1], idx, col_w, styles); idx += 1
                else:
                    right = Table([[Box(col_w-8*mm, 45*mm, "")]], colWidths=[col_w])
                    right.setStyle(TableStyle([
                        ("ALIGN", (0,0), (-1,-1), "CENTER"),
                        ("VALIGN",(0,0), (-1,-1), "TOP"),
                        ("LEFTPADDING",(0,0), (-1,-1), 4),
                        ("RIGHTPADDING",(0,0), (-1,-1), 4),
                        ("TOPPADDING",(0,0), (-1,-1), 4),
                        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
                    ]))
                rows.append([left, right])

            grid = Table(rows, colWidths=[col_w, col_w])
            grid.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.8, colors.black),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
            ]))
            story.append(grid)
        else:
            story.append(Paragraph("No se registraron fotografías en este informe.", styles["Body"]))

        return story
    
    def verificar_datos_disponibles(self) -> bool:
        return 'bloque_2_1' in st.session_state
