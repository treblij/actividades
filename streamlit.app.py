
import streamlit as st
import pandas as pd
import os
from datetime import datetime

ARCHIVO_EXCEL = "registros_ficha_completa.xlsx"

st.set_page_config(page_title="Ficha de Actividades UT", layout="wide")

# ======= LOGIN SIMPLE =======
USUARIOS = {"admin":"1234", "usuario1":"abcd"}

def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Ingreso al Sistema</h2>", unsafe_allow_html=True)
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            st.session_state["login"] = True
            st.session_state["usuario"] = usuario
            st.success(f"Bienvenido {usuario} ✅")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")

if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    login()
else:

    # ====== ESTILOS CSS ======
    st.markdown("""
    <style>
    .cinta {
        background: linear-gradient(90deg, #1f77b4, #4fa3d1);
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: 700;
        color: white;
        margin: 20px 0 10px 0;
        text-align: center;
    }
    .tarjeta {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    div[data-baseweb="select"] > div {
        border-radius: 6px !important;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px 25px;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #155a8a;
        transform: scale(1.05);
    }
    textarea {
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    def titulo_cinta(texto):
        st.markdown(f"<div class='cinta'>{texto}</div>", unsafe_allow_html=True)

    st.title("📋 Ficha de Registro de Actividades UT")

    # ====== DATOS GENERALES ======
    titulo_cinta("Datos Generales")
    with st.container():
        st.markdown("<div class='tarjeta'>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        with col1:
            ut = st.selectbox("UT", [
                "",
                "UT - AMAZONAS","UT - ANCASH","UT - APURIMAC","UT - AREQUIPA",
                "UT - AYACUCHO","UT - CUSCO","UT - HUANCAVELICA","UT - HUANUCO",
                "UT - ICA","UT - JUNIN","UT - LA LIBERTAD","UT - LAMBAYEQUE",
                "UT - LIMA METROPOLITANA Y CALLAO","UT - LIMA PROVINCIAS","UT - LORETO",
                "UT - MADRE DE DIOS","UT - MOQUEGUA","UT - PASCO","UT - PIURA",
                "UT - PUNO","UT - SAN MARTIN","UT - TACNA","UT - TUMBES","UT - UCAYALI"
            ])
        with col2:
            fecha = st.date_input("Fecha", max_value=datetime.today())
        with col3:
            codigo_usuario = st.text_input("Código de Usuario")
        with col4:
            nombres = st.text_input("Apellidos y Nombres")
        with col5:
            cargo = st.selectbox("Cargo/Puesto", ["", "CT-Coordinador Territorial", 
                                                      "PRO-Promotor", 
                                                      "ATE-Asistente Técnico de Saberes Productivos", 
                                                      "Gestor de Acompaño",
                                                      "Otro"])

        st.markdown("</div>", unsafe_allow_html=True)

    # ====== ACTIVIDADES ======
    titulo_cinta("Actividades")
    actividades_dict = {
        "BIENESTAR": [
            "ACTIVO",
            "VACACIONES",
            "LICENCIA SINDICAL",
            "EXAMEN MEDICO",
            "LICENCIA MEDICA"],
        "VISITAS": [
            "VISITAS DOMICILIARIAS A USUARIOS REGULARES",
            "BARRIDOS",
            "VISITAS A USUARIOS CON EMPREDIMITOS",
            "VISITAS A TERCEROS AUTORIZADOS",
            "VISITAS DE CONVOCATORIA TE ACOMPAÑO",
            "CONVOCATORIA PARA CAMPAÑAS",
            "VISITAS REMOTAS"
        ],
        "PAGO RBU": [
            "SUPERVISION Y ACOMPAÑAMIENTO DEL PAGO",
            "TARJETIZACION",
            "SUPERVISION ETV"
        ],
        "MUNICIPALIDAD": ["ATENCION EN ULE","PARTICIPACION EN IAL"],
        "GABINETE": [
            "REGISTRO DE DJ",
            "ELABORACION DE INFORMES, PRIORIZACIONES Y OTROS",
            "GABINETE TE ACOMPAÑO",
            "MAPEO DE USUARIOS",
            "SUPERVISION DE PROMOTORES",
            "APOYO UT",
            "REGISTRO DE EMPRENDIMIENTOS",
            "REGISTRO DE DONACIONES",
            "DESPLAZAMIENTO A COMISIONES",
            "ATENCION AL USUARIO Y TRAMITES",
            "ASISTENCIA Y CAPACITACION A ACTORES EXTERNOS",
            "CAPACITACIONES AL PERSONAL",
            "REGISTRO DE SABERES",
            "ASISTENCIA TECNICA SABERES PRODUCTIVOS"
        ],
       
        "CAMPAÑAS": [
            "PARTICIPACION EN EMERGENCIAS (INCENDIOS)",
            "AVANZADA PARA CAMPAÑAS",
            "PARTICIPACION EN CAMPAÑAS DE ENTREGA DE DONACIONES",
            "PARTICIPACION EN TE ACOMPAÑO",
            "DIALOGOS DE SABERES",
            "ENCUENTROS DE SABERES PRODUCTIVOS",
            "TRASMISION INTER GENERACIONAL",
            "FERIAS DE EMPRENDIMIENTOS"
        ],
        "REUNIONES": [
            "REUNION EQUIPO UT",
            "REUNION CON SECTOR SALUD DIRESA, RIS IPRESS",
            "REUNION SABERES",
            "REUNION CON GL"
        ]
    }

    # Diccionario para almacenar las selecciones de subactividades
    respuestas = {}

    for actividad_principal, subactividades in actividades_dict.items():
        st.markdown(f"**{actividad_principal}**")
        sub_seleccionada = st.selectbox(f"Seleccione subactividad de {actividad_principal}", [""] + subactividades, key=actividad_principal)
        respuestas[actividad_principal] = sub_seleccionada

    # Otras actividades (texto libre)
    otras_actividades = st.text_area("Otras Actividades", height=100)

    # ====== BOTÓN GUARDAR ======
    if st.button("💾 Guardar registro"):
        if not ut or not codigo_usuario or not nombres or not cargo:
            st.warning("⚠️ Complete todos los datos generales antes de guardar.")
        else:
            filas = []
            for actividad, sub in respuestas.items():
                if sub:  # Solo guardar si se seleccionó alguna subactividad
                    fila = {
                        "UT": ut,
                        "Fecha": fecha.strftime("%d/%m/%Y"),
                        "Código de Usuario": codigo_usuario,
                        "Apellidos y Nombres": nombres,
                        "Cargo/Puesto": cargo,
                        "Actividad Principal": actividad,
                        "Subactividad": sub,
                        "Otras Actividades": otras_actividades
                    }
                    filas.append(fila)

            if filas:
                df_nuevo = pd.DataFrame(filas)
                if os.path.exists(ARCHIVO_EXCEL):
                    df_existente = pd.read_excel(ARCHIVO_EXCEL)
                    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
                else:
                    df_final = df_nuevo
                df_final.to_excel(ARCHIVO_EXCEL, index=False)
                st.success(f"✅ Se guardaron {len(filas)} registros correctamente")
                st.dataframe(df_nuevo)
                st.experimental_rerun()
            else:
                st.warning("⚠️ No se seleccionó ninguna subactividad para guardar.")

