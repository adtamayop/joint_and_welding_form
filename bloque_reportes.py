import streamlit as st
import os
from reportes import (
    ReporteInspeccionVisual,
    ReporteLiquidosPenetrantes,
    ReporteParticulasMagneticas,
    ReporteUltrasonido
)
from utils import build_unique_report_filename

st.title("📄 Generación de Reportes")

# Modo de prueba: restringe la generación exclusivamente a Inspección Visual
SOLO_REPORTE_VISUAL = True

# Definir tipos de reportes disponibles
tipos_reportes = {
    "visual": {
        "nombre": "Inspección Visual",
        "modulo": "2_datos_de_inspeccion_visual.py",
        "icono": "👁️",
        "descripcion": "Inspección visual de superficies y estructuras",
        "clase": ReporteInspeccionVisual
    },
    "liquidos_penetrantes": {
        "nombre": "Líquidos Penetrantes", 
        "modulo": "3_datos_de_inspeccion_de_liquidos_penetrantes.py",
        "icono": "💧",
        "descripcion": "Inspección mediante líquidos penetrantes",
        "clase": ReporteLiquidosPenetrantes
    },
    "particulas_magneticas": {
        "nombre": "Partículas Magnéticas",
        "modulo": "4_datos_de_inspeccion_de_particulas_magneticas.py", 
        "icono": "🧲",
        "descripcion": "Inspección mediante partículas magnéticas",
        "clase": ReporteParticulasMagneticas
    },
    "ultrasonido": {
        "nombre": "Ultrasonido",
        "modulo": "5_datos_de_inspeccion_de_ultrasonido.py",
        "icono": "🔊", 
        "descripcion": "Inspección mediante ultrasonido",
        "clase": ReporteUltrasonido
    }
}

# Mostrar selector de tipo de reporte
st.subheader("📋 Seleccionar Tipo de Reporte")

# Verificar qué tipos están disponibles
tipos_disponibles = []
for tipo, info in tipos_reportes.items():
    # Crear instancia temporal para verificar disponibilidad
    reporte_temp = info["clase"]()
    if reporte_temp.verificar_datos_disponibles():
        tipos_disponibles.append(tipo)

# Aplicar restricción global para corridas de prueba
if SOLO_REPORTE_VISUAL:
    tipos_disponibles = [tipo for tipo in tipos_disponibles if tipo == "visual"]

if not tipos_disponibles:
    st.warning("⚠️ No hay datos disponibles para generar reportes.")
    if SOLO_REPORTE_VISUAL:
        st.info("💡 En modo de prueba, solo se permite generar Inspección Visual. Complete ese módulo para continuar.")
    else:
        st.info("💡 Complete los datos en los módulos correspondientes antes de generar un reporte.")
else:
    if SOLO_REPORTE_VISUAL:
        st.info("🧪 Modo de prueba activo: solo está habilitado el informe de Inspección Visual.")

    # Crear selector de tipo de reporte
    tipo_seleccionado = st.selectbox(
        "Seleccione el tipo de reporte a generar:",
        options=tipos_disponibles,
        format_func=lambda x: f"{tipos_reportes[x]['icono']} {tipos_reportes[x]['nombre']}",
        help="Seleccione el tipo de inspección para el cual desea generar el reporte"
    )
    
    if tipo_seleccionado:
        info_tipo = tipos_reportes[tipo_seleccionado]
        
        # Mostrar información del tipo seleccionado
        st.info(f"""
        **{info_tipo['icono']} {info_tipo['nombre']}**
        
        {info_tipo['descripcion']}
        
        Módulo de datos: `{info_tipo['modulo']}`
        """)
        
        # Botón para generar reporte
        if st.button(f"🔄 Generar Reporte de {info_tipo['nombre']}", type="primary"):
            with st.spinner(f"Generando reporte de {info_tipo['nombre']}..."):
                try:
                    # Salvaguarda extra en caso de manipulación manual del estado
                    if SOLO_REPORTE_VISUAL and tipo_seleccionado != "visual":
                        st.error("❌ En modo de prueba solo se puede generar el reporte de Inspección Visual.")
                        st.stop()

                    # Crear instancia del reporte específico
                    reporte = info_tipo["clase"]()
                    
                    # Generar el reporte
                    output_filename = build_unique_report_filename(tipo_seleccionado)
                    output_path = reporte.generar_reporte(output_filename)
                    
                    # Leer el archivo generado
                    try:
                        with open(output_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                    finally:
                        try:
                            if os.path.exists(output_path):
                                os.remove(output_path)
                        except OSError:
                            pass
                    
                    # Mostrar mensaje de éxito
                    st.success(f"✅ Reporte de {info_tipo['nombre']} generado exitosamente!")
                    
                    # Proporcionar descarga del PDF
                    st.download_button(
                        label=f"📥 Descargar Reporte de {info_tipo['nombre']}",
                        data=pdf_bytes,
                        file_name=output_filename,
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error al generar el reporte: {str(e)}")
                    st.write("**Posibles causas:**")
                    st.write("- Falta de datos en los módulos correspondientes")
                    st.write("- Error en la estructura de datos")
                    st.write("- Problema con las dependencias")

# Información adicional
with st.expander("ℹ️ Información sobre los Reportes", expanded=False):
    st.write("""
    **Tipos de Reportes Disponibles:**
    
    - **👁️ Inspección Visual:** Para inspección visual de superficies y estructuras
    - **💧 Líquidos Penetrantes:** Para detectar discontinuidades superficiales
    - **🧲 Partículas Magnéticas:** Para detectar discontinuidades en materiales ferromagnéticos
    - **🔊 Ultrasonido:** Para detectar discontinuidades internas
    
    **Nota:** Solo se muestran los tipos de reportes para los cuales hay datos disponibles.
    """)

# Debug opcional
if st.checkbox("🔧 Modo Debug (Mostrar información técnica)", False):
    st.write("**Información Técnica:**")
    st.write(f"- Tipos disponibles: {tipos_disponibles}")
    st.write("- Módulos de reportes específicos:")
    for tipo, info in tipos_reportes.items():
        reporte_temp = info["clase"]()
        disponible = reporte_temp.verificar_datos_disponibles()
        st.write(f"  - {info['nombre']}: {'✅' if disponible else '❌'}")
    st.write("- Módulo de reportes: `reportes/`")
