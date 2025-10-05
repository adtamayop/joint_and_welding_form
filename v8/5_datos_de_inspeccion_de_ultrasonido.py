import streamlit as st
import pandas as pd
import os
from utils import (
    cargar_kits, get_norma_global, get_material_base,
    get_kits_disponibles, get_componentes_kit, materiales_base,
    get_proceso_soldadura, get_tipo_soldadura, get_tipo_inspeccion,
    get_materiales_base_seleccionados, get_procesos_soldadura_seleccionados,
    get_tipos_soldadura_seleccionados, procesos_soldadura, tipos_soldadura,
    get_esquema_elementos_global, get_datos_palpador
)

st.set_page_config(
    page_title="5 Inspección de Ultrasonido",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔊 5 Datos de Inspección de Ultrasonido")

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

# Procedimiento editable para Ultrasonido
procedimiento_default = "TLPR0028 - Inspección de Ultrasonido - Rev. 1"

# Inicializar procedimiento en session_state si no existe
if "procedimiento_ut" not in st.session_state:
    st.session_state.procedimiento_ut = procedimiento_default

procedimiento = st.text_input("PROCEDIMIENTO:", value=st.session_state.procedimiento_ut, help="Procedimiento utilizado para la inspección de ultrasonido")

# Actualizar session_state cuando cambie
st.session_state.procedimiento_ut = procedimiento

# Determinar el tipo de inspección basado en el procedimiento
tipo_inspeccion = get_tipo_inspeccion(procedimiento)

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
kits_disponibles = get_kits_disponibles(tipo_inspeccion) if tipo_inspeccion else []
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
            
            # Mostrar información específica del equipo de ultrasonido
            if kit['id'] == 'kit_ut' and kit.get('marca'):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Marca:** {kit.get('marca', 'N/A')}")
                    st.write(f"**Modelo:** {kit.get('modelo', 'N/A')}")
                with col2:
                    st.write(f"**Escala:** {kit.get('escala', 'N/A')}")
                    st.write(f"**Grado Calibración (dB):** {kit.get('grado_calibracion', 'N/A')}")

# --- PALPADOR ---
st.markdown("##### Palpador, Tipo y Método de Inspección")

# Obtener datos del palpador desde el kit seleccionado
datos_palpador = get_datos_palpador(kit_seleccionado, kits_disponibles)

if datos_palpador:
    # Mostrar información del palpador cargada desde CSV
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write(f"**Tipo de Palpador:** {datos_palpador['tipo']}")
    
    with col2:
        st.write(f"**Ángulo:** {datos_palpador['angulo']}°")
    
    with col3:
        # Solo la frecuencia es editable
        frecuencia_actual = float(datos_palpador['frecuencia']) if datos_palpador['frecuencia'] else 2.25
        opciones_frecuencia = [1.0, 1.5, 2.0, 2.25, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
        
        # Inicializar frecuencia en session_state si no existe
        if "palpador_frecuencia_editada" not in st.session_state:
            st.session_state.palpador_frecuencia_editada = frecuencia_actual
        
        frecuencia_seleccionada = st.selectbox(
            "**Frecuencia (MHz):**",
            options=opciones_frecuencia,
            index=opciones_frecuencia.index(st.session_state.palpador_frecuencia_editada) if st.session_state.palpador_frecuencia_editada in opciones_frecuencia else 3,
            help="Frecuencia del palpador en MHz (1.0 a 6.0 MHz, incrementos de 0.5)"
        )
        st.session_state.palpador_frecuencia_editada = frecuencia_seleccionada
    
    with col4:
        st.write(f"**Dimensión:** {datos_palpador['dimension']}")
    
    # Construir string para guardar
    palpador = (
        f"Tipo: {datos_palpador['tipo']}\n"
        f"Ángulo: {datos_palpador['angulo']}°\n"
        f"Frecuencia: {frecuencia_seleccionada} MHz\n"
        f"Dimensión: {datos_palpador['dimension']}"
    )
    
else:
    st.warning("⚠️ No se encontraron datos del palpador en el kit seleccionado.")
    palpador = "Datos del palpador no disponibles"

# Sección 2: Materiales y Procedimientos
st.subheader("Materiales y Procedimientos")

# 2.1 Tipo de inspección por ultrasonido
tipo_opciones = ["Haz recto (Solo para palpador recto)", "Haz angular (Solo para palpador angular)"]
tipo = st.selectbox("TIPO DE INSPECCIÓN POR ULTRASONIDO:", tipo_opciones, help="Selecciona el tipo de inspección según el palpador utilizado")

# 2.2 Método
metodo_opciones = ["A-scan", "B-scan"]
metodo = st.selectbox("MÉTODO:", metodo_opciones, help="Selecciona el método de inspección")

# 2.3 Soldadura
soldadura = st.text_area(
    "SOLDADURA:",
    """Proceso: SMAW
Paso 4xe: 4.0
Medio paso P/2: 2.0
11xe rango 111: 11.0""",
    help="Datos de la soldadura: proceso, paso 4xe, medio paso P/2, 11xe rango 111"
)

# 2.4 Materiales
materiales = st.text_area(
    "MATERIALES:",
    """Material base: A36
Espesor de m. base 11: 12.7 mm
Material de aporte: E7018
Acoplante: CMC""",
    help="Materiales utilizados: material base, espesor, material de aporte, acoplante"
)

procedimiento = st.text_area(
    "PROCEDIMIENTO:",
    """1. Limpieza de la superficie con método manual (con paño).
2. Aplicación de limpiador.
3. Aplicación de acoplante (tiempo de exposición: 10:00 min).
4. Limpieza de acoplante.
5. Aplicación de revelador (tiempo de revelado: 10:00 min).
6. Limpieza final."""
)

# Sección 3: Parámetros de Operación
st.subheader("Parámetros de Operación")
parametros = st.text_area(
    "PARÁMETROS DE OPERACIÓN:",
    """LIMPIEZA: 5:00 min
ACOPLANTE: 12:00 min
REVELADOR: 3:00 min
TEMPERATURA: 26° C
APLICACIÓN: Spray
ILUMINACIÓN: Luz Natural"""
)

# Sección 4: Elementos Inspeccionados
st.subheader("Elementos Inspeccionados")

# Inicializar elementos del módulo actual
elementos_key = "tabla_elementos_5_1"
if elementos_key not in st.session_state:
    st.session_state[elementos_key] = []

# Función para agregar una nueva fila
def agregar_fila_elemento_ut():
    nuevo_numero = len(st.session_state[elementos_key]) + 1
    nueva_fila = {
        "numero": str(nuevo_numero),
        "descripcion_junta": "",
        "numero_junta": "",
        "ubicacion_junta": "",
        "estampe": "",
        "decibeles_a": "",
        "decibeles_b": "",
        "decibeles_c": "",
        "decibeles_d": "",
        "discontinuidad_distancia_angular": "",
        "discontinuidad_profundidad": "",
        "discontinuidad_distancia_eje_y": "",
        "discontinuidad_distancia_eje_x": "",
        "evaluacion_junta": "Satisfactorio"
    }
    st.session_state[elementos_key].append(nueva_fila)

# Botón para agregar fila
if st.button("Agregar Elemento", key="agregar_elemento_ut"):
    agregar_fila_elemento_ut()

# Opciones para la evaluación de la junta
opciones_evaluacion = ["Satisfactorio", "No Satisfactorio", "Fuera de Alcance"]

# Crear la tabla de elementos
if st.session_state[elementos_key]:
    st.markdown("### Tabla de Elementos Inspeccionados por Ultrasonido")
    
    # Filas de la tabla - cada elemento es una sección completa
    for i, elemento in enumerate(st.session_state[elementos_key]):
        # Contenedor para cada elemento con borde visual
        with st.container():
            st.markdown(f"#### 🔍 Elemento #{elemento['numero']}")
            
            # Información básica de la junta
            st.markdown("**📋 Información Básica de la Junta**")
            col1, col2, col3, col4 = st.columns([2, 1, 2, 2])
            
            with col1:
                st.session_state[elementos_key][i]["descripcion_junta"] = st.text_input(
                    "Descripción de la Junta",
                    value=elemento["descripcion_junta"],
                    key=f"elem_desc_junta_5_1_{i}",
                    help="Descripción detallada de la junta inspeccionada"
                )
            
            with col2:
                st.session_state[elementos_key][i]["numero_junta"] = st.text_input(
                    "# de Junta",
                    value=elemento["numero_junta"],
                    key=f"elem_num_junta_5_1_{i}",
                    help="Número identificador de la junta"
                )
            
            with col3:
                st.session_state[elementos_key][i]["ubicacion_junta"] = st.text_input(
                    "Ubicación de la Junta",
                    value=elemento["ubicacion_junta"],
                    key=f"elem_ubic_junta_5_1_{i}",
                    help="Ubicación física de la junta en el componente"
                )
            
            with col4:
                st.session_state[elementos_key][i]["estampe"] = st.text_input(
                    "Estampe",
                    value=elemento["estampe"],
                    key=f"elem_estampe_5_1_{i}",
                    help="Estampe o marca identificadora"
                )
            
            # Calificación de decibeles
            st.markdown("**🔊 Calificación de Decibeles**")
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.session_state[elementos_key][i]["decibeles_a"] = st.text_input(
                    "Decibeles A",
                    value=elemento["decibeles_a"],
                    key=f"elem_db_a_5_1_{i}",
                    help="Valor en decibeles para calificación A"
                )
            
            with col6:
                st.session_state[elementos_key][i]["decibeles_b"] = st.text_input(
                    "Decibeles B",
                    value=elemento["decibeles_b"],
                    key=f"elem_db_b_5_1_{i}",
                    help="Valor en decibeles para calificación B"
                )
            
            with col7:
                st.session_state[elementos_key][i]["decibeles_c"] = st.text_input(
                    "Decibeles C",
                    value=elemento["decibeles_c"],
                    key=f"elem_db_c_5_1_{i}",
                    help="Valor en decibeles para calificación C"
                )
            
            with col8:
                st.session_state[elementos_key][i]["decibeles_d"] = st.text_input(
                    "Decibeles D",
                    value=elemento["decibeles_d"],
                    key=f"elem_db_d_5_1_{i}",
                    help="Valor en decibeles para calificación D"
                )
            
            # Discontinuidad
            st.markdown("**📏 Discontinuidad**")
            col9, col10, col11, col12 = st.columns(4)
            
            with col9:
                st.session_state[elementos_key][i]["discontinuidad_distancia_angular"] = st.text_input(
                    "Distancia Angular",
                    value=elemento["discontinuidad_distancia_angular"],
                    key=f"elem_dist_ang_5_1_{i}",
                    help="Distancia angular de la discontinuidad"
                )
            
            with col10:
                st.session_state[elementos_key][i]["discontinuidad_profundidad"] = st.text_input(
                    "Profundidad",
                    value=elemento["discontinuidad_profundidad"],
                    key=f"elem_prof_5_1_{i}",
                    help="Profundidad de la discontinuidad"
                )
            
            with col11:
                st.session_state[elementos_key][i]["discontinuidad_distancia_eje_y"] = st.text_input(
                    "Distancia Eje Y",
                    value=elemento["discontinuidad_distancia_eje_y"],
                    key=f"elem_dist_y_5_1_{i}",
                    help="Distancia sobre el eje Y"
                )
            
            with col12:
                st.session_state[elementos_key][i]["discontinuidad_distancia_eje_x"] = st.text_input(
                    "Distancia Eje X",
                    value=elemento["discontinuidad_distancia_eje_x"],
                    key=f"elem_dist_x_5_1_{i}",
                    help="Distancia sobre el eje X"
                )
            
            # Evaluación y acción
            st.markdown("**✅ Evaluación**")
            col13, col14 = st.columns([3, 1])
            
            with col13:
                st.session_state[elementos_key][i]["evaluacion_junta"] = st.selectbox(
                    "Evaluación de la Junta",
                    options=opciones_evaluacion,
                    index=opciones_evaluacion.index(elemento["evaluacion_junta"]),
                    key=f"elem_eval_5_1_{i}",
                    help="Resultado de la evaluación de la junta"
                )
            
            with col14:
                st.markdown("")  # Espacio en blanco para alineación
                if st.button("🗑️ Eliminar Elemento", key=f"elem_eliminar_5_1_{i}", type="secondary"):
                    st.session_state[elementos_key].pop(i)
                    st.rerun()
            
            # Separador visual entre elementos
            st.markdown("---")
else:
    st.info("No hay elementos inspeccionados. Use el botón 'Agregar Elemento' para comenzar.")

juntas = st.number_input(
    "JUNTAS:",
    min_value=0,
    value=1,
    step=1,
    help="Cantidad de juntas en la inspección"
)

# Sección 5: Detalles y Esquema
st.subheader("Detalles y Esquema")

# Obtener el esquema global heredado
esquema_global = get_esquema_elementos_global()

if len(esquema_global) == 0:
    st.warning("⚠️ No hay esquema global cargado. Ve al módulo de Inspección Visual para subir imágenes del esquema.")
else:
    st.success(f"✅ Esquema Global Heredado: {len(esquema_global)} imágenes")
    st.info("💡 Este esquema se hereda automáticamente del módulo de Inspección Visual.")
    
    for i, img_info in enumerate(esquema_global):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img_info["archivo"], use_container_width=True)
        
        with col2:
            st.write(f"**Archivo:** {img_info['nombre']}")
            if img_info["comentario"]:
                st.write(f"**Comentario:** {img_info['comentario']}")
            else:
                st.write("**Comentario:** Sin comentario")

detalle_resultados = st.text_area("DETALLE DE ELEMENTOS INSPECCIONADOS Y RESULTADOS:", "")

# Sección 6: Observaciones
st.subheader("Observaciones")
observaciones_generales = st.text_area("OBSERVACIONES GENERALES:", "")

# Sección 7: Registros Fotográficos
st.subheader("Registros Fotográficos")

if "imagenes" not in st.session_state:
    st.session_state.imagenes = []

if "delete_idx" not in st.session_state:
    st.session_state.delete_idx = None

st.subheader("Cargar nuevas imágenes")
uploaded_files = st.file_uploader(
    "Selecciona una o varias imágenes",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if st.button("Agregar Imágenes", key="agregar_imagenes_ut"):
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
        st.rerun()

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

if st.button("Guardar Datos", key="guardar_datos_ut"):
    st.write("### Datos guardados correctamente")
    
    st.session_state.bloque_5_1 = {
        "equipo": kit_seleccionado,
        "palpador": palpador,
        "tipo_inspeccion": tipo,
        "metodo": metodo,
        "soldadura": soldadura,
        "materiales": materiales,
        "norma": norma_global,
        "procedimiento": procedimiento,
        "elementos_inspeccionados": st.session_state[elementos_key],
        "juntas": juntas,
        "detalle_resultados": detalle_resultados,
        "esquema_inspeccion": esquema_global,
        "observaciones_generales": observaciones_generales,
        "registros_fotograficos": datos_finales["imagenes"]
    } 