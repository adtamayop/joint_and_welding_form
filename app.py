import streamlit as st

# Configuración inicial de páginas
modulos_sidebar_titles = {
    "1_datos_del_proyecto.py": "Datos del Proyecto",
    "2_datos_de_inspeccion_visual.py": "Datos de Inspección Visual",
    "3_datos_de_inspeccion_de_liquidos_penetrantes.py": "Datos de Inspección de Líquidos Penetrantes",
    "4_datos_de_inspeccion_de_particulas_magneticas.py": "Datos de Inspección de Partículas Magnéticas",
    "5_datos_de_inspeccion_de_ultrasonido.py": "Datos de Inspección de Ultrasonido"
}

def get_sidebar_title(archivo):
    return modulos_sidebar_titles.get(archivo, archivo)

default_pages = {
    "Encabezado y Firmas": [
        st.Page("1_datos_del_proyecto.py", title="Datos del Proyecto"),
    ],
    "Módulos": [
        st.Page("2_datos_de_inspeccion_visual.py", title=get_sidebar_title("2_datos_de_inspeccion_visual.py")),
        st.Page("3_datos_de_inspeccion_de_liquidos_penetrantes.py", title=get_sidebar_title("3_datos_de_inspeccion_de_liquidos_penetrantes.py")),
    ],
    "Reports": [
        st.Page("bloque_reportes.py", title="Generación de reportes"),
    ],
}

# Inicializar la configuración de páginas si no existe
if "pages_config" not in st.session_state:
    st.session_state.pages_config = {
        "modulos": [
            st.Page("2_datos_de_inspeccion_visual.py", title=get_sidebar_title("2_datos_de_inspeccion_visual.py")),
            st.Page("3_datos_de_inspeccion_de_liquidos_penetrantes.py", title=get_sidebar_title("3_datos_de_inspeccion_de_liquidos_penetrantes.py")),
        ]
    }

# Obtener la configuración de páginas del session_state si existe
if "pages_config" in st.session_state and "modulos" in st.session_state.pages_config:
    # Crear una copia de las páginas por defecto
    pages = default_pages.copy()
    # Actualizar la sección de módulos con la configuración dinámica
    pages["Módulos"] = st.session_state.pages_config["modulos"]
else:
    pages = default_pages

pg = st.navigation(pages)
pg.run()