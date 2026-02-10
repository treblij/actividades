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

# ================= OBTENER USUARIOS =================
def obtener_usuarios():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("USUARIOS")
    data = sheet.get_all_records()

    usuarios = {}
    for fila in data:
        usuario = fila.get("usuario")
        contrasena = fila.get("password_hash")
        activo = fila.get("activo")  # puede estar vacío
        rol = fila.get("rol", "USER")

        if usuario and contrasena and activo and activo.strip():
            usuarios[usuario] = {
                "password": str(contrasena).strip(),
                "rol": rol
            }
    return usuarios

# ================= OBTENER DATOS PERSONALES =================
def obtener_datos_personales():
    client = conectar_sheet()
    sheet = client.open_by_key(SHEET_ID).worksheet("DATOSPERSONALES")
    data = sheet.get_all_records()

    datos_ut = {}
    for fila in data:
        ut = fila.get("UT")
        codigo = fila.get("CODIGO_SISOPE")
        nombre = fila.get("NOMBRE")
        if ut and ut.strip() and codigo and nombre:
            if ut not in datos_ut:
                datos_ut[ut] = []
            datos_ut[ut].append({"codigo": codigo, "nombre": nombre})
    return datos_ut

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

usuarios = obtener_usuarios()

def login():
    st.markdown('<div style="max-width:400px;margin:0 auto;text-align:center">', unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.markdown("<h2>🔐 Ingreso al Sistema</h2>", unsafe_allow_html=True)

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
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #1f77b4, #4fa3d1);
        padding: 10px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin: 20px 0;
    ">{texto}</div>
    """, unsafe_allow_html=True)

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
datos_ut = obtener_datos_personales()

# ================= FORMULARIO =================
with st.form(key=f"form_{form_id}"):

    st.title("📋 Ficha de Registro de Actividades UT")
    titulo("Datos Generales")

    st.markdown("<div style='background:white;padding:20px;border-radius:12px;box-shadow:0 3px 8px rgba(0,0,0,0.1);margin-bottom:25px'>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        ut = st.selectbox(
            "UT",
            [""] + list(datos_ut.keys()),
            key=f"ut_{form_id}"
        )

    with col2:
        fecha = st.date_input(
            "Fecha",
            value=datetime.now(ZONA_PERU).date(),
            key=f"fecha_{form_id}"
        )

    with col3:
        codigos_disponibles = []
        if ut:
            codigos_disponibles = [d["codigo"] for d in datos_ut[ut]]
        codigo_usuario = st.selectbox(
            "Código de Usuario",
            [""] + codigos_disponibles,
            key=f"codigo_{form_id}"
        )

    with col4:
        nombre_automatico = ""
        if ut and codigo_usuario:
            for d in datos_ut[ut]:
                if d["codigo"] == codigo_usuario:
                    nombre_automatico = d["nombre"]
                    break
        nombres = st.text_input("Apellidos y Nombres", value=nombre_automatico, key=f"nombres_{form_id}")

    with col5:
        cargo = st.selectbox(
            "Cargo/Puesto",
            ["", "JEFE DE UNIDAD TERRITORIAL", "COORDINADOR TERRITORIAL","PROMOTOR","TECNICO EN ATENCION AL USUARIO",
             "ASISTENTE TECNICO EN SABERES PRODUCTIVOS","AUXILIAR ADMINISTRATIVO","CONDUCTOR","TECNICO EN ATENCION DE PLATAFORMA",
             "ASISTENTE ADMINISTRATIVO","OTRO"],
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
        client = conectar_sheet()
        sheet = client.open_by_key(SHEET_ID).sheet1

        timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")

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
