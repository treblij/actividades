import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import bcrypt

# ================= CONFIGURACIÓN =================
SHEET_ID = "1BihXG87fSsYxt2Ail1v805xwTStyL_4JOWbDPUp9ics"
ZONA_PERU = pytz.timezone("America/Lima")

st.set_page_config(page_title="Ficha de Actividades UT", layout="wide")

# ================= CONEXIÓN GOOGLE SHEETS =================
def conectar_sheet(sheet_id=SHEET_ID):
    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client

def obtener_usuarios():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("USUARIOS")
    data = sheet.get_all_records()

    usuarios = {}
    for fila in data:
        usuario = fila.get("usuario")
        password_hash = fila.get("password_hash")
        activo = fila.get("activo", "").strip().upper()
        rol = fila.get("rol", "USER")

        if not usuario or not password_hash:
            continue

        if activo == "SI":
            usuarios[usuario] = {
                "hash": password_hash,
                "rol": rol
            }
    return usuarios

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

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.markdown("<h2>🔐 Ingreso al Sistema</h2>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        usuarios = obtener_usuarios()
        if usuario in usuarios:
            hash_guardado = usuarios[usuario]["hash"].encode()
            if bcrypt.checkpw(contrasena.encode(), hash_guardado):
                st.session_state.login = True
                st.session_state.usuario = usuario
                st.session_state.form_id = 0
                st.success(f"✅ Bienvenido {usuario}")
            else:
                st.error("Contraseña incorrecta ❌")
        else:
            st.error("Usuario no encontrado ❌")

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

def conectar_sheet_actividades():
    client = conectar_sheet()
    return client.open_by_key(SHEET_ID).sheet1

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
            "U.T. AMAZONAS",
            "U.T. ANCASH",
            "U.T. APURIMAC",
            "U.T. AREQUIPA",
            "U.T. AYACUCHO",
            "U.T. CAJAMARCA",
            "U.T. CUSCO",
            "U.T. HUANCAVELICA",
            "U.T. HUANUCO",
            "U.T. ICA",
            "U.T. JUNIN",
            "U.T. LA LIBERTAD",
            "U.T. LAMBAYEQUE",
            "U.T. LIMA METROPOLITANA Y CALLAO",
            "U.T. LIMA PROVINCIAS",
            "U.T. LORETO",
            "U.T. MADRE DE DIOS",
            "U.T. MOQUEGUA",
            "U.T. PASCO",
            "U.T. PIURA",
            "U.T. PUNO",
            "U.T. SAN MARTIN",
            "U.T. TACNA",
            "U.T. TUMBES",
            "U.T. UCAYALI"],
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
        sheet = conectar_sheet_actividades()

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
