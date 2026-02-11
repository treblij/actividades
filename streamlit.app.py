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
    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client

# ================= CARGAR DATOS PERSONALES =================
@st.cache_data(ttl=300)
def cargar_datos_personales():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("DATOSPERSONALES")
    datos = sheet.get_all_records()
    return datos

datos_personales = cargar_datos_personales()

# Diccionario UT -> Código -> Nombres
ut_dict = {}
for fila in datos_personales:
    ut = fila.get("UT", "").strip()
    codigo = fila.get("CODIGO  DE USUARIO", "").strip()  # Fíjate si hay doble espacio
    nombres = fila.get("APELLIDOS Y NOMBRES", "").strip()
    if ut and codigo:
        if ut not in ut_dict:
            ut_dict[ut] = {}
        ut_dict[ut][codigo] = nombres

# ================= FORMULARIO =================
st.title("📋 Ficha de Registro de Actividades UT")

# Inicializar sesión para botones
if "form_id" not in st.session_state:
    st.session_state.form_id = 0

form_id = st.session_state.form_id

# ---------------- Datos Generales ----------------
st.subheader("Datos Generales")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    lista_ut = [""] + sorted(ut_dict.keys())
    ut_seleccionada = st.selectbox("UT", lista_ut, key=f"ut_{form_id}")

with col2:
    fecha = st.date_input("Fecha", value=datetime.now(ZONA_PERU).date(), key=f"fecha_{form_id}")

with col3:
    codigos = [""] + sorted(ut_dict.get(ut_seleccionada, {}).keys()) if ut_seleccionada else [""]
    codigo_usuario_seleccionado = st.selectbox("Código de Usuario", codigos, key=f"codigo_{form_id}")

with col4:
    nombres = ""
    if ut_seleccionada and codigo_usuario_seleccionado:
        nombres = ut_dict[ut_seleccionada][codigo_usuario_seleccionado]
    st.text_input("Apellidos y Nombres", value=nombres, disabled=True, key=f"nombres_{form_id}")

with col5:
    cargo = st.selectbox(
        "Cargo/Puesto",
        ["", "JEFE DE UNIDAD TERRITORIAL", "COORDINADOR TERRITORIAL","PROMOTOR",
         "TECNICO EN ATENCION AL USUARIO","ASISTENTE TECNICO EN SABERES PRODUCTIVOS",
         "AUXILIAR ADMINISTRATIVO","CONDUCTOR","TECNICO EN ATENCION DE PLATAFORMA",
         "ASISTENTE ADMINISTRATIVO","OTRO"],
        key=f"cargo_{form_id}"
    )

# ---------------- Actividades ----------------
st.subheader("Actividades")
actividades = {
    "BIENESTAR": ["VACACIONES","ACTIVO","LICENCIA SINDICAL","EXAMEN MEDICO OCUPACIONAL","LICENCIA MEDICA","ONOMASTICO","DESCANSO FISICO POR COMPENSACION"],
    "VISITAS": ["VISITAS DOMICILIARIAS A USUARIOS REGULARES","BARRIDOS","VISITAS A USUARIOS CON EMPRENDIMIENTOS","VISITAS A TERCEROS AUTORIZADOS","VISITAS DE CONVOCATORIA DE TE ACOMPAÑO","CONVOCATORIA PARA CAMPAÑAS","VISITAS REMOTAS"],
    "PAGO RBU": ["SUPERVISION Y ACOMPAÑAMIENTO DEL PAGO","TARJETIZACION","SUPERVISION ETV"],
    "MUNICIPALIDAD": ["ATENCION EN ULE","PARTICIPACION EN IAL"],
    "GABINETE": ["REGISTRO DE DJ","ELABORACION DE INFORMES","GABINETE TE ACOMPAÑO","MAPEO DE USUARIOS","SUPERVISION DE PROMOTORES","APOYO UT","REGISTRO DE EMPRENDIMIENTOS","REGISTRO DE DONACIONES","DESPLAZAMIENTO A COMISIONES","ATENCION AL USUARIO Y TRAMITES","ASISTENCIA Y CAPACITACION A ACTORES EXTERNOS","CAPACITACIONES AL PERSONAL","REGISTRO DE SABERES","ASISTENCIA TECNICA SABERES PRODUCTIVOS"],
    "CAMPAÑAS": ["PARTICIPACION EN EMERGENCIAS","AVANZADA PARA CAMPAÑAS","PARTICIPACION EN ENTREGA DE DONACIONES","PARTICIPACION EN TE ACOMPAÑO","DIALOGOS DE SABERES","ENCUENTROS DE SABERES PRODUCTIVOS","TRANSMISION INTER GENERACIONAL","FERIAS DE EMPRENDIMIENTOS"],
    "REUNIONES": ["REUNION EQUIPO UT","REUNION CON SECTOR SALUD","REUNION SABERES","REUNION CON GL"]
}

respuestas = {}
for act, sub_acts in actividades.items():
    respuestas[act] = st.multiselect(f"{act}", sub_acts, key=f"{act}_{form_id}")

otras_actividades = st.text_area("Otras actividades", key=f"otras_{form_id}")

# ---------------- Botones Guardar y Nuevo ----------------
col_guardar, col_nuevo = st.columns([1,1])

with col_guardar:
    guardar = st.button("💾 Guardar registro", key=f"guardar_{form_id}")

with col_nuevo:
    nuevo = st.button("🆕 Nuevo registro", key=f"nuevo_{form_id}")

# ================= FUNCIONES =================
def reiniciar_formulario():
    st.session_state.form_id += 1

# ================= ACCIONES =================
if guardar:
    if not ut_seleccionada or not codigo_usuario_seleccionado or not nombres or not cargo:
        st.warning("⚠️ Complete todos los datos generales")
    else:
        try:
            client = conectar_sheet()
            sheet = client.open_by_key(SHEET_ID).sheet1  # Cambiar si tu hoja destino es otra
            timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")
            filas = []
            for act, sub_seleccionadas in respuestas.items():
                for sub in sub_seleccionadas:
                    filas.append([
                        timestamp,
                        ut_seleccionada,
                        fecha.strftime("%d/%m/%Y"),
                        codigo_usuario_seleccionado,
                        nombres,
                        cargo,
                        act,
                        sub,
                        otras_actividades.upper() if otras_actividades else ""
                    ])
            if filas:
                sheet.append_rows(filas)
                st.success("✅ Registro guardado correctamente")
                reiniciar_formulario()
        except Exception as e:
            st.error(f"Error al guardar en Google Sheets: {e}")

if nuevo:
    reiniciar_formulario()
    st.experimental_rerun()  # Reinicia el formulario limpio
