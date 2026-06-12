import streamlit as st
import pandas as pd
import requests
import json
import random
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

st.title("🧪 Control de Perfumería")

# ENLACES REALES DE TU PLANILLA DE GOOGLE SHEETS
GSHEETS_URL = "https://google.com"
SCRIPT_URL = "https://google.com"

# FUNCIONES DE LECTURA REALES CON ROMPE-CACHÉ
def cargar_datos_usuarios():
    try: 
        # El número aleatorio obliga a Google a dar los datos nuevos sin guardarse copias viejas
        url = f"{GSHEETS_URL}Usuario&cache_buster={random.randint(1, 100000)}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except: 
        return pd.DataFrame([{"usuario": "admin", "clave": "admin123", "rol": "Admin"}])

def cargar_datos_clientes():
    try:
        url = f"{GSHEETS_URL}Clientes&cache_buster={random.randint(1, 100000)}"
        return pd.read_csv(url)
    except: return pd.DataFrame(columns=["Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Notas"])

# FUNCIÓN MÁGICA DE ESCRITURA REAL
def guardar_en_google_sheets(pestaña, datos_lista):
    try:
        url_final = f"{SCRIPT_URL}?sheet={pestaña}"
        headers = {"Content-Type": "application/json"}
        respuesta = requests.post(url_final, data=json.dumps(datos_lista), headers=headers, timeout=15)
        if respuesta.status_code == 200: return True
        return False
    except: return False

# CONTROL DE SESIÓN
if "usuario_logueado" not in st.session_state: st.session_state.usuario_logueado = None
if "rol_logueado" not in st.session_state: st.session_state.rol_logueado = None

df_usuarios = cargar_datos_usuarios()

# --- LOGIN ---
if st.session_state.usuario_logueado is None:
    st.subheader("Iniciar Sesión")
    usuario_ingresado = st.text_input("Usuario")
    clave_ingresada = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar", type="primary"):
        u_limpio = str(usuario_ingresado).strip().lower()
        c_limpia = str(clave_ingresada).strip()
        
        if u_limpio == "admin" and c_limpia == "admin123":
            st.session_state.usuario_logueado = "admin"
            st.session_state.rol_logueado = "Admin"
            st.rerun()
            
        elif not df_usuarios.empty and "usuario" in df_usuarios.columns and "clave" in df_usuarios.columns:
            df_usuarios['usuario'] = df_usuarios['usuario'].astype(str).str.strip().str.lower()
            df_usuarios['clave'] = df_usuarios['clave'].astype(str).str.strip()
            
            user_row = df_usuarios[df_usuarios['usuario'] == u_limpio]
            
            if not user_row.empty and str(user_row.iloc[0]['clave']) == c_limpia:
                st.session_state.usuario_logueado = u_limpio
                st.session_state.rol_logueado = user_row.iloc[0]['rol']
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
        else: st.error("Usuario o contraseña incorrectos")
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None; st.session_state.rol_logueado = None; st.rerun()

    # Volvemos a leer los datos frescos
    df_usuarios = cargar_datos_usuarios()
    df_clientes = cargar_datos_clientes()

    opciones = ["📋 Clientes"]
    if rol == "Admin": opciones.append("👥 Gestión de Empleados")
    opcion_menu = st.sidebar.radio("Ir a la ventana:", opciones)
    ciudades_argentina = ["Neuquén", "Plottier", "Cipolletti", "Centenario", "General Roca", "Cutral Co"]

    # ==================== GESTIÓN DE EMPLEADOS ====================
    if opcion_menu == "👥 Gestión de Empleados" and rol == "Admin":
        st.header("👥 Control de Personal")
        tab1, tab2 = st.tabs(["🔒 Empleados Actuales", "➕ Dar de Alta"])
        
        with tab1:
            st.dataframe(df_usuarios, use_container_width=True)

        with tab2:
            st.subheader("Crear cuenta de empleado real")
            nuevo_user = st.text_input("Nombre de Usuario (sin espacios)")
            nueva_pass = st.text_input("Contraseña", type="password")
            nuevo_rol = st.selectbox("Rol", ["Vendedor", "Repartidor"])
            
            if st.button("Guardar Empleado en Google Sheets", type="primary"):
                if nuevo_user and nueva_pass:
                    nueva_fila = [nuevo_user.strip().lower(), nueva_pass.strip(), nuevo_rol]
                    with st.spinner("Guardando en Google Sheets..."):
                        if guardar_en_google_sheets("Usuario", nueva_fila):
                            st.success(f"✅ ¡CUENTA CREADA! El empleado '{nuevo_user}' se guardó correctamente.")
                            st.balloons()
                            st.rerun()
                        else: st.error("🛑 Error técnico de conexión con el puente.")
                        
    # ==================== CLIENTES ====================
    elif opcion_menu == "📋 Clientes":
        st.header("📍 Módulo de Clientes")
        st.dataframe(df_clientes, use_container_width=True)
