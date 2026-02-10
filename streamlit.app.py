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
    return client.open_by_key(SHEET_ID).sheet1

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
.login-container {
    max-width: 400px;
    margin: 0 auto 40px auto;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN SIMPLE =================
USUARIOS = {
    "admin": "1234",
    "jrm": "jrm"
}

if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.markdown("<h2>🔐 Ingreso al Sistema</h2>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if USUARIOS.get(usuario) == contrasena:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.form_id = 0
        else:
            st.error("Usuario o contraseña incorrectos ❌")

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.login:
    login()
    st.stop()

# ================= LOGOUT =================
col_logout, _ = st.columns([1, 6])
if col_logout.button("🔓 Cerrar sesión"):
    st.session_state.clear()
    st.experimental_rerun()

# ================= FUNCIONES =================
def titulo(texto):
    st.markdown(f"<div class='cinta'>{texto}</div>", unsafe_allow_html=True)

# ================= ACTIVIDADES =================
actividades = {
    "BIENESTAR": ["VACACIONES",
                  "ACTIVO",
                  "LICENCIA SINDICAL",
                  "EXAMEN MEDICO OCUPACIONAL",
                  "LICENCIA MEDICA", 
                  "ONOMASTICO", 
                  "DESCANSO FISICO POR COMPENSACION"],
    "VISITAS": [
        "VISITAS DOMICILIARIAS A USUARIOS REGULARES","BARRIDOS",
        "VISITAS A USUARIOS CON EMPRENDIMIENTOS","VISITAS A TERCEROS AUTORIZADOS",
        "VISITAS DE CONVOCATORIA DE TE ACOMPAÑO","CONVOCATORIA PARA CAMPAÑAS",
        "VISITAS REMOTAS"
    ],
    "PAGO RBU": ["SUPERVISION Y ACOMPAÑAMIENTO DEL PAGO","TARJETIZACION","SUPERVISION ETV"],
    "MUNICIPALIDAD": ["ATENCION EN ULE","PARTICIPACION EN IAL"],
    "GABINETE": [
        "REGISTRO DE DJ","ELABORACION DE INFORMES, PRIORIZACIONES Y OTROS",
        "GABINETE TE ACOMPAÑO","MAPEO DE USUARIOS","SUPERVISION DE PROMOTORES",
        "APOYO UT","REGISTRO DE EMPRENDIMIENTOS","REGISTRO DE DONACIONES",
        "DESPLAZAMIENTO A COMISIONES","ATENCION AL USUARIO Y TRAMITES",
        "ASISTENCIA Y CAPACITACION A ACTORES EXTERNOS",
        "CAPACITACIONES AL PERSONAL","REGISTRO DE SABERES",
        "ASISTENCIA TECNICA SABERES PRODUCTIVOS"
    ],
    "CAMPAÑAS": [
        "PARTICIPACION EN EMERGENCIAS (INCENDIOS)","AVANZADA PARA CAMPAÑAS",
        "PARTICIPACION EN CAMPAÑAS DE ENTREGA DE DONACIONES",
        "PARTICIPACION EN TE ACOMPAÑO","DIALOGOS DE SABERES",
        "ENCUENTROS DE SABERES PRODUCTIVOS","TRANSMISION INTER GENERACIONAL",
        "FERIAS DE EMPRENDIMIENTOS"
    ],
    "REUNIONES": [
        "REUNION EQUIPO UT","REUNION CON SECTOR SALUD DIRESA, RIS, IPRESS",
        "REUNION SABERES","REUNION CON GL"
    ]
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
            value=datetime.now(ZONA_PERU).date(),
            key=f"fecha_{form_id}"
        )

    with col3:
        codigo_usuario = st.text_input("Código de Usuario", key=f"codigo_{form_id}")

    with col4:
        nombres = st.text_input("Apellidos y Nombres", key=f"nombres_{form_id}")

    with col5:
        cargo = st.selectbox(
            "Cargo/Puesto",
            ["", "JEFE DE UNIDAD TERRITORIAL", 
                 "COORDINADOR TERRITORIAL",
                 "PROMOTOR",
                 "TECNICO EN ATENCION AL USUARIO",
                 "ASISTENTE TECNICO EN SABERES PRODUCTIVOS",
                 "AUXILIAR ADMINISTRATIVO",
                 "CONDUCTOR",
                 "TECNICO EN ATENCION DE PLATAFORMA",
                 "ASISTENTE ADMINISTRATIVO", "OTRO"],
            key=f"cargo_{form_id}"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    titulo("Actividades")

    respuestas = {}
    for act, subs in actividades.items():
        respuestas[act] = st.selectbox(act, [""] + subs, key=f"{act}_{form_id}")

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

        timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")

        # FORZAR MAYÚSCULAS
        nombres_mayus = nombres.strip().upper()
        otras_mayus = otras_actividades.strip().upper()

        for act, sub in respuestas.items():
            if sub:
                sheet.append_row([
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

        st.success("✅ Registro guardado correctamente")
        st.session_state.form_id += 1
        st.experimental_rerun()

if nuevo:
    st.session_state.form_id += 1
    st.experimental_rerun()
