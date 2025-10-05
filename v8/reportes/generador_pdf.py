# -*- coding: utf-8 -*-
"""
Generador de PDF para reportes de inspección
Contiene toda la lógica de generación de PDF usando reportlab
"""

import os
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, Flowable
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para numeración de páginas"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        super().showPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(total)
            super().showPage()
        super().save()

    def draw_page_number(self, total):
        self.setFont("Helvetica", 9)
        self.drawRightString(200*mm, 10*mm, f"Página {self._pageNumber} de {total}")

class Box(Flowable):
    """Caja placeholder para fotos"""
    
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

class GeneradorPDF:
    """Clase principal para generar PDFs de reportes de inspección"""
    
    def __init__(self):
        self.data = {}
        self.output_path = ""
    
    def generar_inspeccion_visual(self, datos_proyecto: Dict[str, Any], 
                                 datos_inspeccion: Dict[str, Any], 
                                 output_filename: str) -> str:
        """
        Genera un PDF de inspección visual
        
        Args:
            datos_proyecto: Datos del proyecto
            datos_inspeccion: Datos de la inspección filtrados por imagen
            output_filename: Nombre del archivo de salida
            
        Returns:
            str: Ruta del archivo PDF generado
        """
        # Formatear datos directamente desde los datos filtrados
        self.data = self._formatear_datos_inspeccion_visual(datos_proyecto, datos_inspeccion)
        
        # Generar PDF
        self.output_path = os.path.join(os.getcwd(), output_filename)
        self._generar_pdf(self.output_path)
        
        return self.output_path
    
    def generar_liquidos_penetrantes(self, datos_proyecto: Dict[str, Any], 
                                    datos_inspeccion: Dict[str, Any], 
                                    output_filename: str) -> str:
        """Genera un PDF de inspección de líquidos penetrantes"""
        # Formatear datos específicos para líquidos penetrantes
        self.data = self._formatear_datos_liquidos_penetrantes(datos_proyecto, datos_inspeccion)
        
        # Generar PDF
        self.output_path = os.path.join(os.getcwd(), output_filename)
        self._generar_pdf(self.output_path, "liquidos_penetrantes")
        
        return self.output_path
    
    def generar_particulas_magneticas(self, datos_proyecto: Dict[str, Any], 
                                     datos_inspeccion: Dict[str, Any], 
                                     output_filename: str) -> str:
        """Genera un PDF de inspección de partículas magnéticas"""
        self.data = self._formatear_datos_particulas_magneticas(datos_proyecto, datos_inspeccion)
        self.output_path = os.path.join(os.getcwd(), output_filename)
        self._generar_pdf(self.output_path, report_type="particulas_magneticas")
        return self.output_path
    
    def generar_ultrasonido(self, datos_proyecto: Dict[str, Any], 
                           datos_inspeccion: Dict[str, Any], 
                           output_filename: str) -> str:
        """Genera un PDF de inspección de ultrasonido"""
        self.data = self._formatear_datos_ultrasonido(datos_proyecto, datos_inspeccion)
        self.output_path = os.path.join(os.getcwd(), output_filename)
        self._generar_pdf(self.output_path, report_type="ultrasonido")
        return self.output_path
    
    def _generar_pdf(self, out_path: str, report_type: str = "visual"):
        """Genera el PDF usando reportlab"""
        enc = self.data["encabezado"]
        doc = BaseDocTemplate(
            out_path, pagesize=letter,
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=18*mm, bottomMargin=45*mm
        )

        # Configurar frames
        header_bottom_y = 220*mm
        padding = 6*mm
        first_top_y = header_bottom_y - padding
        first_height = first_top_y - doc.bottomMargin

        frame_first = Frame(doc.leftMargin, doc.bottomMargin, doc.width, first_height, id="first")
        frame_rest = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="rest")

        # Configurar templates
        template_first = PageTemplate(
            id="tpl_first",
            frames=[frame_first],
            onPage=lambda c, d: self._draw_header(c, d, enc, report_type),
            onPageEnd=lambda c, d: self._draw_footer(c, d, enc),
        )

        template_rest = PageTemplate(
            id="tpl_rest",
            frames=[frame_rest],
            onPage=lambda c, d: self._draw_header(c, d, enc, report_type),
            onPageEnd=lambda c, d: self._draw_footer(c, d, enc),
        )

        doc.addPageTemplates([template_first, template_rest])

        # Construir contenido según el tipo de reporte
        if report_type == "liquidos_penetrantes":
            story = self._build_story_liquidos_penetrantes(doc.width)
        elif report_type == "particulas_magneticas":
            story = self._build_story_particulas_magneticas(doc.width)
        elif report_type == "ultrasonido":
            story = self._build_story_ultrasonido(doc.width)
        else:
            story = self._build_story(doc.width)
        doc.build(story, canvasmaker=NumberedCanvas)
    
    def _draw_header(self, canv, doc, enc, report_type="visual"):
        """Dibuja el encabezado de cada página"""
        canv.saveState()
        is_first = (getattr(doc, "page", 1) == 1)

        # Títulos centrados (todas las páginas)
        canv.setFont("Helvetica-Bold", 13)
        
        # Determinar el título según el tipo de reporte
        if report_type == "liquidos_penetrantes":
            title = "INFORME INSPECCIÓN LÍQUIDOS PENETRANTES"
        elif report_type == "particulas_magneticas":
            title = "INFORME INSPECCIÓN PARTÍCULAS MAGNÉTICAS"
        elif report_type == "ultrasonido":
            title = "INFORME INSPECCIÓN ULTRASONIDO"
        else:
            title = "INFORME INSPECCIÓN VISUAL"
            
        canv.drawCentredString(105*mm, 272*mm, title)
        canv.setFont("Helvetica-Bold", 11)
        canv.drawCentredString(105*mm, 265*mm, enc.get("norma", "AWS D1.1 2020"))

        # Logo (opcional) a la izquierda
        logo = enc.get("logo")
        if logo:
            try:
                img = Image(logo, width=32*mm, height=16*mm)
                img.drawOn(canv, doc.leftMargin, 262*mm)
            except Exception:
                pass

        # Bloque de metadatos SOLO en página 1
        if is_first:
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

        # Texto vertical margen izquierdo
        canv.setFont("Helvetica", 7)
        canv.saveState()
        canv.translate(10*mm, 140*mm)
        canv.rotate(90)
        canv.drawString(0, 0, "© Joint and Welding Ingenieros S.A.S. 2024 - Versión 7.0")
        canv.restoreState()

        canv.restoreState()

    def _draw_footer(self, canv, doc, enc):
        """Dibuja el pie de página"""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle

        x0, w = doc.leftMargin, doc.width

        st_small   = ParagraphStyle("small",   fontName="Helvetica",       fontSize=7, leading=8)
        st_small_b = ParagraphStyle("small_b", parent=st_small,            fontName="Helvetica-Bold", alignment=1)
        st_small_r = ParagraphStyle("small_r", parent=st_small,            alignment=2)

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
        col_widths = [col_left, col_mid, col_right]

        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BOX", (0,0), (-1,-1), 0.8, colors.black),
            ("INNERGRID", (0,0), (-1,-1), 0.8, colors.black),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("ALIGN", (1,0), (1,0), "CENTER"),
            ("ALIGN", (2,0), (2,0), "LEFT"),
        ]))

        tw, th = t.wrapOn(canv, w, 0)
        by = 15*mm
        t.drawOn(canv, x0, by)

    def _section_box(self, title, rows, with_obs, total_w):
        """Crea una tabla de sección"""
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="SectionTitle",
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            leading=12
        )
        
        # Convert title to Paragraph if it's a string
        if isinstance(title, str):
            title_para = Paragraph(title, title_style)
        else:
            title_para = title
            
        cols = [total_w*0.7, total_w*0.3] if with_obs else [total_w]
        data = [[title_para, "OBSERVACIONES"]] if with_obs else [[title_para]]
        for r in rows:
            data.append([r, ""] if with_obs else [r])

        t = Table(data, colWidths=cols)
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.6, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        return t

    def _section_text_box(self, title, text, total_w):
        """Crea una caja de texto para sección"""
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        styles = getSampleStyleSheet()
        body_style = ParagraphStyle(
            name="BodyText",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            leftIndent=0,
            rightIndent=0
        )
        
        if isinstance(text, str):
            # Convert text to Paragraph for proper text wrapping
            if '\n' in text:
                # Handle multi-line text
                lines = text.split('\n')
                paragraphs = [Paragraph(line, body_style) for line in lines]
                rows = paragraphs
            else:
                rows = [Paragraph(text, body_style)]
        else:
            # Handle list of strings
            rows = [Paragraph(str(item), body_style) for item in text]
        
        return self._section_box(title, rows, False, total_w)

    def _formatear_datos_particulas_magneticas(self, datos_proyecto: Dict[str, Any],
                                              datos_inspeccion: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea los datos de inspección de partículas magnéticas para el PDF"""
        
        data = {
            "encabezado": {
                "cliente": datos_proyecto.get('cliente', 'Cliente'),
                "proyecto": datos_proyecto.get('proyecto', 'Proyecto'),
                "subproyecto": datos_proyecto.get('subproyecto', 'Subproyecto'),
                "contratista": datos_proyecto.get('contratista', 'Contratista'),
                "elaboro": datos_proyecto.get('inspector', 'Inspector'),
                "rep": datos_proyecto.get('numero_informe', 'REP-XXXX-XXXX'),
                "fecha": datos_proyecto.get('fecha', 'DD/MMM/YYYY'),
                "lugar": datos_proyecto.get('ubicacion', 'Ubicación'),
                "proceso_soldadura": ', '.join(datos_inspeccion.get('proceso_soldadura', ['SMAW'])) if isinstance(datos_inspeccion.get('proceso_soldadura'), list) else datos_inspeccion.get('proceso_soldadura', 'SMAW'),
                "tipo": "III - Partículas Magnéticas",
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020'),
                "procedimiento": datos_inspeccion.get('procedimiento', 'TLPR0027 - Inspección de Partículas Magnéticas - Rev. 1')
            },
            "seccion_1_procedimiento": {
                "procedimiento": datos_inspeccion.get('procedimiento', 'TLPR0027 - Inspección de Partículas Magnéticas - Rev. 1')
            },
            "seccion_2_normas": {
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020')
            },
            "seccion_3_equipos": {
                "equipos": datos_inspeccion.get('equipos', 'Kit de Partículas Magnéticas')
            },
            "seccion_4_material_base": {
                "material_base": ', '.join(datos_inspeccion.get('material_base', ['No especificado'])) if isinstance(datos_inspeccion.get('material_base'), list) else datos_inspeccion.get('material_base', 'No especificado')
            },
            "seccion_5_materiales": {
                "materiales": datos_inspeccion.get('materiales_utilizados', [])
            },
            "seccion_6_tipo_metodo": {
                "tipo_metodo": datos_inspeccion.get('tipo_y_metodo', [])
            },
            "seccion_7_parametros": {
                "parametros": datos_inspeccion.get('parametros_operacion', [])
            },
            "seccion_8_proceso_corriente": {
                "proceso_corriente": datos_inspeccion.get('proceso_y_corriente', [])
            },
            "seccion_9_elementos": {
                "elementos": datos_inspeccion.get('elementos', [])
            },
            "seccion_10_detalle": {
                "detalle_resultados": datos_inspeccion.get('detalle_resultados', ''),
                "observaciones_generales": datos_inspeccion.get('observaciones_generales', '')
            },
            "registros_fotograficos": datos_inspeccion.get('registros_fotograficos', [])
        }
        return data

    def _formatear_datos_ultrasonido(self, datos_proyecto: Dict[str, Any],
                                    datos_inspeccion: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea los datos de inspección de ultrasonido para el PDF"""
        
        data = {
            "encabezado": {
                "cliente": datos_proyecto.get('cliente', 'Cliente'),
                "proyecto": datos_proyecto.get('proyecto', 'Proyecto'),
                "subproyecto": datos_proyecto.get('subproyecto', 'Subproyecto'),
                "contratista": datos_proyecto.get('contratista', 'Contratista'),
                "elaboro": datos_proyecto.get('inspector', 'Inspector'),
                "rep": datos_proyecto.get('numero_informe', 'REP-XXXX-XXXX'),
                "fecha": datos_proyecto.get('fecha', 'DD/MMM/YYYY'),
                "lugar": datos_proyecto.get('ubicacion', 'Ubicación'),
                "proceso_soldadura": ', '.join(datos_inspeccion.get('soldadura', ['SMAW'])) if isinstance(datos_inspeccion.get('soldadura'), list) else datos_inspeccion.get('soldadura', 'SMAW'),
                "tipo": "IV - Ultrasonido",
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020'),
                "procedimiento": datos_inspeccion.get('procedimiento', 'TLPR0028 - Inspección de Ultrasonido - Rev. 1')
            },
            "seccion_1_procedimiento": {
                "procedimiento": datos_inspeccion.get('procedimiento', 'TLPR0028 - Inspección de Ultrasonido - Rev. 1')
            },
            "seccion_2_normas": {
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020')
            },
            "seccion_3_equipos": {
                "equipos": datos_inspeccion.get('equipo', 'Equipo de Ultrasonido'),
                "palpador": datos_inspeccion.get('palpador', 'Palpador')
            },
            "seccion_4_material_base": {
                "material_base": ', '.join(datos_inspeccion.get('material_base', ['No especificado'])) if isinstance(datos_inspeccion.get('material_base'), list) else datos_inspeccion.get('material_base', 'No especificado')
            },
            "seccion_5_juntas": {
                "juntas": datos_inspeccion.get('juntas', [])
            },
            "seccion_6_elementos": {
                "elementos": datos_inspeccion.get('elementos_inspeccionados', [])
            },
            "seccion_7_detalle": {
                "detalle_resultados": datos_inspeccion.get('detalle_resultados', ''),
                "observaciones_generales": datos_inspeccion.get('observaciones_generales', '')
            },
            "registros_fotograficos": datos_inspeccion.get('registros_fotograficos', [])
        }
        return data

    def _build_story(self, total_w):
        """Construye el contenido del PDF"""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="HSection", fontName="Helvetica-Bold", fontSize=10, spaceBefore=6, spaceAfter=4))
        styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9, leading=12))
        styles.add(ParagraphStyle(name="Legend", fontName="Helvetica", fontSize=8))

        story = []

        # CONTENIDO ESTÁTICO COMENTADO PARA EVITAR DUPLICACIÓN
        # Este método se usa solo para otros tipos de inspección, no para inspección visual
        # La inspección visual usa ReporteInspeccionVisual que tiene su propio _build_story dinámico
        
        # story.append(self._section_text_box("1. NORMAS PARA EL CRITERIO DE EVALUACIÓN:", self.data["seccion_1_normas"]["norma"], total_w))
        # story.append(Spacer(0, 3*mm))
        # story.append(self._section_text_box("2. EQUIPOS UTILIZADOS", self.data["seccion_2_equipos"]["equipos"], total_w))
        # story.append(Spacer(0, 3*mm))
        # story.append(self._section_text_box("3. MATERIAL BASE:", self.data["seccion_3_material_base"]["material_base"], total_w))
        # story.append(Spacer(0, 3*mm))
        # story.append(self._section_box("4. ANTES DE INICIAR EL PROCESO DE SOLDADURA", self.data["seccion_4_antes_soldadura"]["items"], True, total_w))
        # story.append(Spacer(0, 3*mm))
        # story.append(self._section_box("5. INICIO DE LA JUNTA", self.data["seccion_5_inicio_junta"]["items"], True, total_w))
        # story.append(Spacer(0, 3*mm))
        # story.append(self._section_box("6. DESPUÉS DE LA SOLDADURA", self.data["seccion_6_despues_soldadura"]["items"], True, total_w))

        # Página 2
        story.append(PageBreak())
        story.append(Spacer(0, 70*mm))
        story.append(Paragraph("ESQUEMA DE ELEMENTOS INSPECCIONADOS", styles["HSection"]))

        legend_rows = [[k, v] for k, v in self.data["seccion_7_elementos_inspeccionados"]["leyenda"].items()]
        legend_tbl = Table(legend_rows, colWidths=[20*mm, 60*mm])
        legend_tbl.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.black),
                                        ('FONT', (0,0), (-1,-1), 'Helvetica', 8),
                                        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke)]))
        conv_txt = ", ".join(self.data["seccion_7_elementos_inspeccionados"]["convencion_discontinuidades"])
        story.append(legend_tbl)
        story.append(Spacer(0, 3*mm))
        story.append(Paragraph(f"Convención de DISCONTINUIDAD: {conv_txt}", styles["Legend"]))

        ids = self.data["seccion_7_elementos_inspeccionados"]["items_esquema"]
        if ids:
            grid_data = [["ID", "Cal."]] + [[str(x["id"]), x["estado"]] for x in ids]
            grid = Table(grid_data, colWidths=[25*mm, 25*mm])
            grid.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.black),
                                      ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
                                      ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke)]))
            story.append(Spacer(0, 3*mm))
            story.append(grid)

        # Página 3
        story.append(PageBreak())
        story.append(Spacer(0, 60*mm))
        story.append(Paragraph("8. DETALLE ELEMENTOS INSPECCIONADOS", styles["HSection"]))

        detalle_data = [["ITEM", "ELEMENTO", "INDICACIÓN", "CAL"]]
        for r in self.data["seccion_8_detalle_elementos"]:
            detalle_data.append([r["item"], r["elemento"], r["indicacion"], r["cal"]])
        
        if len(detalle_data) > 1:
            detalle = Table(detalle_data, colWidths=[15*mm, 75*mm, 65*mm, 15*mm])
            detalle.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.black),
                                         ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
                                         ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
                                         ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(detalle)
        else:
            story.append(Paragraph("No hay elementos inspeccionados registrados.", styles["Body"]))

        story.append(Spacer(0, 4*mm))
        story.append(Paragraph("10. OBSERVACIONES", styles["HSection"]))
        obs_rows = [[f"• {x}"] for x in self.data["seccion_10_observaciones"]]
        
        # Verificar que hay observaciones antes de crear la tabla
        if obs_rows:
            obs_tbl = Table(obs_rows, colWidths=[total_w])
            obs_tbl.setStyle(TableStyle([('FONT', (0,0), (-1,-1), 'Helvetica', 9),
                                         ('LEADING', (0,0), (-1,-1), 12),
                                         ('LEFTPADDING', (0,0), (-1,-1), 2),
                                         ('RIGHTPADDING', (0,0), (-1,-1), 2)]))
            story.append(obs_tbl)
        else:
            # Si no hay observaciones, agregar un mensaje
            story.append(Paragraph("No hay observaciones registradas.", styles["Body"]))

        # Página 4
        story.append(PageBreak())
        story.append(Spacer(0, 60*mm))
        story.append(Paragraph("11. REGISTRO FOTOGRÁFICO", styles["HSection"]))

        fotos = self.data["seccion_11_registro_fotografico"]
        foto_cells = []
        for f in fotos:
            if f.get("imagen"):
                try:
                    img = Image(f["imagen"], width=75*mm, height=45*mm)
                except Exception:
                    img = Box(75*mm, 45*mm, "FOTO")
            else:
                img = Box(75*mm, 45*mm, "FOTO")
            caption = Paragraph(f"<b>{f['titulo']}</b><br/>{f['descripcion']}", styles['Body'])
            cell = Table([[img],[caption]], colWidths=[75*mm])
            cell.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                                      ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
            foto_cells.append(cell)

        if len(foto_cells) >= 6:
            grid_fotos = Table([
                [foto_cells[0], foto_cells[1]],
                [foto_cells[2], foto_cells[3]],
                [foto_cells[4], foto_cells[5]],
            ], colWidths=[(total_w/2)-5*mm, (total_w/2)-5*mm], rowHeights=[60*mm, 60*mm, 60*mm])
        elif len(foto_cells) > 0:
            grid_fotos = Table([foto_cells], colWidths=[(total_w/2)-5*mm, (total_w/2)-5*mm], rowHeights=[60*mm])
            grid_fotos.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                                            ('ALIGN',(0,0),(-1,-1),'CENTER')]))
            story.append(grid_fotos)
        else:
            # Si no hay fotos, agregar un mensaje
            story.append(Paragraph("No hay registros fotográficos.", styles["Body"]))

        return story 
    
    def _build_story_liquidos_penetrantes(self, total_w):
        """Construye el contenido del PDF específico para líquidos penetrantes"""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="HSection", fontName="Helvetica-Bold", fontSize=10, spaceBefore=6, spaceAfter=4))
        styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9, leading=12))
        styles.add(ParagraphStyle(name="Legend", fontName="Helvetica", fontSize=8))

        story = []

        # 1. NORMAS PARA EL CRITERIO DE EVALUACIÓN
        norma_text = f"Norma: {self.data['seccion_2_normas']['norma']}"
        story.append(self._section_text_box("1. NORMAS PARA EL CRITERIO DE EVALUACIÓN:", norma_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 2. PROCEDIMIENTO (Información General)
        procedimiento_value = self.data.get('seccion_1_procedimiento', {}).get('procedimiento', 'TLPR0026 - Inspección de Líquidos Penetrantes - Rev. 1')
        procedimiento_text = f"Procedimiento: {procedimiento_value}"
        story.append(self._section_text_box("2. PROCEDIMIENTO:", procedimiento_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 3. EQUIPOS UTILIZADOS
        story.append(self._section_text_box("3. EQUIPOS UTILIZADOS", self.data["seccion_2_equipos"]["equipos"], total_w))
        story.append(Spacer(0, 6*mm))

        # 4. MATERIAL BASE
        story.append(self._section_text_box("4. MATERIAL BASE:", self.data["seccion_3_material_base"]["material_base"], total_w))
        story.append(Spacer(0, 6*mm))

        # 5. MATERIALES UTILIZADOS
        materiales_text = "Materiales utilizados en la inspección de líquidos penetrantes"
        story.append(self._section_text_box("5. MATERIALES UTILIZADOS:", materiales_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 6. NORMAS PARA PROCEDIMIENTOS Y MÉTODOS DE APLICACIÓN
        tipo_metodo_text = f"Tipo: {self.data['seccion_5_tipo_metodo']['tipo']}\nMétodo: {self.data['seccion_5_tipo_metodo']['metodo']}"
        pasos_text = self.data['seccion_5_tipo_metodo'].get('pasos_procedimiento', '')
        if pasos_text:
            tipo_metodo_text += f"\n\nPasos del Procedimiento:\n{pasos_text}"
        story.append(self._section_text_box("6. NORMAS PARA PROCEDIMIENTOS Y MÉTODOS DE APLICACIÓN:", tipo_metodo_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 7. PARÁMETROS DE OPERACIÓN
        parametros_text = "Parámetros de operación para la inspección"
        story.append(self._section_text_box("7. PARÁMETROS DE OPERACIÓN:", parametros_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 8. ELEMENTOS INSPECCIONADOS
        elementos_text = "Elementos inspeccionados durante la prueba"
        story.append(self._section_text_box("8. ELEMENTOS INSPECCIONADOS:", elementos_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 9. DETALLE DE RESULTADOS
        detalle_text = self.data["seccion_8_detalle"]["detalle_resultados"] or "Sin detalles específicos"
        story.append(self._section_text_box("9. DETALLE DE ELEMENTOS INSPECCIONADOS Y RESULTADOS:", detalle_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 10. OBSERVACIONES GENERALES
        obs_text = self.data["seccion_8_detalle"]["observaciones_generales"] or "Sin observaciones"
        story.append(self._section_text_box("10. OBSERVACIONES GENERALES:", obs_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 11. REGISTROS FOTOGRÁFICOS
        story.append(Paragraph("11. REGISTROS FOTOGRÁFICOS", styles["HSection"]))
        story.append(Spacer(0, 3*mm))

        # Agregar fotos si existen
        fotos = self.data.get("seccion_9_fotos", [])
        if fotos:
            foto_cells = []
            for i, foto in enumerate(fotos):
                # Crear celda con imagen y descripción
                foto_cell = []
                if foto.get("imagen"):
                    foto_cell.append(Image(foto["imagen"], width=80*mm, height=60*mm))
                else:
                    foto_cell.append(Paragraph(f"Foto {i+1}", styles["Body"]))
                
                if foto.get("descripcion"):
                    foto_cell.append(Paragraph(foto["descripcion"], styles["Legend"]))
                
                foto_cells.append(foto_cell)

            # Crear tabla de fotos
            if len(foto_cells) >= 6:
                grid_fotos = Table([
                    [foto_cells[0], foto_cells[1]],
                    [foto_cells[2], foto_cells[3]],
                    [foto_cells[4], foto_cells[5]],
                ], colWidths=[(total_w/2)-5*mm, (total_w/2)-5*mm], rowHeights=[60*mm, 60*mm, 60*mm])
            elif len(foto_cells) > 0:
                grid_fotos = Table([foto_cells], colWidths=[(total_w/2)-5*mm, (total_w/2)-5*mm], rowHeights=[60*mm])
                grid_fotos.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                                                ('ALIGN',(0,0),(-1,-1),'CENTER')]))
                story.append(grid_fotos)
            else:
                story.append(Paragraph("No hay registros fotográficos.", styles["Body"]))
        else:
            story.append(Paragraph("No hay registros fotográficos.", styles["Body"]))

        return story

    def _build_story_particulas_magneticas(self, total_w):
        """Construye el contenido del PDF para partículas magnéticas"""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="HSection", fontName="Helvetica-Bold", fontSize=10, spaceBefore=6, spaceAfter=4))
        styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9, leading=12))
        styles.add(ParagraphStyle(name="Legend", fontName="Helvetica", fontSize=8))

        story = []

        # 1. PROCEDIMIENTO (Información General)
        procedimiento_value = self.data.get('seccion_1_procedimiento', {}).get('procedimiento', 'TLPR0027 - Inspección de Partículas Magnéticas - Rev. 1')
        procedimiento_text = f"Procedimiento: {procedimiento_value}"
        story.append(self._section_text_box("1. PROCEDIMIENTO:", procedimiento_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 2. NORMAS PARA EL CRITERIO DE EVALUACIÓN
        norma_text = f"Norma: {self.data['seccion_2_normas']['norma']}"
        story.append(self._section_text_box("2. NORMAS PARA EL CRITERIO DE EVALUACIÓN:", norma_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 3. EQUIPOS UTILIZADOS
        story.append(self._section_text_box("3. EQUIPOS UTILIZADOS", self.data["seccion_3_equipos"]["equipos"], total_w))
        story.append(Spacer(0, 6*mm))

        # 4. MATERIAL BASE
        story.append(self._section_text_box("4. MATERIAL BASE:", self.data["seccion_4_material_base"]["material_base"], total_w))
        story.append(Spacer(0, 6*mm))

        # 5. MATERIALES UTILIZADOS
        materiales_text = "Materiales utilizados en la inspección de partículas magnéticas"
        story.append(self._section_text_box("5. MATERIALES UTILIZADOS:", materiales_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 6. TIPO Y MÉTODO
        tipo_metodo_text = "Tipo y método de partículas magnéticas"
        story.append(self._section_text_box("6. TIPO Y MÉTODO:", tipo_metodo_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 7. PARÁMETROS DE OPERACIÓN
        parametros_text = "Parámetros de operación para la inspección"
        story.append(self._section_text_box("7. PARÁMETROS DE OPERACIÓN:", parametros_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 8. PROCESO Y CORRIENTE
        proceso_corriente_text = "Proceso y corriente utilizados"
        story.append(self._section_text_box("8. PROCESO Y CORRIENTE:", proceso_corriente_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 9. ELEMENTOS INSPECCIONADOS
        elementos_text = "Elementos inspeccionados durante la prueba"
        story.append(self._section_text_box("9. ELEMENTOS INSPECCIONADOS:", elementos_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 10. DETALLE DE RESULTADOS
        detalle_text = self.data["seccion_10_detalle"]["detalle_resultados"] or "Sin detalles específicos"
        story.append(self._section_text_box("10. DETALLE DE ELEMENTOS INSPECCIONADOS Y RESULTADOS:", detalle_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 11. OBSERVACIONES GENERALES
        obs_text = self.data["seccion_10_detalle"]["observaciones_generales"] or "Sin observaciones"
        story.append(self._section_text_box("11. OBSERVACIONES GENERALES:", obs_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 12. REGISTROS FOTOGRÁFICOS
        story.append(Paragraph("12. REGISTROS FOTOGRÁFICOS", styles["HSection"]))
        story.append(Spacer(0, 3*mm))
        
        # Manejar registros fotográficos
        if self.data.get("registros_fotograficos"):
            for i, foto in enumerate(self.data["registros_fotograficos"]):
                if foto and foto.get("imagen"):
                    try:
                        img = Image(foto["imagen"], width=120, height=90)
                        story.append(img)
                        story.append(Paragraph(f"Foto {i+1}: {foto.get('descripcion', 'Sin descripción')}", styles["Legend"]))
                        story.append(Spacer(0, 3*mm))
                    except Exception as e:
                        story.append(Paragraph(f"Error al cargar foto {i+1}: {str(e)}", styles["Body"]))
        else:
            # Si no hay fotos, agregar un mensaje
            story.append(Paragraph("No hay registros fotográficos.", styles["Body"]))

        return story

    def _build_story_ultrasonido(self, total_w):
        """Construye el contenido del PDF para ultrasonido"""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="HSection", fontName="Helvetica-Bold", fontSize=10, spaceBefore=6, spaceAfter=4))
        styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9, leading=12))
        styles.add(ParagraphStyle(name="Legend", fontName="Helvetica", fontSize=8))

        story = []

        # 1. PROCEDIMIENTO (Información General)
        procedimiento_value = self.data.get('seccion_1_procedimiento', {}).get('procedimiento', 'TLPR0028 - Inspección de Ultrasonido - Rev. 1')
        procedimiento_text = f"Procedimiento: {procedimiento_value}"
        story.append(self._section_text_box("1. PROCEDIMIENTO:", procedimiento_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 2. NORMAS PARA EL CRITERIO DE EVALUACIÓN
        norma_text = f"Norma: {self.data['seccion_2_normas']['norma']}"
        story.append(self._section_text_box("2. NORMAS PARA EL CRITERIO DE EVALUACIÓN:", norma_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 3. EQUIPOS UTILIZADOS
        equipos_text = f"Equipo: {self.data['seccion_3_equipos']['equipos']}\nPalpador: {self.data['seccion_3_equipos']['palpador']}"
        story.append(self._section_text_box("3. EQUIPOS UTILIZADOS", equipos_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 4. MATERIAL BASE
        story.append(self._section_text_box("4. MATERIAL BASE:", self.data["seccion_4_material_base"]["material_base"], total_w))
        story.append(Spacer(0, 6*mm))

        # 5. JUNTAS
        juntas_text = "Juntas inspeccionadas"
        story.append(self._section_text_box("5. JUNTAS:", juntas_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 6. ELEMENTOS INSPECCIONADOS
        elementos_text = "Elementos inspeccionados durante la prueba"
        story.append(self._section_text_box("6. ELEMENTOS INSPECCIONADOS:", elementos_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 7. DETALLE DE RESULTADOS
        detalle_text = self.data["seccion_7_detalle"]["detalle_resultados"] or "Sin detalles específicos"
        story.append(self._section_text_box("7. DETALLE DE ELEMENTOS INSPECCIONADOS Y RESULTADOS:", detalle_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 8. OBSERVACIONES GENERALES
        obs_text = self.data["seccion_7_detalle"]["observaciones_generales"] or "Sin observaciones"
        story.append(self._section_text_box("8. OBSERVACIONES GENERALES:", obs_text, total_w))
        story.append(Spacer(0, 6*mm))

        # 9. REGISTROS FOTOGRÁFICOS
        story.append(Paragraph("9. REGISTROS FOTOGRÁFICOS", styles["HSection"]))
        story.append(Spacer(0, 3*mm))
        
        # Manejar registros fotográficos
        if self.data.get("registros_fotograficos"):
            for i, foto in enumerate(self.data["registros_fotograficos"]):
                if foto and foto.get("imagen"):
                    try:
                        img = Image(foto["imagen"], width=120, height=90)
                        story.append(img)
                        story.append(Paragraph(f"Foto {i+1}: {foto.get('descripcion', 'Sin descripción')}", styles["Legend"]))
                        story.append(Spacer(0, 3*mm))
                    except Exception as e:
                        story.append(Paragraph(f"Error al cargar foto {i+1}: {str(e)}", styles["Body"]))
        else:
            # Si no hay fotos, agregar un mensaje
            story.append(Paragraph("No hay registros fotográficos.", styles["Body"]))

        return story

    def _formatear_datos_inspeccion_visual(self, datos_proyecto: Dict[str, Any], 
                                          datos_inspeccion: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea los datos de inspección visual para el PDF"""
        
        # Estructura de datos para el PDF basada en los datos reales
        data = {
            "encabezado": {
                "numero_informe": datos_proyecto.get('numero_informe', 'T1234I1005'),
                "fecha": datos_proyecto.get('fecha', '5-jun-24'),
                "cliente": datos_proyecto.get('cliente', 'Cliente'),
                "proyecto": datos_proyecto.get('proyecto', 'Proyecto'),
                "ubicacion": datos_proyecto.get('ubicacion', 'Lugar'),
                "inspector": datos_proyecto.get('inspector', 'Ing. Andrés López'),
                "contratista": datos_proyecto.get('contratista', 'Contratista'),
                "subproyecto": datos_proyecto.get('subproyecto', 'Subproyecto'),
                "proceso_soldadura": datos_inspeccion.get('proceso_soldadura', 'SMAW'),
                "tipo": datos_inspeccion.get('tipo', 'Manual'),
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020')
            },
            "seccion_1_normas": {
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020')
            },
            "seccion_2_equipos": {
                "equipos": datos_inspeccion.get('equipos', 'Flexómetro, Calibrador, galga soldadura, Cámara digital, linterna, Regla')
            },
            "seccion_3_material_base": {
                "material_base": datos_inspeccion.get('especificacion', 'No especificado')
            },
            "seccion_4_antes_soldadura": {
                "items": datos_inspeccion.get('antes_soldadura', [
                    'Chequear la calificación del personal',
                    'Chequear el tipo del material base y el de aporte',
                    'Chequear si hay algún tipo discontinuidad en el metal base',
                    'Chequear el alineamiento de la junta de soldadura',
                    'Chequear condiciones de precalentamiento'
                ])
            },
            "seccion_5_inicio_junta": {
                "items": datos_inspeccion.get('inicio_junta', [
                    'Angulo de chaflán',
                    'Hombro de raíz',
                    'Alineamiento de la junta',
                    'Respaldo con soldadura o platina',
                    'Limpieza de la junta',
                    'Puntos de soldadura (si se punteo)',
                    'Precalentamiento'
                ])
            },
            "seccion_6_despues_soldadura": {
                "items": datos_inspeccion.get('despues_soldadura', [
                    'Apariencia final de la soldadura',
                    'Tamaño final de la soldadura',
                    'Longitud de la soldadura',
                    'Cantidad de distorsión (en la pieza)',
                    'Tratamiento Térmico después de la soldadura'
                ])
            },
            "seccion_7_elementos_inspeccionados": {
                "leyenda": {
                    "A": "Aplica",
                    "N.A": "No aplica", 
                    "S": "Satisfactorio",
                    "N.S": "No Satisfactorio",
                    "F.A": "Fuera de Alcance"
                },
                "convencion_discontinuidades": ["A", "N.A", "S", "N.S", "F.A"],
                "items_esquema": []
            },
            "seccion_8_detalle_elementos": [
                {
                    "item": str(i+1),
                    "elemento": elem.get('elemento', ''),
                    "especificacion": elem.get('especificacion', ''),
                    "indicacion": elem.get('indicacion', ''),
                    "cal": elem.get('cal', 'Satisfactorio')
                }
                for i, elem in enumerate(datos_inspeccion.get('elementos_inspeccionados', []))
            ],
            "seccion_10_observaciones": [
                datos_inspeccion.get('observaciones_generales', '')
            ],
            "seccion_11_registro_fotografico": [
                {
                    "titulo": f"Foto {i+1}",
                    "descripcion": img.get('comentario', ''),
                    "imagen": None  # Las imágenes se manejan por separado
                }
                for i, img in enumerate(datos_inspeccion.get('registros_fotograficos', []))
            ]
        }
        
        return data 
    
    def _formatear_datos_liquidos_penetrantes(self, datos_proyecto: Dict[str, Any], 
                                            datos_inspeccion: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea los datos de inspección de líquidos penetrantes para el PDF"""
        
        # Estructura de datos para el PDF basada en los datos reales
        data = {
            "encabezado": {
                "numero_informe": datos_proyecto.get('numero_informe', 'T1234I1005'),
                "fecha": datos_proyecto.get('fecha', '5-jun-24'),
                "cliente": datos_proyecto.get('cliente', 'Cliente'),
                "proyecto": datos_proyecto.get('proyecto', 'Proyecto'),
                "ubicacion": datos_proyecto.get('ubicacion', 'Lugar'),
                "inspector": datos_proyecto.get('inspector', 'Ing. Andrés López'),
                "contratista": datos_proyecto.get('contratista', 'Contratista'),
                "subproyecto": datos_proyecto.get('subproyecto', 'Subproyecto'),
                "proceso_soldadura": ', '.join(datos_inspeccion.get('proceso', ['SMAW'])) if isinstance(datos_inspeccion.get('proceso'), list) else datos_inspeccion.get('proceso', 'SMAW'),
                "tipo": datos_inspeccion.get('tipo', 'II - Líquidos Penetrantes Visibles'),
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020'),
                "procedimiento": datos_inspeccion.get('procedimiento', 'TLPR0026 - Inspección de Líquidos Penetrantes - Rev. 1')
            },
            "seccion_1_procedimiento": {
                "procedimiento": datos_inspeccion.get('procedimiento', 'TLPR0026 - Inspección de Líquidos Penetrantes - Rev. 1')
            },
            "seccion_2_normas": {
                "norma": datos_inspeccion.get('norma', 'AWS D1.1 2020')
            },
            "seccion_2_equipos": {
                "equipos": datos_inspeccion.get('equipos', 'Kit de Líquidos Penetrantes')
            },
            "seccion_3_material_base": {
                "material_base": ', '.join(datos_inspeccion.get('especificacion', ['No especificado'])) if isinstance(datos_inspeccion.get('especificacion'), list) else datos_inspeccion.get('especificacion', 'No especificado')
            },
            "seccion_4_materiales": {
                "materiales": datos_inspeccion.get('materiales', {})
            },
            "seccion_5_tipo_metodo": {
                "tipo": datos_inspeccion.get('tipo', 'II - Líquidos Penetrantes Visibles'),
                "metodo": datos_inspeccion.get('metodo', 'C - Eliminables con Disolvente'),
                "pasos_procedimiento": datos_inspeccion.get('pasos_procedimiento', '')
            },
            "seccion_6_parametros": {
                "parametros": datos_inspeccion.get('parametros', [])
            },
            "seccion_7_elementos": {
                "elementos": datos_inspeccion.get('elementos', [])
            },
            "seccion_8_detalle": {
                "detalle_resultados": datos_inspeccion.get('detalle_resultados', ''),
                "observaciones_generales": datos_inspeccion.get('observaciones_generales', '')
            },
            "seccion_9_fotos": [
                {
                    "titulo": f"Foto {i+1}",
                    "descripcion": img.get('comentario', ''),
                    "imagen": None  # Las imágenes se manejan por separado
                }
                for i, img in enumerate(datos_inspeccion.get('registros_fotograficos', []))
            ]
        }
        
        return data