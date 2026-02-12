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
    return gspread.authorize(creds)

# ================= CACHE DATOS =================
@st.cache_data(ttl=600)
def cargar_datos_personales():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("DATOSPERSONALES")
    return sheet.get_all_records()

@st.cache_data(ttl=600)
def obtener_usuarios():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("USUARIOS")
    return sheet.get_all_records()

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

usuarios_data = obtener_usuarios()
usuarios = {}
for fila in usuarios_data:
    if fila.get("usuario") and fila.get("password_hash") and fila.get("activo"):
        usuarios[fila["usuario"]] = str(fila["password_hash"]).strip()

def login():
    st.image("logo.png", width=150)
    st.subheader("🔐 Ingreso al Sistema")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario in usuarios and usuarios[usuario] == contrasena:
            st.session_state.login = True
            st.session_state.form_id = 0
            st.success("Bienvenido")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

if not st.session_state.login:
    login()
    st.stop()

# ================= LOGOUT =================
if st.button("🔓 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

# ================= FORM ID =================
if "form_id" not in st.session_state:
    st.session_state.form_id = 0

form_id = st.session_state.form_id

# ================= CARGAR DATOS PERSONALES =================
datos = cargar_datos_personales()
ut_dict = {}
for fila in datos:
    ut = fila.get("UT", "").strip()
    codigo = fila.get("CODIGO  DE USUARIO", "").strip()
    nombre = fila.get("APELLIDOS Y NOMBRES", "").strip()
    if ut and codigo:
        ut_dict.setdefault(ut, {})[codigo] = nombre

# ================= TITULO =================
st.title("📋 Ficha de Registro de Actividades UT")

# ================= DATOS GENERALES =================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    ut = st.selectbox("UT", [""] + sorted(ut_dict.keys()), key="ut_global")

with col2:
    fecha = st.date_input("Fecha", value=datetime.now(ZONA_PERU).date(), key="fecha_global")

with col3:
    codigos = [""] + sorted(ut_dict.get(ut, {}).keys()) if ut else [""]
    codigo_usuario = st.selectbox("Código de Usuario", codigos, key="codigo_global")

with col4:
    nombres = ""
    if ut and codigo_usuario:
        nombres = ut_dict[ut].get(codigo_usuario, "")
    st.text_input("Apellidos y Nombres", value=nombres, disabled=True)

with col5:
    cargo = st.selectbox(
        "Cargo/Puesto",
        ["", "JEFE DE UNIDAD TERRITORIAL", "COORDINADOR TERRITORIAL",
         "PROMOTOR","TECNICO EN ATENCION AL USUARIO",
         "ASISTENTE TECNICO EN SABERES PRODUCTIVOS",
         "AUXILIAR ADMINISTRATIVO","CONDUCTOR",
         "TECNICO EN ATENCION DE PLATAFORMA",
         "ASISTENTE ADMINISTRATIVO","OTRO"],
        key="cargo_global"
    )

# ================= ACTIVIDADES =================
actividades = {
    "BIENESTAR": ["VACACIONES","ACTIVO","LICENCIA SINDICAL","EXAMEN MEDICO OCUPACIONAL","LICENCIA MEDICA","ONOMASTICO","DESCANSO FISICO POR COMPENSACION"],
    "VISITAS": ["VISITAS DOMICILIARIAS A USUARIOS REGULARES","BARRIDOS","VISITAS A USUARIOS CON EMPRENDIMIENTOS","VISITAS A TERCEROS AUTORIZADOS","VISITAS DE CONVOCATORIA DE TE ACOMPAÑO","CONVOCATORIA PARA CAMPAÑAS","VISITAS REMOTAS"],
    "PAGO RBU": ["SUPERVISION Y ACOMPAÑAMIENTO DEL PAGO","TARJETIZACION","SUPERVISION ETV"],
    "MUNICIPALIDAD": ["ATENCION EN ULE","PARTICIPACION EN IAL"],
    "GABINETE": ["REGISTRO DE DJ","ELABORACION DE INFORMES, PRIORIZACIONES Y OTROS","GABINETE TE ACOMPAÑO","MAPEO DE USUARIOS","SUPERVISION DE PROMOTORES","APOYO UT","REGISTRO DE EMPRENDIMIENTOS","REGISTRO DE DONACIONES","DESPLAZAMIENTO A COMISIONES","ATENCION AL USUARIO Y TRAMITES","ASISTENCIA Y CAPACITACION A ACTORES EXTERNOS","CAPACITACIONES AL PERSONAL","REGISTRO DE SABERES","ASISTENCIA TECNICA SABERES PRODUCTIVOS"],
    "CAMPAÑAS": ["PARTICIPACION EN EMERGENCIAS (INCENDIOS)","AVANZADA PARA CAMPAÑAS","PARTICIPACION EN CAMPAÑAS DE ENTREGA DE DONACIONES","PARTICIPACION EN TE ACOMPAÑO","DIALOGOS DE SABERES","ENCUENTROS DE SABERES PRODUCTIVOS","TRANSMISION INTER GENERACIONAL","FERIAS DE EMPRENDIMIENTOS"],
    "REUNIONES": ["REUNION EQUIPO UT","REUNION CON SECTOR SALUD DIRESA, RIS, IPRESS","REUNION SABERES","REUNION CON GL"]
}

actividades_con_detalle = ["VISITAS", "PAGO RBU", "MUNICIPALIDAD", "CAMPAÑAS", "REUNIONES"]

# ================= FORM DE ACTIVIDADES =================
with st.form(key=f"form_{form_id}"):

    respuestas = {}

    for act, subs in actividades.items():
        seleccionadas = st.multiselect(
            act,
            subs,
            key=f"multi_{act}_{form_id}"
        )
        respuestas[act] = seleccionadas

        # Campo de detalle debajo de actividades específicas
        if act in actividades_con_detalle:
            st.text_area(
                f"Detalle adicional para {act}:",
                key=f"detalle_{act}_{form_id}",
                disabled=(len(seleccionadas) == 0),
                placeholder="Ingrese comentario o detalle..."
            )

    otras = st.text_area(
        "Otras actividades",
        key=f"otras_{form_id}"
    )

    col1, col2 = st.columns(2)
    guardar = col1.form_submit_button("💾 Guardar registro")
    nuevo = col2.form_submit_button("🆕 Nuevo registro")

# ================= GUARDAR =================
if guardar:
    if not ut or not codigo_usuario or not nombres or not cargo:
        st.warning("Complete todos los datos generales")
    else:
        client = conectar_sheet()
        sheet = client.open_by_key(SHEET_ID).sheet1
        timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")
        filas = []

        for act, subs in respuestas.items():
            comentario = st.session_state.get(f"detalle_{act}_{form_id}", "").upper()
            for sub in subs:
                filas.append([
                    timestamp,
                    ut,
                    fecha.strftime("%d/%m/%Y"),
                    codigo_usuario,
                    nombres.upper(),
                    cargo,
                    act,
                    sub,
                    comentario or st.session_state.get(f"otras_{form_id}", "").upper()
                ])

        if filas:
            sheet.append_rows(filas)
            st.success("Se registró tu información ✅")
            st.session_state.form_id += 1
            st.rerun()

# ================= NUEVO REGISTRO =================
if nuevo:
    st.session_state.form_id += 1
    st.rerun()
