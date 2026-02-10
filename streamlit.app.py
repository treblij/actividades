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
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        st.stop()

# ================= OBTENER USUARIOS =================
def obtener_usuarios():
    client = conectar_sheet()
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet("USUARIOS")
        data = sheet.get_all_records()
    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        st.stop()

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
    st.experimental_rerun()  # Para cerrar sesión

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

# ================= FORMULARIO =================
with st.form(key=f"form_{form_id}"):

    st.title("📋 Ficha de Registro de Actividades UT")

    titulo("Datos Generales")
    st.markdown("<div style='background:white;padding:20px;border-radius:12px;box-shadow:0 3px 8px rgba(0,0,0,0.1);margin-bottom:25px'>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        ut = st.selectbox(
            "UT",
            ["",
             "U.T. AMAZONAS","U.T. ANCASH","U.T. APURIMAC","U.T. AREQUIPA","U.T. AYACUCHO","U.T. CAJAMARCA","U.T. CUSCO",
             "U.T. HUANCAVELICA","U.T. HUANUCO","U.T. ICA","U.T. JUNIN","U.T. LA LIBERTAD","U.T. LAMBAYEQUE",
             "U.T. LIMA METROPOLITANA Y CALLAO","U.T. LIMA PROVINCIAS","U.T. LORETO","U.T. MADRE DE DIOS","U.T. MOQUEGUA",
             "U.T. PASCO","U.T. PIURA","U.T. PUNO","U.T. SAN MARTIN","U.T. TACNA","U.T. TUMBES","U.T. UCAYALI"],
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
            ["", "JEFE DE UNIDAD TERRITORIAL", "COORDINADOR TERRITORIAL","PROMOTOR","TECNICO EN ATENCION AL USUARIO",
             "ASISTENTE TECNICO EN SABERES PRODUCTIVOS","AUXILIAR ADMINISTRATIVO","CONDUCTOR","TECNICO EN ATENCION DE PLATAFORMA",
             "ASISTENTE ADMINISTRATIVO","OTRO"],
            key=f"cargo_{form_id}"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    titulo("Actividades")

    respuestas = {}
    for act, subs in actividades.items():
        # Cambiado a MULTISELECT
        respuestas[act] = st.multiselect(f"{act}", subs, key=f"{act}_{form_id}")

    otras_actividades = st.text_area("Otras actividades", key=f"otras_{form_id}")

    colg1, colg2 = st.columns(2)
    guardar = colg1.form_submit_button("💾 Guardar registro")
    nuevo = colg2.form_submit_button("🆕 Nuevo registro")

# ================= ACCIONES =================
def reiniciar_formulario():
    st.session_state.form_id += 1
    # Limpiar campos del formulario
    keys_a_borrar = [k for k in st.session_state.keys() if k.startswith((
        "ut_", "fecha_", "codigo_", "nombres_", "cargo_",
        "BIENESTAR", "VISITAS", "PAGO RBU", "MUNICIPALIDAD", "GABINETE", "CAMPAÑAS", "REUNIONES", "otras_"
    ))]
    for key in keys_a_borrar:
        del st.session_state[key]

if guardar:
    if not ut or not codigo_usuario or not nombres or not cargo:
        st.warning("⚠️ Complete todos los datos generales")
    else:
        client = conectar_sheet()
        try:
            sheet = client.open_by_key(SHEET_ID).sheet1
        except Exception as e:
            st.error(f"Error al abrir la hoja: {e}")
            st.stop()

        timestamp = datetime.now(ZONA_PERU).strftime("%d/%m/%Y %H:%M:%S")
        nombres_mayus = nombres.strip().upper()
        otras_mayus = (otras_actividades or "").strip().upper()

        filas = []
        # Guardar múltiples sub-actividades por actividad
        for act, subs_seleccionadas in respuestas.items():
            for sub in subs_seleccionadas:
                filas.append([
                    timestamp,
                    ut or "",
                    fecha.strftime("%d/%m/%Y"),
                    codigo_usuario or "",
                    nombres_mayus or "",
                    cargo or "",
                    act or "",
                    sub or "",
                    otras_mayus
                ])

        if filas:
            try:
                sheet.append_rows(filas)
                st.success("✅ Registro guardado correctamente")
                reiniciar_formulario()
            except Exception as e:
                st.error(f"Error al guardar en Google Sheets: {e}")

if nuevo:
    reiniciar_formulario()
