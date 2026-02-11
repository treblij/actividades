import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# ================= CONFIGURACIÓN =================
SHEET_ID = "1BihXG87fSsYxt2Ail1v805xwTStyL_4JOWbDPUp9ics"
ZONA_PERU = pytz.timezone("America/Lima")

st.set_page_config(page_title="Ficha de Actividades UT", layout="wide")

# ================= CONEXIÓN GOOGLE SHEETS =================
def conectar_sheet():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["connections"]["gsheets"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        st.stop()

# ================= CARGAR DATOS PERSONALES =================
@st.cache_data(ttl=300)
def cargar_datos_personales():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("DATOSPERSONALES")
    return sheet.get_all_records()

datos_personales = cargar_datos_personales()

# Diccionario UT -> Código -> Nombre
ut_dict = {}
for fila in datos_personales:
    ut = fila.get("UT", "").strip()
    codigo = fila.get("CODIGO  DE USUARIO", "").strip()
    nombre = fila.get("APELLIDOS Y NOMBRES", "").strip()

    if ut and codigo:
        if ut not in ut_dict:
            ut_dict[ut] = {}
        ut_dict[ut][codigo] = nombre

# ================= CONTROL FORMULARIO =================
if "form_id" not in st.session_state:
    st.session_state.form_id = 0

form_id = st.session_state.form_id

# 🔵 RESET cuando cambia la UT
def reset_codigo():
    codigo_key = f"codigo_{form_id}"
    if codigo_key in st.session_state:
        st.session_state[codigo_key] = ""

# ================= FORMULARIO =================
with st.form(key=f"form_{form_id}"):

    st.title("📋 Ficha de Registro de Actividades UT")

    col1, col2, col3, col4, col5 = st.columns(5)

    # ========= UT =========
    with col1:
        ut = st.selectbox(
            "UT",
            [""] + sorted(ut_dict.keys()),
            key=f"ut_{form_id}",
            on_change=reset_codigo
        )

    # ========= FECHA =========
    with col2:
        fecha = st.date_input(
            "Fecha",
            value=datetime.now(ZONA_PERU).date(),
            key=f"fecha_{form_id}"
        )

    # ========= CODIGO =========
    with col3:
        codigos = [""] + sorted(ut_dict.get(ut, {}).keys()) if ut else [""]
        codigo_usuario = st.selectbox(
            "Código de Usuario",
            codigos,
            key=f"codigo_{form_id}"
        )

    # ========= NOMBRES =========
    with col4:
        nombres = ""
        if ut and codigo_usuario:
            nombres = ut_dict[ut].get(codigo_usuario, "")
        st.text_input(
            "Apellidos y Nombres",
            value=nombres,
            disabled=True,
            key=f"nombres_{form_id}"
        )

    # ========= CARGO =========
    with col5:
        cargo = st.selectbox(
            "Cargo/Puesto",
            ["", "JEFE DE UNIDAD TERRITORIAL", "COORDINADOR TERRITORIAL","PROMOTOR",
             "TECNICO EN ATENCION AL USUARIO","ASISTENTE TECNICO EN SABERES PRODUCTIVOS",
             "AUXILIAR ADMINISTRATIVO","CONDUCTOR","TECNICO EN ATENCION DE PLATAFORMA",
             "ASISTENTE ADMINISTRATIVO","OTRO"],
            key=f"cargo_{form_id}"
        )

    # ================= ACTIVIDADES =================
    actividades = {
        "BIENESTAR": ["VACACIONES","ACTIVO","LICENCIA SINDICAL","EXAMEN MEDICO OCUPACIONAL",
                      "LICENCIA MEDICA","ONOMASTICO","DESCANSO FISICO POR COMPENSACION"],
        "VISITAS": ["VISITAS DOMICILIARIAS A USUARIOS REGULARES","BARRIDOS",
                    "VISITAS A USUARIOS CON EMPRENDIMIENTOS",
                    "VISITAS A TERCEROS AUTORIZADOS",
                    "VISITAS DE CONVOCATORIA DE TE ACOMPAÑO",
                    "CONVOCATORIA PARA CAMPAÑAS","VISITAS REMOTAS"],
        "REUNIONES": ["REUNION EQUIPO UT","REUNION CON SECTOR SALUD",
                      "REUNION SABERES","REUNION CON GL"]
    }

    respuestas = {}
    for act, subs in actividades.items():
        respuestas[act] = st.multiselect(
            f"{act}",
            subs,
            key=f"{act}_{form_id}"
        )

    otras_actividades = st.text_area(
        "Otras actividades",
        key=f"otras_{form_id}"
    )

    # ========= BOTONES =========
    colg1, colg2 = st.columns(2)
    guardar = colg1.form_submit_button("💾 Guardar registro")
    nuevo = colg2.form_submit_button("🆕 Nuevo registro")

# ================= FUNCIONES =================
def reiniciar_formulario():
    st.session_state.form_id += 1

# ================= ACCIONES =================
if guardar:

    if not ut or not codigo_usuario or not nombres or not cargo:
        st.warning("⚠️ Complete todos los datos generales")
    else:
        client = conectar_sheet()
        sheet = client.open_by_key(SHEET_ID).sheet1

        timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")
        nombres_mayus = nombres.upper()
        otras_mayus = otras_actividades.upper() if otras_actividades else ""

        filas = []
        for act, subs in respuestas.items():
            for sub in subs:
                filas.append([
                    timestamp,
                    ut,
                    fecha.strftime("%d/%m/%Y"),
                    codigo_usuario,
                    nombres_mayus,
                    cargo,
                    act,
                    sub,
                    otras_mayus
                ])

        if filas:
            sheet.append_rows(filas)
            st.success("✅ Registro guardado correctamente")
            reiniciar_formulario()
            st.rerun()

if nuevo:
    reiniciar_formulario()
    st.rerun()
