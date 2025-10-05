import streamlit as st
from datetime import datetime
from utils import cargar_inspectores, cargar_normas


def formatear_fecha_para_display(fecha):
    """Convierte un objeto date a formato DD/MMM/YYYY"""
    if hasattr(fecha, 'strftime'):
        meses_abrev = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
                      'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
        return f"{fecha.day:02d}/{meses_abrev[fecha.month-1]}/{fecha.year}"
    return str(fecha)

# Configuración de la página
st.set_page_config(
    page_title="Datos del Proyecto",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado restaurado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stTabs {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stTabs"] > div {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background: none !important;
        height: 0px !important;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    .module-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .module-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stTabs div, .stTabs [data-baseweb="tab-list"], .stTabs, div[data-testid="stTabs"], div[data-testid="stTabs"] > div {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Título principal con icono y descripción
st.title("📋 Datos del Proyecto")
st.markdown("Configure los detalles de su informe y seleccione los módulos necesarios para su inspección.")

# Barra de progreso
if "bloque_1" in st.session_state:
    progress = 100
else:
    progress = 0
st.progress(progress/100)

# Crear pestañas para organizar la información
tab1, tab2 = st.tabs(["📝 Datos del Proyecto", "⚙️ Configuración de Módulos"])

# Definir módulos disponibles
modulos_disponibles = {
    "Inspección Visual": {
        "archivo": "2_datos_de_inspeccion_visual.py",
        "descripcion": "Inspección visual detallada de superficies y estructuras",
        "icono": "👁️",
        "titulo_sidebar": "Datos de Inspección Visual"
    },
    "Líquidos Penetrantes": {
        "archivo": "3_datos_de_inspeccion_de_liquidos_penetrantes.py",
        "descripcion": "Inspección mediante líquidos penetrantes para detectar discontinuidades superficiales",
        "icono": "💧",
        "titulo_sidebar": "Inspección de Líquidos Penetrantes"
    },
    "Partículas Magnéticas": {
        "archivo": "4_datos_de_inspeccion_de_particulas_magneticas.py",
        "descripcion": "Inspección mediante partículas magnéticas para detectar discontinuidades en materiales ferromagnéticos",
        "icono": "🧲",
        "titulo_sidebar": "Inspección de Partículas Magnéticas"
    },
    "Ultrasonido": {
        "archivo": "5_datos_de_inspeccion_de_ultrasonido.py",
        "descripcion": "Inspección mediante ondas ultrasónicas para detectar discontinuidades internas",
        "icono": "📡",
        "titulo_sidebar": "Inspección de Ultrasonido"
    }
}

# Módulos seleccionados por defecto
modulos_default = ["Inspección Visual", "Líquidos Penetrantes"]

with tab1:
    # Usar valores guardados si existen, si no usar por defecto
    def_valores = {
        "cliente": "Nureon",
        "proyecto": "Inspección de Estructuras",
        "subproyecto": "Inspección No Destructiva",
        "contratista": "Nureon S.A.S",
        "reporte_no": f"REP-{datetime.now().year}-{datetime.now().strftime('%m%d')}",
        "elaboro": "Andrés López",
        "norma_global": "AWS D1.1 2020",
        "fecha": datetime.now().date(),
        "lugar": "Bogotá, Colombia",
        "firma_1": "Firma del inspector que realiza la inspección y el informe",
        "firma_2": "Revisa el informe",
        "firma_3": "Cliente",
        "modulos_seleccionados": modulos_default
    }

    if "bloque_1" in st.session_state:
        valores = st.session_state.bloque_1.copy()
        if "firmas" in valores:
            valores["firma_1"] = valores["firmas"].get("firma_1", def_valores["firma_1"])
            valores["firma_2"] = valores["firmas"].get("firma_2", def_valores["firma_2"])
            valores["firma_3"] = valores["firmas"].get("firma_3", def_valores["firma_3"])
    else:
        valores = def_valores.copy()
        # Inicializar la configuración de páginas
        st.session_state.pages_config = {
            "modulos": [
                st.Page(modulos_disponibles[modulo]["archivo"], title=modulos_disponibles[modulo]["titulo_sidebar"])
                for modulo in modulos_default
            ]
        }

    # Crear columnas para los campos del formulario
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Información General")
        with st.container():
            cliente = st.text_input("Cliente", valores["cliente"], help="Nombre del cliente o empresa")
            proyecto = st.text_input("Proyecto", valores["proyecto"], help="Nombre del proyecto")
            subproyecto = st.text_input("Subproyecto", valores["subproyecto"], help="Nombre del subproyecto o área específica")
            contratista = st.text_input("Contratista", valores["contratista"], help="Nombre de la empresa contratista")
            reporte_no = st.text_input("Reporte N°", valores["reporte_no"], help="Número de identificación del reporte")

    with col2:
        st.subheader("📋 Detalles del Informe")
        with st.container():
            # Cargar lista de inspectores desde CSV
            inspectores = cargar_inspectores()
            elaboro = st.selectbox("Elaboró", options=inspectores, index=inspectores.index(valores["elaboro"]) if valores["elaboro"] in inspectores else 0, help="Nombre del inspector que elabora el informe")
            # Cargar lista de normas desde CSV
            normas = cargar_normas()
            norma_global = st.selectbox("Norma global", options=normas, index=normas.index(valores["norma_global"]) if valores["norma_global"] in normas else 0, help="Norma de referencia para la inspección")
            st.session_state["norma_global"] = norma_global
            fecha = st.date_input("Fecha", value=valores["fecha"] if hasattr(valores["fecha"], 'strftime') else datetime.now().date(), help="Fecha de la inspección")
            lugar = st.text_input("Lugar", valores["lugar"], help="Ubicación donde se realiza la inspección")

    # Sección de firmas en un contenedor expandible
    with st.expander("👥 Firmas", expanded=True):
        st.markdown("Configure las firmas necesarias para el informe")
        col1, col2, col3 = st.columns(3)
        with col1:
            firma_1 = st.text_input("Firma 1", valores["firma_1"], help="Inspector que realiza la inspección")
        with col2:
            firma_2 = st.text_input("Firma 2", valores["firma_2"], help="Revisor del informe")
        with col3:
            firma_3 = st.text_input("Firma 3", valores["firma_3"], help="Cliente o representante")

with tab2:
    st.subheader("🎯 Selección de Módulos")
    st.markdown("Seleccione los módulos que desea incluir en el informe:")

    # Crear columnas para los módulos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Módulos Disponibles")
        modulos_seleccionados = []
        
        for nombre, info in modulos_disponibles.items():
            with st.container():
                st.markdown(f"""
                <div class="module-card">
                    <h4>{info['icono']} {nombre}</h4>
                    <p>{info['descripcion']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.checkbox(f"Incluir {nombre}", 
                             value=nombre in valores.get("modulos_seleccionados", modulos_default),
                             key=f"modulo_{nombre}"):
                    modulos_seleccionados.append(nombre)

    with col2:
        st.markdown("### ℹ️ Información")
        st.info("""
        **Instrucciones:**
        1. Seleccione los módulos que necesita para su inspección
        2. Cada módulo contiene formularios específicos
        3. Los módulos seleccionados aparecerán en la barra lateral
        4. Puede modificar su selección en cualquier momento
        """)
        
        if modulos_seleccionados:
            st.success(f"✅ {len(modulos_seleccionados)} módulos seleccionados")
        else:
            st.warning("⚠️ No hay módulos seleccionados")

# Botón de guardar en la parte inferior
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
        if not modulos_seleccionados:
            st.error("⚠️ Debe seleccionar al menos un módulo")
        else:
            # Guardar datos del proyecto en formato para reporte
            st.session_state.datos_proyecto = {
                "numero_informe": reporte_no,
                "fecha": formatear_fecha_para_display(fecha) if hasattr(fecha, 'strftime') else str(fecha),
                "cliente": cliente,
                "proyecto": proyecto,
                "ubicacion": lugar,
                "inspector": elaboro,
                "contratista": contratista,
                "subproyecto": subproyecto,
                "norma_global": norma_global,
                "firmas": {
                    "firma_1": firma_1,
                    "firma_2": firma_2,
                    "firma_3": firma_3
                }
            }
            
            # También guardar en bloque_1 para compatibilidad
            st.session_state.bloque_1 = {
                "cliente": cliente,
                "proyecto": proyecto,
                "subproyecto": subproyecto,
                "contratista": contratista,
                "reporte_no": reporte_no,
                "elaboro": elaboro,
                "norma_global": norma_global,
                "fecha": fecha,
                "lugar": lugar,
                "firmas": {
                    "firma_1": firma_1,
                    "firma_2": firma_2,
                    "firma_3": firma_3
                },
                "modulos_seleccionados": modulos_seleccionados
            }
            
            # Actualizar la configuración de páginas en session_state
            if "pages_config" not in st.session_state:
                st.session_state.pages_config = {}
            
            # Actualizar la configuración de módulos
            st.session_state.pages_config["modulos"] = [
                st.Page(modulos_disponibles[modulo]["archivo"], title=modulos_disponibles[modulo]["titulo_sidebar"])
                for modulo in modulos_seleccionados
            ]
            
            st.success("✅ Configuración guardada correctamente")
            st.balloons()
            st.rerun() 