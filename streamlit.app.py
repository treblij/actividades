import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= CONFIGURACIÓN =================
SHEET_ID = "1BihXG87fSsYxt2Ail1v805xwTStyL_4JOWbDPUp9ics"

st.set_page_config(page_title="Ficha de Actividades UT", layout="wide")

# ================= CONEXIÓN GOOGLE SHEETS =================
def conectar_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

# ================= LOGIN MINIMALISTA =================
USUARIOS = {
    "admin": "1234",
    "jrm": "jrm"
}

def login():

    st.markdown("""
    <style>
    .login-card {
        width: 320px;
        margin: 120px auto;
        padding: 30px;
        border-radius: 14px;
        background: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        text-align: center;
    }
    .login-card img {
        width: 90px;
        margin-bottom: 15px;
    }
    .login-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-card">
        <img src="logo.png">
        <div class="login-title">Ingreso al sistema</div>
    </div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario", key="login_user")
    contrasena = st.text_input("Contraseña", type="password", key="login_pass")

    if st.button("Ingresar"):
        if USUARIOS.get(usuario) == contrasena:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.form_id = 0
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    login()
    st.stop()

# ================= LOGOUT =================
col_logout, _ = st.columns([1, 6])
if col_logout.button("🔓 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

# ================= ESTILOS =================
st.markdown("""
<style>
.cinta {
    background: linear-gradient(90deg, #1f77b4, #4fa3d1);
    padding: 10px;
    border-radius: 8px;
    font-size: 22px;
    font-weight: bold;
    color: white;
    text-align: center;
    margin: 20px 0;
}
.tarjeta {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

def titulo(texto):
    st.markdown(f"<div class='cinta'>{texto}</div>", unsafe_allow_html=True)

# ================= ACTIVIDADES =================
actividades = {
    "BIENESTAR": ["ACTIVO", "VACACIONES", "LICENCIA SINDICAL", "EXAMEN MEDICO", "LICENCIA MEDICA"],
    "VISITAS": ["VISITAS DOMICILIARIAS", "BARRIDOS", "VISITAS A EMPRENDIMIENTOS", "VISITAS REMOTAS"],
    "GABINETE": ["REGISTRO DE DJ", "ELABORACION DE INFORMES", "SUPERVISION", "ATENCION AL USUARIO"],
    "REUNIONES": ["REUNION EQUIPO UT", "REUNION CON SALUD", "REUNION CON GL"]
}

# ================= FORM ID =================
if "form_id" not in st.session_state:
    st.session_state.form_id = 0

form_id = st.session_state.form_id

# ================= FORMULARIO =================
with st.form(key=f"form_{form_id}"):

    st.title("📋 Ficha de Registro de Actividades UT")

    titulo("Datos Generales")
    st.markdown("<div class='tarjeta'>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        ut = st.selectbox(
            "UT",
            ["",
             "UT - AMAZONAS","UT - ANCASH","UT - APURIMAC","UT - AREQUIPA",
             "UT - AYACUCHO","UT - CUSCO","UT - HUANCAVELICA","UT - HUANUCO",
             "UT - ICA","UT - JUNIN","UT - LA LIBERTAD","UT - LAMBAYEQUE",
             "UT - LIMA METROPOLITANA Y CALLAO","UT - LIMA PROVINCIAS","UT - LORETO",
             "UT - MADRE DE DIOS","UT - MOQUEGUA","UT - PASCO","UT - PIURA",
             "UT - PUNO","UT - SAN MARTIN","UT - TACNA","UT - TUMBES","UT - UCAYALI"],
            key=f"ut_{form_id}"
        )

    with col2:
        fecha = st.date_input(
            "Fecha",
            value=datetime.today(),
            key=f"fecha_{form_id}"
        )

    with col3:
        codigo_usuario = st.text_input("Código de Usuario", key=f"codigo_{form_id}")

    with col4:
        nombres = st.text_input("Apellidos y Nombres", key=f"nombres_{form_id}")

    with col5:
        cargo = st.selectbox(
            "Cargo/Puesto",
            ["", "CT-Coordinador Territorial", "PRO-Promotor",
             "ATE-Asistente Técnico", "Gestor te Acompaño", "Otro"],
            key=f"cargo_{form_id}"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    titulo("Actividades")

    respuestas = {}
    for act, subs in actividades.items():
        respuestas[act] = st.selectbox(
            act,
            [""] + subs,
            key=f"{act}_{form_id}"
        )

    otras_actividades = st.text_area("Otras actividades", key=f"otras_{form_id}")

    colg1, colg2 = st.columns(2)
    guardar = colg1.form_submit_button("💾 Guardar registro")
    nuevo = colg2.form_submit_button("🆕 Nuevo registro")

# ================= ACCIONES =================
if guardar:
    if not ut or not codigo_usuario or not nombres or not cargo:
        st.warning("⚠️ Complete todos los datos generales")
    else:
        sheet = conectar_sheet()
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        for act, sub in respuestas.items():
            if sub:
                sheet.append_row([
                    timestamp,
                    ut,
                    fecha.strftime("%d/%m/%Y"),
                    codigo_usuario,
                    nombres,
                    cargo,
                    act,
                    sub,
                    otras_actividades
                ])

        st.success("✅ Registro guardado correctamente")
        st.session_state.form_id += 1
        st.rerun()

if nuevo:
    st.session_state.form_id += 1
    st.rerun()
