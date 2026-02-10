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

# ================= LOGIN SIMPLE MEJORADO =================
USUARIOS = {
    "admin": "1234",
    "usuario1": "abcd"
}

def login():
    # Centrar contenido y limitar ancho con CSS
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 350px;
            margin: 50px auto;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.2);
            background: white;
        }
        .login-title {
            text-align: center;
            font-weight: 700;
            font-size: 24px;
            margin-bottom: 20px;
            color: #1f77b4;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">🔐 Ingreso al Sistema</div>', unsafe_allow_html=True)

        with st.form(key="login_form", clear_on_submit=False):
            usuario = st.text_input("Usuario")
            contrasena = st.text_input("Contraseña", type="password")
            ingresar = st.form_submit_button("Ingresar")

        if ingresar:
            if USUARIOS.get(usuario) == contrasena:
                st.session_state.login = True
                st.session_state.usuario = usuario
                st.session_state.form_id = 0
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos ❌")

        st.markdown('</div>', unsafe_allow_html=True)

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    login()
    st.stop()

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

form_id = st.session_state.form_id  # variable local para claridad

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
        fecha = st.date_input("Fecha", value=datetime.today(), max_value=datetime.today(), key=f"fecha_{form_id}")

    with col3:
        codigo_usuario = st.text_input("Código de Usuario", key=f"codigo_usuario_{form_id}")

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
        respuestas[act] = st.selectbox(f"{act}", [""] + subs, key=f"{act}_{form_id}")

    otras_actividades = st.text_area("Otras actividades", key=f"otras_actividades_{form_id}")

    colg1, colg2 = st.columns(2)
    guardar = colg1.form_submit_button("💾 Guardar registro")
    nuevo = colg2.form_submit_button("🆕 Nuevo registro")

# ================= ACCIONES =================
if guardar:
    if not ut or not codigo_usuario or not nombres or not cargo:
        st.warning("⚠️ Complete todos los datos generales")
    else:
        sheet = conectar_sheet()
        for act, sub in respuestas.items():
            if sub:
                sheet.append_row([
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
        st.experimental_rerun()

if nuevo:
    st.session_state.form_id += 1
    st.experimental_rerun()
