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
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        st.stop()

# ================= OBTENER USUARIOS =================
def obtener_usuarios():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("USUARIOS")
    data = sheet.get_all_records()

    usuarios = {}
    for fila in data:
        usuario = fila.get("usuario")
        contrasena = fila.get("password_hash")
        activo = fila.get("activo")
        rol = fila.get("rol", "USER")

        if usuario and contrasena and activo and activo.strip():
            usuarios[usuario] = {
                "password": str(contrasena).strip(),
                "rol": rol
            }
    return usuarios

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

usuarios = obtener_usuarios()

def login():
    st.image("logo.png", width=150)
    st.subheader("🔐 Ingreso al Sistema")

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario in usuarios and usuarios[usuario]["password"] == contrasena:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.form_id = 0
            st.success(f"Bienvenido {usuario}!")
        else:
            st.error("Usuario o contraseña incorrectos ❌")

if not st.session_state.login:
    login()
    st.stop()

# ================= LOGOUT =================
if st.button("🔓 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

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

# ================= FORM ID =================
if "form_id" not in st.session_state:
    st.session_state.form_id = 0

form_id = st.session_state.form_id

# ================= CARGAR DATOS PERSONALES =================
def cargar_datos_personales():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("DATOSPERSONALES")
    return sheet.get_all_records()

datos_personales = cargar_datos_personales()

ut_dict = {}
for fila in datos_personales:
    ut = fila.get("UT", "").strip()
    codigo = fila.get("CODIGO  DE USUARIO", "").strip()
    nombre = fila.get("APELLIDOS Y NOMBRES", "").strip()

    if ut and codigo:
        if ut not in ut_dict:
            ut_dict[ut] = {}
        ut_dict[ut][codigo] = nombre

# ================= DATOS GENERALES =================
st.title("📋 Ficha de Registro de Actividades UT")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    ut = st.selectbox("UT", [""] + sorted(ut_dict.keys()), key=f"ut_{form_id}")

with col2:
    fecha = st.date_input("Fecha", value=datetime.now(ZONA_PERU).date(), key=f"fecha_{form_id}")

with col3:
    codigos = [""] + sorted(ut_dict.get(ut, {}).keys()) if ut else [""]
    codigo_usuario = st.selectbox("Código de Usuario", codigos, key=f"codigo_{form_id}")

# 🔥 ACTUALIZACIÓN AUTOMÁTICA DEL NOMBRE
if ut and codigo_usuario:
    st.session_state[f"nombres_{form_id}"] = ut_dict[ut].get(codigo_usuario, "")
else:
    st.session_state[f"nombres_{form_id}"] = ""

with col4:
    st.text_input("Apellidos y Nombres", key=f"nombres_{form_id}", disabled=True)

with col5:
    cargo = st.selectbox(
        "Cargo/Puesto",
        ["", "JEFE DE UNIDAD TERRITORIAL", "COORDINADOR TERRITORIAL","PROMOTOR",
         "TECNICO EN ATENCION AL USUARIO","ASISTENTE TECNICO EN SABERES PRODUCTIVOS",
         "AUXILIAR ADMINISTRATIVO","CONDUCTOR","TECNICO EN ATENCION DE PLATAFORMA",
         "ASISTENTE ADMINISTRATIVO","OTRO"],
        key=f"cargo_{form_id}"
    )

# ================= FORM ACTIVIDADES =================
with st.form(key=f"form_{form_id}"):

    respuestas = {}
    for act, subs in actividades.items():
        respuestas[act] = st.multiselect(f"{act}", subs, key=f"{act}_{form_id}")

    otras_actividades = st.text_area("Otras actividades", key=f"otras_{form_id}")

    colg1, colg2 = st.columns(2)
    guardar = colg1.form_submit_button("💾 Guardar registro")
    nuevo = colg2.form_submit_button("🆕 Nuevo registro")

# ================= FUNCIONES =================
def reiniciar_formulario():
    st.session_state.form_id += 1

# ================= ACCIONES =================
if guardar:
    nombres = st.session_state.get(f"nombres_{form_id}", "")
    if not ut or not codigo_usuario or not nombres or not cargo:
        st.warning("⚠️ Complete todos los datos generales")
    else:
        client = conectar_sheet()
        sheet = client.open_by_key(SHEET_ID).sheet1

        timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")

        filas = []
        for act, subs in respuestas.items():
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
                    (otras_actividades or "").upper()
                ])

        if filas:
            sheet.append_rows(filas)
            st.success("✅ Registro guardado correctamente")
            reiniciar_formulario()
            st.rerun()

if nuevo:
    reiniciar_formulario()
    st.rerun()
