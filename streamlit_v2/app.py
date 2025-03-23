import yaml
import pandas as pd
import streamlit as st
from datetime import date, datetime
import base64
import os
import config
from typing import List

st.set_page_config(layout=config.LAYOUT)

@st.cache_data
def image_to_base64(image_path: str) -> str:
    """Converts an image at the given path to a base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

def load_config(file) -> dict:
    """Loads the content of a YAML file from a file-like object."""
    try:
        string_data = file.read().decode("utf-8")
        return yaml.safe_load(string_data) or {}
    except Exception as e:
        st.error(f"Error loading YAML file: {e}")
        return {}

def load_default_yaml(file_path: str) -> dict:
    """Loads the content of a YAML file from the default path."""
    try:
        with open(file_path, "rb") as f:
            return yaml.safe_load(f.read().decode("utf-8")) or {}
    except Exception as e:
        st.error(f"Error loading default YAML: {e}")
        return {}
    
def custom_selectbox(label: str, options: List[str], session_list: List[str], key: str, new_key: str) -> str:
    # De esto está pendiente almacenar los nuevos valores en el archivo yaml
    opciones = options + ["Otro..."]
    opcion = st.selectbox(label, opciones, key=key)
    if opcion == "Otro...":
        nuevo_valor = st.text_input(f"Ingrese el nuevo {label.lower()}", key=new_key)
        if nuevo_valor and nuevo_valor not in session_list:
            session_list.append(nuevo_valor)
            return nuevo_valor
        else:
            return opcion
    else:
        return opcion

if os.path.exists(config.LOGO_PATH):
    logo_base64 = image_to_base64(config.LOGO_PATH)
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo" style="max-width: 100%; height: auto;">
        </div>
        """,
        unsafe_allow_html=True
    )

##################################################
#################### BLOQUE 1 ####################
##################################################

st.title("Información del proyecto")

try:
    DEFAULT_DATE_OBJ = datetime.strptime(config.DEFAULT_DATE, "%Y-%m-%d").date()
except Exception:
    DEFAULT_DATE_OBJ = date.today()

uploaded_project_file = st.file_uploader("Carga el archivo del reporte", type=["yaml", "yml"], key="reporte")
if uploaded_project_file is not None:
    project_config = load_config(uploaded_project_file)
else:
    project_config = load_default_yaml(config.DEFAULT_PROJECT_INFO_PATH)

if "fecha" in project_config:
    try:
        fecha_default = datetime.strptime(project_config.get("fecha"), "%Y-%m-%d").date()
    except Exception:
        fecha_default = DEFAULT_DATE_OBJ
else:
    fecha_default = DEFAULT_DATE_OBJ

with st.form("project_info"):
    cliente = st.text_input("Cliente", project_config.get("cliente", config.DEFAULT_TEXT))
    proyecto = st.text_input("Proyecto", project_config.get("proyecto", config.DEFAULT_TEXT))
    subproyecto = st.text_input("Subproyecto", project_config.get("subproyecto", config.DEFAULT_TEXT))
    contratista = st.text_input("Contratista", project_config.get("contratista", config.DEFAULT_TEXT))
    rep_no = st.text_input("Rep N°", project_config.get("rep_no", config.DEFAULT_TEXT))
    lugar = st.text_input("Lugar", project_config.get("lugar", config.DEFAULT_TEXT))
    elaboro = st.selectbox("Elaboró", project_config.get("elaboro", [config.DEFAULT_TEXT]))
    fecha = st.date_input("Fecha", fecha_default)
    submit_project = st.form_submit_button("Guardar Datos")

    if submit_project:
        st.success("#### ✅ Datos guardados correctamente")
        st.session_state.bloque_1 = {
            "cliente": cliente,
            "proyecto": proyecto,
            "subproyecto": subproyecto,
            "contratista": contratista,
            "elaboro": elaboro,
            "rep_no": rep_no,
            "fecha": fecha,
            "lugar": lugar
    }

##################################################
#################### BLOQUE 2 ####################
##################################################

st.title("Datos de Evaluación de Soldadura")

uploaded_welding_file = st.file_uploader("Carga archivo normas soldadura", type=["yaml", "yml"], key="soldadura")
if uploaded_welding_file is not None:
    welding_config = load_config(uploaded_welding_file)
else:
    welding_config = load_default_yaml(config.DEFAULT_NORMAS_PATH)

with st.form("normas_soldadura"):
    norma = st.selectbox("NORMAS PARA EL CRITERIO DE EVALUACIÓN:", 
                         welding_config.get("normas", [config.DEFAULT_TEXT]))
    procedimiento = st.selectbox("PROCEDIMIENTO:", 
                                 welding_config.get("procedimientos", [config.DEFAULT_TEXT]))
    especificacion = st.selectbox("ESPECIFICACIÓN MATERIAL BASE:", 
                                  welding_config.get("materiales", [config.DEFAULT_TEXT]))
    proceso = st.selectbox("PROCESO DE SOLDADURA:", 
                           welding_config.get("procesos", [config.DEFAULT_TEXT]))
    equipos = st.text_area("EQUIPOS UTILIZADOS:", 
                           welding_config.get("equipos", config.DEFAULT_TEXT))
    submit_welding = st.form_submit_button("Guardar Datos")

    if submit_welding:
        st.success("### Datos guardados correctamente")
        st.session_state.bloque_2 = {
            "norma": norma,
            "procedimiento": procedimiento,
            "especificacion": especificacion,
            "proceso": proceso,
            "equipos": equipos
        }

##################################################
#################### BLOQUE 3 ####################
##################################################

st.title('Selección de Materiales Utilizados')

uploaded_material_file = st.file_uploader("Carga archivo de configuración de materiales", type=["yaml", "yml"], key="material_config")
if uploaded_material_file is not None:
    material_config = load_config(uploaded_material_file)
else:
    material_config = load_default_yaml(config.DEFAULT_MATERIALS_PATH)

if "detalles" not in st.session_state:
    st.session_state.detalles = material_config.get("detalles", [config.DEFAULT_TEXT])
if "fabricantes" not in st.session_state:
    st.session_state.fabricantes = material_config.get("fabricantes", [config.DEFAULT_TEXT])
if "referencias" not in st.session_state:
    st.session_state.referencias = material_config.get("referencias", [config.DEFAULT_TEXT])
if "lotes" not in st.session_state:
    st.session_state.lotes = material_config.get("lotes", [config.DEFAULT_TEXT])

num_entries = config.DEFAULT_MATERIALS_ENTRIES
data = []
st.write("### Selecciona los parámetros para cada material:")

for i in range(num_entries):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        detalle = custom_selectbox(f"Detalle {i+1}", st.session_state.detalles, st.session_state.detalles,
                                   key=f"detalle_{i}", new_key=f"nuevo_detalle_{i}")
    
    with col2:
        fabricante = custom_selectbox(f"Fabricante {i+1}", st.session_state.fabricantes, st.session_state.fabricantes,
                                      key=f"fabricante_{i}", new_key=f"nuevo_fabricante_{i}")
    
    with col3:
        referencia = custom_selectbox(f"Referencia {i+1}", st.session_state.referencias, st.session_state.referencias,
                                      key=f"referencia_{i}", new_key=f"nueva_referencia_{i}")
    
    with col4:
        lote = custom_selectbox(f"Lote {i+1}", st.session_state.lotes, st.session_state.lotes,
                                key=f"lote_{i}", new_key=f"nuevo_lote_{i}")
    
    data.append([detalle, fabricante, referencia, lote])

df = pd.DataFrame(data, columns=["DETALLE", "FABRICANTE", "REFERENCIA COMERCIAL", "LOTE"])

if st.button("Guardar Datos", key="guardar_datos_bloque_3"):
    st.success("#### ✅ Datos guardados correctamente")
    st.session_state.bloque_3 = {"data": df}

##################################################
#################### BLOQUE 4 ####################
##################################################

st.title("Normas para procedimientos")

uploaded_file_block4 = st.file_uploader("Carga archivo de normas y procedimientos", type=["yaml", "yml"], key="block4")
if uploaded_file_block4 is not None:
    block4_config = load_config(uploaded_file_block4)
else:
    block4_config = load_default_yaml(config.DEFAULT_MATERIALS_PROCESS_PATH)

normas_value = block4_config.get("normas", config.DEFAULT_TEXT)
tipo_options = block4_config.get("tipo_opciones", [config.DEFAULT_TEXT, config.DEFAULT_TEXT])
metodo_options = block4_config.get("metodo_opciones", [config.DEFAULT_TEXT])
procedimiento_value = block4_config.get("procedimiento", config.DEFAULT_TEXT)

with st.form("form_block4"):
    st.text_input("Normas (7.0)", normas_value, disabled=True)
    tipo = st.selectbox("Tipo (7.1)", tipo_options, key="tipo_block4")
    metodo = st.selectbox("Método (7.1)", metodo_options, key="metodo_block4")
    procedimiento = st.text_area("Procedimiento (7.2)", procedimiento_value, key="procedimiento_block4")
    
    submit_block4 = st.form_submit_button("Guardar Datos")
    if submit_block4:
        st.success("#### ✅ Datos guardados correctamente")
        st.session_state.bloque_4 = {
            "normas": normas_value,
            "tipo": tipo,
            "metodo": metodo,
            "procedimiento": procedimiento
        }

##################################################
#################### BLOQUE 5 ####################
##################################################


st.title("Parámetros de Operación")

num_rows = 4

uploaded_operaciones_file = st.file_uploader("Carga archivo de parámetros de operación", type=["yaml", "yml"], key="operaciones")
if uploaded_operaciones_file is not None:
    op_config = load_config(uploaded_operaciones_file)
else:
    op_config = load_default_yaml(config.DEFAULT_MATERIALS_OPERATION_PATH)

actividades = op_config.get("actividades", [config.DEFAULT_TEXT])
tiempos = op_config.get("tiempos", [config.DEFAULT_TEXT])
temperaturas = op_config.get("temperaturas", [config.DEFAULT_TEXT])
aplicaciones = op_config.get("aplicaciones", [config.DEFAULT_TEXT])
iluminaciones = op_config.get("iluminaciones", [config.DEFAULT_TEXT])

data = []

st.write("### Selecciona los parámetros para cada actividad:")

for i in range(num_rows):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        actividad = st.selectbox(f"Actividad {i+1}", actividades, key=f"act_{i}")
    with col2:
        tiempo = st.selectbox(f"Tiempo {i+1}", tiempos, key=f"time_{i}")
    with col3:
        temperatura = st.selectbox(f"Temp. {i+1}", temperaturas, key=f"temp_{i}")
    with col4:
        aplicacion = st.selectbox(f"Aplicación {i+1}", aplicaciones, key=f"aplic_{i}")
    with col5:
        iluminacion = st.selectbox(f"Iluminación {i+1}", iluminaciones, key=f"ilum_{i}")
    
    data.append([actividad, tiempo, temperatura, aplicacion, iluminacion])

df = pd.DataFrame(data, columns=["ACTIVIDAD", "TIEMPO DE PERMANENCIA", "TEMPERATURA", "APLICACIÓN", "ILUMINACIÓN"])

if st.button("Guardar Datos", key="guardar_datos_bloque_5"):
    st.success("#### ✅ Datos guardados correctamente")
    st.session_state.bloque_5 = {
        "data": df
    }

##################################################
#################### BLOQUE 6 ####################
##################################################


procedimiento = st.text_area(
    "Elementos inspeccionados",
    """Inspección a las uniones soldadas correspondientes a la estructura metálica de Puente Metro - Madera."""
)

if st.button("Guardar Datos", key="guardar_datos_bloque_6"):
    st.write("### Datos guardados correctamente")
    st.session_state.bloque_6 = {
        "procedimiento": procedimiento
    }


if "imagenes" not in st.session_state:
    st.session_state.imagenes = []

if "delete_idx" not in st.session_state:
    st.session_state.delete_idx = None

st.title("Esquema Estructura Inspeccionada")

st.subheader("Cargar nuevas imágenes")
uploaded_files = st.file_uploader(
    "Selecciona una o varias imágenes",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="file_uploader_bloque_7"  # Add a unique key
)

if st.button("Agregar Imágenes", key="agregar_imagenes_bloque_7"):  # Add a unique key
    if uploaded_files:
        for file in uploaded_files:
            nueva_imagen = {
                "archivo": file,
                "nombre": file.name,
                "comentario": ""
            }
            st.session_state.imagenes.append(nueva_imagen)
    else:
        st.warning("No has seleccionado ningún archivo.")

st.write("---")

st.subheader("Imágenes cargadas")
if len(st.session_state.imagenes) == 0:
    st.info("No hay imágenes cargadas todavía.")
else:
    for i, img_info in enumerate(st.session_state.imagenes):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img_info["archivo"], use_container_width=True)
        
        with col2:
            st.write(f"**Archivo:** {img_info['nombre']}")
            nuevo_comentario = st.text_area(
                "Comentario",
                value=img_info["comentario"],
                key=f"comentario_{i}"
            )
            st.session_state.imagenes[i]["comentario"] = nuevo_comentario
            
            if st.button("Eliminar esta imagen", key=f"eliminar_{i}"):
                st.session_state.delete_idx = i

    if st.session_state.delete_idx is not None:
        st.session_state.imagenes.pop(st.session_state.delete_idx)
        st.session_state.delete_idx = None
        st.experimental_rerun()

st.write("---")

st.subheader("Datos finales (diccionario)")
datos_finales = {
    "imagenes": [
        {
            "nombre": img["nombre"],
            "comentario": img["comentario"]
        }
        for img in st.session_state.imagenes
    ]
}


if st.button("Guardar datos", key="guardar_datos_bloque_7"):
    st.write(datos_finales)
    if datos_finales["imagenes"]:
        st.session_state.bloque_7 = datos_finales
    else:
        st.session_state.bloque_7 = {"imagenes": [{"nombre": "default", "comentario": "default"}]}
    st.success("Datos guardados exitosamente.")


discontinuidades = [
    "CIR: Cordón irregular",
    "FP: Falta de Fusión",
    "SF: Socavado",
    "ExP: Exceso de Penetración",
    "P: Poro",
    "S: Salpicado Externo",
    "ER: Escoria Remanente",
    "R: Reparable",
    "NC: No Conforme"
]

if "tabla_datos" not in st.session_state:
    st.session_state.tabla_datos = []

if "delete_idx" not in st.session_state:
    st.session_state.delete_idx = None

def agregar_fila():
    nuevo_item = len(st.session_state.tabla_datos) + 1
    nueva_fila = {
        "ITEM": str(nuevo_item),
        "ELEMENTO": "",
        "INDICACION": "",
        "CAL": discontinuidades[0],
        "OBSERVACIONES": ""
    }
    st.session_state.tabla_datos.append(nueva_fila)

st.title("Inspección y Evaluación de Resultados")
st.write("## Tabla de Soldaduras")

if st.button("Agregar Fila"):
    agregar_fila()

cabeceras = st.columns([1, 3, 2, 4, 4, 2])
cabeceras[0].markdown("**ITEM**")
cabeceras[1].markdown("**ELEMENTO**")
cabeceras[2].markdown("**INDICACIÓN**")
cabeceras[3].markdown("**CAL**")
cabeceras[4].markdown("**OBSERVACIONES**")
cabeceras[5].markdown("**ACCIONES**")

for i, fila in enumerate(st.session_state.tabla_datos):
    c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 4, 4, 2])
    
    st.session_state.tabla_datos[i]["ITEM"] = c1.text_input(
        label="",
        value=fila["ITEM"],
        key=f"item_{i}"
    )
    
    st.session_state.tabla_datos[i]["ELEMENTO"] = c2.text_input(
        label="",
        value=fila["ELEMENTO"],
        key=f"elemento_{i}"
    )

    st.session_state.tabla_datos[i]["INDICACION"] = c3.text_input(
        label="",
        value=fila["INDICACION"],
        key=f"indicacion_{i}"
    )
    
    st.session_state.tabla_datos[i]["CAL"] = c4.selectbox(
        label="",
        options=discontinuidades,
        index=discontinuidades.index(fila["CAL"]) if fila["CAL"] in discontinuidades else 0,
        key=f"cal_{i}"
    )
    
    st.session_state.tabla_datos[i]["OBSERVACIONES"] = c5.text_input(
        label="",
        value=fila["OBSERVACIONES"],
        key=f"obs_{i}"
    )
    
    if c6.button("Eliminar", key=f"eliminar_{i}"):
        st.session_state.delete_idx = i

if st.session_state.delete_idx is not None:
    st.session_state.tabla_datos.pop(st.session_state.delete_idx)
    st.session_state.delete_idx = None

st.write("---")

observaciones_generales = st.text_area("Observaciones Generales", "")
st.write("**Texto ingresado:**", observaciones_generales)

if st.button("Guardar Datos", key="guardar_datos_bloque_8"):
    st.write("### Datos guardados correctamente")
    st.session_state.bloque_8 = {
       "tabla": st.session_state.tabla_datos,
       "observaciones_generales": observaciones_generales
    }


if "imagenes" not in st.session_state:
    st.session_state.imagenes = []

if "delete_idx" not in st.session_state:
    st.session_state.delete_idx = None

st.title("Registro fotográfico")

st.subheader("Cargar nuevas imágenes")
uploaded_files = st.file_uploader(
    "Selecciona una o varias imágenes",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="file_uploader_bloque_9"  # Add a unique key
)

if st.button("Agregar Imágenes", key="agregar_imagenes_bloque_9"):  # Add a unique key
    if uploaded_files:
        for file in uploaded_files:
            nueva_imagen = {
                "archivo": file,
                "nombre": file.name,
                "comentario": ""
            }
            st.session_state.imagenes.append(nueva_imagen)
    else:
        st.warning("No has seleccionado ningún archivo.")

st.write("---")

st.subheader("Imágenes cargadas")
if len(st.session_state.imagenes) == 0:
    st.info("No hay imágenes cargadas todavía.")
else:
    for i, img_info in enumerate(st.session_state.imagenes):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img_info["archivo"], use_container_width=True)
        
        with col2:
            st.write(f"**Archivo:** {img_info['nombre']}")
            nuevo_comentario = st.text_area(
                "Comentario",
                value=img_info["comentario"],
                key=f"comentario_{i}"
            )
            st.session_state.imagenes[i]["comentario"] = nuevo_comentario
            
            if st.button("Eliminar esta imagen", key=f"eliminar_{i}"):
                st.session_state.delete_idx = i

    if st.session_state.delete_idx is not None:
        st.session_state.imagenes.pop(st.session_state.delete_idx)
        st.session_state.delete_idx = None
        st.experimental_rerun()

st.write("---")

st.subheader("Datos finales (diccionario)")
datos_finales = {
    "imagenes": [
        {
            "nombre": img["nombre"],
            "comentario": img["comentario"]
        }
        for img in st.session_state.imagenes
    ]
}


if st.button("Guardar datos", key="guardar_datos_bloque_9"):
    st.write(datos_finales)
    st.session_state.bloque_9 = datos_finales
    st.success("Datos guardados exitosamente.")


