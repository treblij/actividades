import streamlit as st
import pandas as pd
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

# ================= LOGIN SIMPLE =================
USUARIOS = {
    "admin": "1234",
    "usuario1": "abcd"
}

def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Ingreso al Sistema</h2>", unsafe_allow_html=True)
    usuario = st.text_input("Usuario", key="login_usuario")
    contrasena = st.text_input("Contraseña", type="password", key="login_pass")

    if st.button("Ingresar"):
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            st.session_state["login"] = True
            st.session_state["usuario"] = usuario
            st.success(f"Bienvenido {usuario} ✅")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")

if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
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

st.title("📋 Ficha de Registro de Actividades UT")

# ================= ACTIVIDADES (DEFINIR ANTES PARA LIMPIEZA) =================
actividades = {
    "BIENESTAR": ["ACTIVO", "VACACIONES", "LICENCIA SINDICAL", "EXAMEN MEDICO", "LICENCIA MEDICA"],
    "VISITAS": ["VISITAS DOMICILIARIAS", "BARRIDOS", "VISITAS A EMPRENDIMIENTOS", "VISITAS REMOTAS"],
    "GABINETE": ["REGISTRO DE DJ", "ELABORACION DE INFORMES", "SUPERVISION", "ATENCION AL USUARIO"],
    "REUNIONES": ["REUNION EQUIPO UT", "REUNION CON SALUD", "REUNION CON GL"]
}

# ================= FUNCIÓN LIMPIAR FORMULARIO =================
def limpiar_formulario():
    keys_a_borrar = [
        "ut", "fecha", "codigo_usuario", "nombres", "cargo",
        "otras_actividades"
    ] + list(actividades.keys())

    for key in keys_a_borrar:
        if key in st.session_state:
            del st.session_state[key]

# ================= DATOS GENERALES =================
titulo("Datos Generales")
with st.container():
    st.markdown("<div class='tarjeta'>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        ut = st.selectbox(
            "UT",
            [
                "",
                "UT - AMAZONAS","UT - ANCASH","UT - APURIMAC","UT - AREQUIPA",
                "UT - AYACUCHO","UT - CUSCO","UT - HUANCAVELICA","UT - HUANUCO",
                "UT - ICA","UT - JUNIN","UT - LA LIBERTAD","UT - LAMBAYEQUE",
                "UT - LIMA METROPOLITANA Y CALLAO","UT - LIMA PROVINCIAS","UT - LORETO",
                "UT - MADRE DE DIOS","UT - MOQUEGUA","UT - PASCO","UT - PIURA",
                "UT - PUNO","UT - SAN MARTIN","UT - TACNA","UT - TUMBES","UT - UCAYALI"
            ],
            key="ut"
        )

    with col2:
        fecha = st.date_input(
            "Fecha",
            value=datetime.today(),
            max_value=datetime.today(),
            key="fecha"
        )

    with col3:
        codigo_usuario = st.text_input("Código de Usuario", key="codigo_usuario")

    with col4:
        nombres = st.text_input("Apellidos y Nombres", key="nombres")

    with col5:
        cargo = st.selectbox(
            "Cargo/Puesto",
            ["", "CT-Coordinador Territorial", "PRO-Promotor",
             "ATE-Asistente Técnico", "Gestor te Acompaño", "Otro"],
            key="cargo"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ================= ACTIVIDADES =================
titulo("Actividades")

respuestas = {}
for act, subs in actividades.items():
    st.markdown(f"**{act}**")
    respuestas[act] = st.selectbox(
        f"Subactividad de {act}",
        [""] + subs,
        key=act
    )

otras_actividades = st.text_area("Otras actividades", key="otras_actividades")

# ================= BOTONES =================
col1, col2 = st.columns(2)

# Guardar registro
with col1:
    if st.button("💾 Guardar registro"):
        if not ut or not codigo_usuario or not nombres or not cargo:
            st.warning("⚠️ Complete todos los datos generales")
        else:
            filas = []
            for act, sub in respuestas.items():
                if sub:
                    filas.append([
                        ut,
                        fecha.strftime("%d/%m/%Y"),
                        codigo_usuario,
                        nombres,
                        cargo,
                        act,
                        sub,
                        otras_actividades
                    ])

            if not filas:
                st.warning("⚠️ No seleccionó actividades")
            else:
                sheet = conectar_sheet()
                for fila in filas:
                    sheet.append_row(fila)

                st.success(f"✅ Se guardaron {len(filas)} registros")
                limpiar_formulario()
                st.rerun()

# Nuevo registro
with col2:
    if st.button("🆕 Nuevo registro"):
        limpiar_formulario()
        st.rerun()
