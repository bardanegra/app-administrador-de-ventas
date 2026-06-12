import streamlit as st
import pandas as pd
import requests
import random

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

st.title("🧪 Control de Perfumería")

# ENLACE DE LECTURA DE TU EXCEL
GSHEETS_URL = "https://google.com"

# FORMULARIO DE GOOGLE DIRECTO (Elimina el puente de Apps Script que daba error)
FORM_URL = "https://google.com"

def cargar_datos_usuarios():
    try: 
        url = f"{GSHEETS_URL}Usuario&cache_buster={random.randint(1, 100000)}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except: 
        return pd.DataFrame([{"usuario": "admin", "clave": "admin123", "rol": "Admin"}])

# CONTROL DE SESIÓN
if "usuario_logueado" not in st.session_state: st.session_state.usuario_logueado = None

df_usuarios = cargar_datos_usuarios()

if st.session_state.usuario_logueado is None:
    st.subheader("Iniciar Sesión")
    usuario_ingresado = st.text_input("Usuario")
    clave_ingresada = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar", type="primary"):
        u_limpio = str(usuario_ingresado).strip().lower()
        c_limpia = str(clave_ingresada).strip()
        
        if u_limpio == "admin" and c_limpia == "admin123":
            st.session_state.usuario_logueado = "admin"
            st.rerun()
        elif not df_usuarios.empty and "usuario" in df_usuarios.columns:
            df_usuarios['usuario'] = df_usuarios['usuario'].astype(str).str.strip().str.lower()
            df_usuarios['clave'] = df_usuarios['clave'].astype(str).str.strip()
            user_row = df_usuarios[df_usuarios['usuario'] == u_limpio]
            
            if not user_row.empty and str(user_row.iloc[0]['clave']) == c_limpia:
                st.session_state.usuario_logueado = u_limpio
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
else:
    st.sidebar.title(f"👤 ADMINISTRADORA")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None; st.rerun()

    df_usuarios = cargar_datos_usuarios()
    
    st.header("👥 Control de Personal")
    tab1, tab2 = st.tabs(["🔒 Empleados Actuales", "➕ Dar de Alta"])
    
    with tab1:
        st.dataframe(df_usuarios, use_container_width=True)

    with tab2:
        st.subheader("Crear cuenta de empleado real")
        nuevo_user = st.text_input("Nombre de Usuario")
        nueva_pass = st.text_input("Contraseña", type="password")
        nuevo_rol = st.selectbox("Rol", ["Vendedor", "Repartidor"])
        
        if st.button("Guardar Empleado", type="primary"):
            if nuevo_user and nueva_pass:
                # Datos del formulario directo de Google para inyectar la fila
                form_data = {
                    'entry.1345678901': nuevo_user.strip().lower(),
                    'entry.2345678902': nueva_pass.strip(),
                    'entry.3456789003': nuevo_rol
                }
                with st.spinner("Guardando..."):
                    try:
                        requests.post(FORM_URL, data=form_data, timeout=10)
                        st.success(f"✅ ¡CUENTA CREADA EXITOSAMENTE!")
                        st.balloons()
                        st.rerun()
                    except:
                        st.error("Error al registrar.")
