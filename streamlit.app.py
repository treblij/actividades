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

# ================= USUARIOS =================
USUARIOS = {
    "admin": "1234",
    "usuario1": "abcd"
}

# ================= SESIÓN =================
if "login" not in st.session_state:
    st.session_state.login = False
if "login_success" not in st.session_state:
    st.session_state.login_success = False
if "form_id" not in st.session_state:
    st.session_state.form_id = 0

# ================= LOGIN =================
def login():
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
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Ingreso al Sistema</div>', unsafe_allow_html=True)

    with st.form(key="login_form"):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")

    if ingresar:
        if USUARIOS.get(usuario) == contrasena:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.form_id = 0
            st.session_state.login_success = True  # flag temporal
        else:
            st.error("Usuario o contraseña incorrectos ❌")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= LÓGICA LOGIN =================
if not st.session_state.login:
    login()
    # fuera de la función, hacemos rerun seguro si login fue exitoso
    if st.session_state.login_success:
        st.session_state.login_success = False
        st.experimental_rerun()
    else:
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

# ================= FORMULARIO =================
def limpiar_formulario():
    keys_a_borrar = ["ut", "fecha", "codigo_usuario", "nombres", "cargo", "otras_actividades"] + list(actividades.keys())
    for key in keys_a_borrar:
        if key in st.session_state:
            del st.session_state[key]

with st.form(key=f"form_{st.session_state.form_id}"):

    st.title(f"Bienvenido {st.session_state.usuario} ✅")
    st.markdown("<h3>📋 Ficha de Registro de Actividades UT</h3>", unsafe_allow_html=True)

    # Datos generales
    titulo("Datos Generales")
    st.markdown("<div class='tarjeta'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        ut = st.selectbox("UT", ["","UT - AMAZONAS","UT - ANCASH","UT - APURIMAC","UT - AREQUIPA",
                                 "UT - AYACUCHO","UT - CUSCO","UT - HUANCAVELICA","UT - HUANUCO",
                                 "UT - ICA","UT - JUNIN","UT - LA LIBERTAD","UT - LAMBAYEQUE",
                                 "UT - LIMA METROPOLITANA Y CALLAO","UT - LIMA PROVINCIAS","UT - LORETO",
                                 "UT - MADRE DE DIOS","UT - MOQUEGUA","UT - PASCO","UT - PIURA",
                                 "UT - PUNO","UT - SAN MARTIN","UT - TACNA","UT - TUMBES","UT - UCAYALI"], key="ut")
    with col2:
        fecha = st.date_input("Fecha", value=datetime.today(), max_value=datetime.today(), key="fecha")
    with col3:
        codigo_usuario = st.text_input("Código de Usuario", key="codigo_usuario")
    with col4:
        nombres = st.text_input("Apellidos y Nombres", key="nombres")
    with col5:
        cargo = st.selectbox("Cargo/Puesto", ["","CT-Coordinador Territorial","PRO-Promotor","ATE-Asistente Técnico","Gestor te Acompaño","Otro"], key="cargo")
    st.markdown("</div>", unsafe_allow_html=True)

    # Actividades
    titulo("Actividades")
    respuestas = {}
    for act, subs in actividades.items():
        respuestas[act] = st.selectbox(f"{act}", [""] + subs, key=act)
    otras_actividades = st.text_area("Otras actividades", key="otras_actividades")

    # Botones
    colb1, colb2 = st.columns(2)
    guardar = colb1.form_submit_button("💾 Guardar registro")
    nuevo = colb2.form_submit_button("🆕 Nuevo registro")

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
        limpiar_formulario()
        st.session_state.form_id += 1
        st.experimental_rerun()

if nuevo:
    limpiar_formulario()
    st.session_state.form_id += 1
    st.experimental_rerun()
