import streamlit as st
import pandas as pd
import os
from utils import (
    cargar_kits, get_norma_global, get_material_base,
    get_kits_disponibles, get_componentes_kit, materiales_base,
    get_proceso_soldadura, get_tipo_soldadura,
    get_materiales_base_seleccionados, get_procesos_soldadura_seleccionados,
    get_tipos_soldadura_seleccionados, procesos_soldadura, tipos_soldadura,
    get_esquema_elementos_global
)

st.set_page_config(
    page_title="4 Datos de Inspección de Partículas Magnéticas",
    page_icon="🧲",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧲 4 Datos de Inspección de Partículas Magnéticas")

# Obtener la norma global
norma_global = get_norma_global()
st.markdown(f"**Norma global:** {norma_global}")

# Mostrar información heredada del módulo de inspección visual
st.subheader("📋 Información Heredada del Módulo de Inspección Visual")

# Obtener materiales base seleccionados
materiales_seleccionados = get_materiales_base_seleccionados()
procesos_seleccionados = get_procesos_soldadura_seleccionados()
tipos_seleccionados = get_tipos_soldadura_seleccionados()

# Mostrar información heredada
if materiales_seleccionados:
    st.success(f"**Materiales Base:** {', '.join(materiales_seleccionados)}")
else:
    st.warning("No hay materiales base seleccionados en el módulo de inspección visual")

if procesos_seleccionados:
    st.success(f"**Procesos de Soldadura:** {', '.join(procesos_seleccionados)}")
else:
    st.warning("No hay procesos de soldadura seleccionados en el módulo de inspección visual")

if tipos_seleccionados:
    st.success(f"**Tipos de Soldadura:** {', '.join(tipos_seleccionados)}")
else:
    st.warning("No hay tipos de soldadura seleccionados en el módulo de inspección visual")

st.markdown("---")

# Selector múltiple de material base (heredado pero editable)
st.subheader("Especificación de Material Base")
st.markdown("Los materiales base se heredan del módulo de inspección visual. Puede modificarlos si es necesario:")

materiales_editados = st.multiselect(
    "ESPECIFICACIÓN MATERIAL BASE:",
    options=materiales_base,
    default=materiales_seleccionados,
    help="Selecciona una o más especificaciones del material base"
)

# Guardar en session_state
st.session_state.materiales_base_seleccionados = materiales_editados

# Mostrar materiales seleccionados
if materiales_editados:
    st.success(f"Materiales seleccionados: {', '.join(materiales_editados)}")
else:
    st.warning("No se han seleccionado materiales base")

# Sección 1: Información General
st.subheader("Información General")

# Procedimiento editable para Partículas Magnéticas
procedimiento_default = "TLPR0027 - Inspección de Partículas Magnéticas - Rev. 1"

# Inicializar procedimiento en session_state si no existe
if "procedimiento_pm" not in st.session_state:
    st.session_state.procedimiento_pm = procedimiento_default

procedimiento = st.text_input("PROCEDIMIENTO:", value=st.session_state.procedimiento_pm, help="Procedimiento utilizado para la inspección de partículas magnéticas")

# Actualizar session_state cuando cambie
st.session_state.procedimiento_pm = procedimiento

# Mostrar procesos de soldadura heredados
st.markdown("**Procesos de Soldadura Heredados:**")
if procesos_seleccionados:
    st.success(f"{', '.join(procesos_seleccionados)}")
else:
    st.warning("No hay procesos de soldadura seleccionados")

st.markdown("**Tipos de Soldadura Heredados:**")
if tipos_seleccionados:
    st.success(f"{', '.join(tipos_seleccionados)}")
else:
    st.warning("No hay tipos de soldadura seleccionados")

# Opción para editar procesos de soldadura si es necesario
with st.expander("✏️ Editar Procesos de Soldadura (opcional)"):
    st.markdown("Puede modificar los procesos de soldadura si es necesario:")
    
    col_proc, col_tipo = st.columns(2)
    with col_proc:
        procesos_editados = st.multiselect(
            "Procesos de soldadura:",
            options=procesos_soldadura,
            default=procesos_seleccionados,
            help="Selecciona uno o más procesos de soldadura"
        )
        st.session_state.procesos_soldadura_seleccionados = procesos_editados

    with col_tipo:
        tipos_editados = st.multiselect(
            "Tipos de soldadura:",
            options=tipos_soldadura,
            default=tipos_seleccionados,
            help="Selecciona uno o más tipos de soldadura"
        )
        st.session_state.tipos_soldadura_seleccionados = tipos_editados

    # Mostrar selecciones editadas
    if procesos_editados:
        st.success(f"Procesos seleccionados: {', '.join(procesos_editados)}")
    if tipos_editados:
        st.success(f"Tipos seleccionados: {', '.join(tipos_editados)}")

# Cargar y filtrar kits
kits = cargar_kits()
kits_disponibles = get_kits_disponibles("MT")
opciones_kits = [f"{kit['nombre']} - {kit['descripcion']}" for kit in kits_disponibles]

kit_seleccionado = st.selectbox(
    "EQUIPOS UTILIZADOS:",
    options=opciones_kits,
    help="Selecciona el kit necesario para la inspección"
)

if kit_seleccionado:
    componentes = get_componentes_kit(kit_seleccionado, kits_disponibles)
    if componentes:
        componentes_texto = ", ".join(componentes)
        kit = next((k for k in kits_disponibles if f"{k['nombre']} - {k['descripcion']}" == kit_seleccionado), None)
        if kit:
            st.write(f"**{kit['nombre']}:** {componentes_texto}")

# Sección 2: Materiales Utilizados
st.subheader("3. Materiales Utilizados")

materiales_mt_data = {
    "PARTICULAS MAGNETICAS": { "Met-L-Check": ["MPI-80"], },
    "PINTURA DE CONTRASTE": { "Met-L-Check": ["WCP-81"], }
}

if "materiales_utilizados_mt" not in st.session_state:
    st.session_state.materiales_utilizados_mt = {
        "PARTICULAS MAGNETICAS": {"fabricante": "Met-L-Check", "referencia": "MPI-80", "lote": ""},
        "PINTURA DE CONTRASTE": {"fabricante": "Met-L-Check", "referencia": "WCP-81", "lote": ""},
    }

materiales_values = st.session_state.materiales_utilizados_mt
c1, c2, c3, c4 = st.columns(4)
c1.markdown("**DETALLES**")
c2.markdown("**FABRICANTE**")
c3.markdown("**REF. COMERCIAL**")
c4.markdown("**LOTE N°**")

for detalle, values in materiales_values.items():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.write(f"**{detalle}**")
    with c2:
        fabricantes = list(materiales_mt_data[detalle].keys())
        fab_idx = fabricantes.index(values["fabricante"]) if values["fabricante"] in fabricantes else 0
        values["fabricante"] = st.selectbox(f"fab_{detalle}", fabricantes, index=fab_idx, label_visibility="collapsed", key=f"fab_mt_{detalle}")
    with c3:
        referencias = materiales_mt_data[detalle].get(values["fabricante"], [])
        ref_idx = referencias.index(values["referencia"]) if values["referencia"] in referencias else 0
        values["referencia"] = st.selectbox(f"ref_{detalle}", referencias, index=ref_idx, label_visibility="collapsed", key=f"ref_mt_{detalle}")
    with c4:
        values["lote"] = st.text_input(f"lote_{detalle}", value=values["lote"], label_visibility="collapsed", key=f"lote_mt_{detalle}")


# Sección 4.1: Tipo y Método
st.subheader("4.1 Tipo y Método")
if "tipo_metodo_mt" not in st.session_state:
    st.session_state.tipo_metodo_mt = { "tipo": "Wet Magnetic Particles", "metodo": "No fluorescente" }
tipo_metodo_values = st.session_state.tipo_metodo_mt
col1, col2 = st.columns(2)
with col1:
    tipo_options = ["Wet Magnetic Particles", "Dry Magnetic Particles"]
    tipo_idx = tipo_options.index(tipo_metodo_values["tipo"]) if tipo_metodo_values["tipo"] in tipo_options else 0
    tipo_metodo_values["tipo"] = st.selectbox("TIPO:", tipo_options, index=tipo_idx)
with col2:
    metodo_options = ["No fluorescente", "Fluorescente"]
    metodo_idx = metodo_options.index(tipo_metodo_values["metodo"]) if tipo_metodo_values["metodo"] in metodo_options else 0
    tipo_metodo_values["metodo"] = st.selectbox("MÉTODO:", metodo_options, index=metodo_idx)

# Sección 5: Parámetros de Operación
st.subheader("5. Parámetros de Operación")
if "parametros_operacion_mt" not in st.session_state:
    st.session_state.parametros_operacion_mt = [
        {"actividad": "Yugo", "distancia": "150 mm", "aplicacion": "N.A.", "iluminacion": "N.A."},
        {"actividad": "Partículas", "distancia": "20 mm", "aplicacion": "Spray", "iluminacion": "No Fluorescente"},
    ]
c1, c2, c3, c4 = st.columns(4)
c1.markdown("**ACTIVIDAD**")
c2.markdown("**DISTANCIA**")
c3.markdown("**APLICACIÓN**")
c4.markdown("**ILUMINACIÓN**")
for i, param in enumerate(st.session_state.parametros_operacion_mt):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.write(param["actividad"])
    with c2:
        param["distancia"] = st.text_input(f"distancia_mt_{i}", value=param["distancia"], label_visibility="collapsed")
    with c3:
        param["aplicacion"] = st.text_input(f"aplicacion_mt_{i}", value=param["aplicacion"], label_visibility="collapsed")
    with c4:
        param["iluminacion"] = st.text_input(f"iluminacion_mt_{i}", value=param["iluminacion"], label_visibility="collapsed")

# Sección 6 & 7: Proceso y Corriente de Magnetización
st.subheader("6. Proceso de Magnetización y 7. Corriente de Magnetización")
if "proceso_corriente_mt" not in st.session_state:
    st.session_state.proceso_corriente_mt = { "proceso": "Continua", "corriente": "AC" }
proceso_corriente_values = st.session_state.proceso_corriente_mt
col1, col2 = st.columns(2)
with col1:
    proceso_options = ["Continua", "Residual"]
    proceso_idx = proceso_options.index(proceso_corriente_values["proceso"]) if proceso_corriente_values["proceso"] in proceso_options else 0
    proceso_corriente_values["proceso"] = st.selectbox("PROCESO DE MAGNETIZACIÓN:", proceso_options, index=proceso_idx)
with col2:
    corriente_options = ["AC", "DC", "HWDC"]
    corriente_idx = corriente_options.index(proceso_corriente_values["corriente"]) if proceso_corriente_values["corriente"] in corriente_options else 0
    proceso_corriente_values["corriente"] = st.selectbox("CORRIENTE DE MAGNETIZACIÓN:", corriente_options, index=corriente_idx)

# Sección 8: Elementos Inspeccionados
st.subheader("Elementos Inspeccionados")

# Inicializar elementos del módulo actual
elementos_key = "tabla_elementos_4_1"
if elementos_key not in st.session_state:
    # Heredar elementos de inspección visual si existen
    if "tabla_elementos_2_1" in st.session_state and st.session_state.tabla_elementos_2_1:
        # Copiar elementos de inspección visual (herencia inicial)
        st.session_state[elementos_key] = []
        for elemento in st.session_state.tabla_elementos_2_1:
            # Crear una copia independiente del elemento
            elemento_copia = {
                "numero": elemento["numero"],
                "descripcion": elemento["descripcion"],
                "indicacion": elemento["indicacion"],
                "calificacion": "Satisfactorio",  # Valor por defecto para partículas magnéticas
                "observacion": elemento["observacion"]
            }
            st.session_state[elementos_key].append(elemento_copia)
        st.success(f"✅ Elementos heredados de Inspección Visual: {len(st.session_state[elementos_key])} elementos")
    else:
        # Si no hay elementos en inspección visual, inicializar lista vacía
        st.session_state[elementos_key] = []
        st.info("💡 No hay elementos en Inspección Visual para heredar. Puedes agregar elementos manualmente.")

# Función para agregar una nueva fila
def agregar_fila_elemento_mt():
    nuevo_numero = len(st.session_state[elementos_key]) + 1
    nueva_fila = {
        "numero": str(nuevo_numero),
        "descripcion": "",
        "indicacion": "",
        "calificacion": "Satisfactorio",
        "observacion": ""
    }
    st.session_state[elementos_key].append(nueva_fila)

# Botones para gestionar elementos
col1, col2 = st.columns(2)
with col1:
    if st.button("Agregar Elemento", key="agregar_elemento_mt"):
        agregar_fila_elemento_mt()

with col2:
    if st.button("Re-heredar de Inspección Visual", key="reheredar_elementos_mt"):
        if "tabla_elementos_2_1" in st.session_state and st.session_state.tabla_elementos_2_1:
            # Limpiar elementos actuales y re-heredar
            st.session_state[elementos_key] = []
            for elemento in st.session_state.tabla_elementos_2_1:
                elemento_copia = {
                    "numero": elemento["numero"],
                    "descripcion": elemento["descripcion"],
                    "indicacion": elemento["indicacion"],
                    "calificacion": "Satisfactorio",
                    "observacion": elemento["observacion"]
                }
                st.session_state[elementos_key].append(elemento_copia)
            st.success(f"✅ Elementos actualizados desde Inspección Visual: {len(st.session_state[elementos_key])} elementos")
            st.rerun()
        else:
            st.warning("⚠️ No hay elementos en Inspección Visual para heredar.")

# Opciones para la calificación
opciones_calificacion = ["Satisfactorio", "No Satisfactorio", "Fuera de Alcance"]

# Crear la tabla de elementos
if st.session_state[elementos_key]:
    # Encabezados de la tabla
    col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 3])
    col1.markdown("**No.**")
    col2.markdown("**Descripción del Elemento**")
    col3.markdown("**Indicación**")
    col4.markdown("**Calificación**")
    col5.markdown("**Observación**")

    # Filas de la tabla
    for i, elemento in enumerate(st.session_state[elementos_key]):
        c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 3])
        
        # Número (solo lectura)
        c1.write(elemento["numero"])
        
        # Descripción (editable)
        st.session_state[elementos_key][i]["descripcion"] = c2.text_input(
            f"Descripción del elemento {elemento['numero']}",
            value=elemento["descripcion"],
            key=f"elem_desc_4_1_{i}",
            label_visibility="collapsed"
        )
        
        # Indicación (editable)
        st.session_state[elementos_key][i]["indicacion"] = c3.text_input(
            f"Indicación del elemento {elemento['numero']}",
            value=elemento["indicacion"],
            key=f"elem_ind_4_1_{i}",
            label_visibility="collapsed"
        )
        
        # Calificación (editable)
        calificacion_actual = elemento["calificacion"]
        try:
            index_calificacion = opciones_calificacion.index(calificacion_actual)
        except ValueError:
            # Si el valor no está en la lista, usar el primer valor por defecto
            index_calificacion = 0
            calificacion_actual = opciones_calificacion[0]
        
        st.session_state[elementos_key][i]["calificacion"] = c4.selectbox(
            f"Calificación del elemento {elemento['numero']}",
            options=opciones_calificacion,
            index=index_calificacion,
            key=f"elem_cal_4_1_{i}",
            label_visibility="collapsed"
        )
        
        # Observación (editable)
        st.session_state[elementos_key][i]["observacion"] = c5.text_area(
            f"Observación del elemento {elemento['numero']}",
            value=elemento["observacion"],
            key=f"elem_obs_4_1_{i}",
            height=70,
            label_visibility="collapsed"
        )
        
        # Botón para eliminar fila
        if c5.button("Eliminar", key=f"elem_eliminar_4_1_{i}"):
            st.session_state[elementos_key].pop(i)
            st.rerun()
else:
    st.info("No hay elementos inspeccionados. Use el botón 'Agregar Elemento' para comenzar.")

# Sección 9: Esquema y Detalles
st.subheader("Esquema y Detalles")

# Inicializar esquema del módulo actual
esquema_key = "esquema_4_1"
if esquema_key not in st.session_state:
    # Heredar esquema de inspección visual si existe
    esquema_global_original = get_esquema_elementos_global()
    if esquema_global_original:
        # Copiar esquema de inspección visual (herencia inicial)
        st.session_state[esquema_key] = []
        for img_info in esquema_global_original:
            # Crear una copia independiente de la imagen
            img_copia = {
                "archivo": img_info["archivo"],
                "nombre": img_info["nombre"],
                "comentario": img_info["comentario"]
            }
            st.session_state[esquema_key].append(img_copia)
        st.success(f"✅ Esquema heredado de Inspección Visual: {len(st.session_state[esquema_key])} imágenes")
    else:
        # Si no hay esquema en inspección visual, inicializar lista vacía
        st.session_state[esquema_key] = []
        st.info("💡 No hay esquema en Inspección Visual para heredar. Puedes agregar imágenes manualmente.")

# Cargar nuevas imágenes del esquema
uploaded_files_esquema = st.file_uploader(
    "Selecciona las imágenes del esquema de inspección (puedes subir múltiples)",
    type=["png", "jpg", "jpeg"],
    key="upload_esquema_mt",
    accept_multiple_files=True
)

if uploaded_files_esquema:
    if st.button("Agregar Imágenes al Esquema", key="agregar_esquema_mt"):
        for file in uploaded_files_esquema:
            nueva_imagen = {
                "archivo": file,
                "nombre": file.name,
                "comentario": ""
            }
            st.session_state[esquema_key].append(nueva_imagen)
        st.success(f"Se agregaron {len(uploaded_files_esquema)} imágenes al esquema")
        st.rerun()
    else:
        st.warning("No has seleccionado ningún archivo.")

# Botones para gestionar esquema
col1, col2 = st.columns(2)
with col1:
    if st.button("Re-heredar de Inspección Visual", key="reheredar_esquema_mt"):
        esquema_global_original = get_esquema_elementos_global()
        if esquema_global_original:
            # Limpiar esquema actual y re-heredar
            st.session_state[esquema_key] = []
            for img_info in esquema_global_original:
                img_copia = {
                    "archivo": img_info["archivo"],
                    "nombre": img_info["nombre"],
                    "comentario": img_info["comentario"]
                }
                st.session_state[esquema_key].append(img_copia)
            st.success(f"✅ Esquema actualizado desde Inspección Visual: {len(st.session_state[esquema_key])} imágenes")
            st.rerun()
        else:
            st.warning("⚠️ No hay esquema en Inspección Visual para heredar.")

with col2:
    if st.button("Limpiar Esquema", key="limpiar_esquema_mt"):
        st.session_state[esquema_key] = []
        st.success("✅ Esquema limpiado")
        st.rerun()

# Mostrar las imágenes del esquema
if len(st.session_state[esquema_key]) == 0:
    st.info("No hay esquema cargado todavía. Sube imágenes o hereda desde Inspección Visual.")
else:
    st.success(f"✅ Esquema de Partículas Magnéticas: {len(st.session_state[esquema_key])} imágenes cargadas")
    st.info("💡 Este esquema es independiente del módulo de Inspección Visual.")
    
    for i, img_info in enumerate(st.session_state[esquema_key]):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img_info["archivo"], use_container_width=True)
        
        with col2:
            st.write(f"**Archivo:** {img_info['nombre']}")
            nuevo_comentario = st.text_area(
                "Comentario",
                value=img_info["comentario"],
                key=f"comentario_esquema_mt_{i}"
            )
            st.session_state[esquema_key][i]["comentario"] = nuevo_comentario
            
            if st.button("Eliminar imagen", key=f"eliminar_esquema_mt_{i}"):
                st.session_state[esquema_key].pop(i)
                st.rerun()

detalle_resultados = st.text_area("DETALLE DE ELEMENTOS INSPECCIONADOS Y RESULTADOS:", "")

# Sección 10: Observaciones y Registros
st.subheader("Observaciones y Registros")
observaciones_generales = st.text_area("OBSERVACIONES GENERALES:", "")

# Sección 11: Registros Fotográficos
st.subheader("Registros Fotográficos")

if "imagenes_4_1" not in st.session_state:
    st.session_state.imagenes_4_1 = []

if "delete_idx_4_1" not in st.session_state:
    st.session_state.delete_idx_4_1 = None

st.subheader("Cargar nuevas imágenes")
uploaded_files = st.file_uploader(
    "Selecciona una o varias imágenes",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if st.button("Agregar Imágenes", key="agregar_imagenes_mt"):
    if uploaded_files:
        for file in uploaded_files:
            nueva_imagen = {
                "archivo": file,
                "nombre": file.name,
                "comentario": ""
            }
            st.session_state.imagenes_4_1.append(nueva_imagen)
    else:
        st.warning("No has seleccionado ningún archivo.")

st.write("---")

st.subheader("Imágenes cargadas")
if len(st.session_state.imagenes_4_1) == 0:
    st.info("No hay imágenes cargadas todavía.")
else:
    for i, img_info in enumerate(st.session_state.imagenes_4_1):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img_info["archivo"], use_container_width=True)
        
        with col2:
            st.write(f"**Archivo:** {img_info['nombre']}")
            nuevo_comentario = st.text_area(
                "Comentario",
                value=img_info["comentario"],
                key=f"comentario_4_1_{i}"
            )
            st.session_state.imagenes_4_1[i]["comentario"] = nuevo_comentario
            
            if st.button("Eliminar esta imagen", key=f"eliminar_4_1_{i}"):
                st.session_state.delete_idx_4_1 = i

    if st.session_state.delete_idx_4_1 is not None:
        st.session_state.imagenes_4_1.pop(st.session_state.delete_idx_4_1)
        st.session_state.delete_idx_4_1 = None
        st.rerun()

st.write("---")

st.subheader("Datos finales (diccionario)")
datos_finales = {
    "imagenes": [
        {
            "nombre": img["nombre"],
            "comentario": img["comentario"]
        }
        for img in st.session_state.imagenes_4_1
    ]
}

if st.button("Guardar Datos", key="guardar_datos_mt"):
    st.write("### Datos guardados correctamente")
    
    st.session_state.bloque_4_1 = {
        "norma": norma_global,
        "procedimiento": procedimiento,
        "equipos": kit_seleccionado,
        "material_base": materiales_editados,
        "proceso_soldadura": procesos_editados,
        "materiales_utilizados": st.session_state.materiales_utilizados_mt,
        "tipo_y_metodo": st.session_state.tipo_metodo_mt,
        "parametros_operacion": st.session_state.parametros_operacion_mt,
        "proceso_y_corriente": st.session_state.proceso_corriente_mt,
        "elementos_inspeccionados": st.session_state[elementos_key],
        "esquema_elementos": st.session_state[esquema_key],
        "detalle_resultados": detalle_resultados,
        "observaciones_generales": observaciones_generales,
        "registros_fotograficos": datos_finales["imagenes"]
    }
    st.rerun() 