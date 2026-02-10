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

# ================= ESTILOS =================
st.markdown("""
<style>
/* Login personalizado */
.login-container {
    background-color: #f0f8ff;
    padding: 25px;
    border-radius: 15px;
    max-width: 400px;
    margin: 0 auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.login-container h2 {
    text-align: center;
    color: #1f77b4;
}
.stTextInput>div>div>input {
    background-color: #e6f2ff !important;
    border-radius: 8px !important;
    border: 1px solid #1f77b4 !important;
    padding: 8px !important;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}
.stButton>button:hover {
    background-color: #4fa3d1;
}
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

# ================= LOGIN SIMPLE =================
USUARIOS = {
    "admin": "1234",
    "jrm": "jrm"
}

def login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Logo arriba del título
    st.image("logo.png", width=150)
    st.markdown("<h2>🔐 Ingreso al Sistema</h2>", unsafe_allow_html=True)
    
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if USUARIOS.get(usuario) == contrasena:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.form_id = 0
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")
    
    st.markdown("</div>", unsafe_allow_html=True)

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

# ================= FUNCIONES =================
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
            if sub:  # evita guardar vacíos
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
