import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

st.title("🧪 Control de Perfumería")

# ENLACE OFICIAL DE TU GOOGLE SHEETS
URL_EXCEL = "https://google.com"

try:
    # Encendemos el conector nativo de Streamlit
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    if "logueado" not in st.session_state:
        st.session_state.logueado = False

    if not st.session_state.logueado:
        st.subheader("Iniciar Sesión")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary"):
            if usuario == "admin" and clave == "admin123":
                st.session_state.logueado = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    else:
        st.sidebar.title("👤 ADMINISTRADORA")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.logueado = False
            st.rerun()
            
        st.header("👥 Gestión de Empleados")
        tab1, tab2 = st.tabs(["🔒 Ver Empleados", "➕ Dar de Alta Nuevo"])
        
        with tab1:
            st.subheader("Cuentas leídas en tiempo real desde Google Drive")
            try:
                # Lee tu pestaña Usuario de forma nativa sin pasar por Apps Script
                df_usuarios = conn.read(spreadsheet=URL_EXCEL, worksheet="Usuario", ttl=0)
                st.dataframe(df_usuarios, use_container_width=True)
            except:
                st.info("Aún no hay datos cargados en tu Google Sheets.")
                
        with tab2:
            st.subheader("Crear cuenta de empleado real")
            nuevo_user = st.text_input("Nombre de Usuario (sin espacios)")
            nueva_pass = st.text_input("Contraseña")
            nuevo_rol = st.selectbox("Rol", ["Vendedor", "Repartidor"])
            
            if st.button("Guardar Empleado en Google Sheets", type="primary"):
                if nuevo_user and nueva_pass:
                    with st.spinner("Guardando directamente en tu Google Drive..."):
                        # Creamos el nuevo registro
                        nueva_fila = pd.DataFrame([{"usuario": nuevo_user.strip().lower(), "clave": nueva_pass.strip(), "rol": nuevo_rol}])
                        
                        # Leemos lo que ya existe para no pisar nada
                        try: df_actual = conn.read(spreadsheet=URL_EXCEL, worksheet="Usuario", ttl=0)
                        except: df_actual = pd.DataFrame(columns=["usuario", "clave", "rol"])
                        
                        # Unimos el viejo listado con el nuevo empleado
                        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        
                        # Guardamos directo en tu archivo de Google Drive
                        conn.update(spreadsheet=URL_EXCEL, worksheet="Usuario", data=df_final)
                        
                        st.success(f"✅ ¡ÉXITO TOTAL! El empleado '{nuevo_user}' se guardó en tu Excel.")
                        st.balloons()
                        st.rerun()
                else:
                    st.warning("Completa el usuario y la contraseña.")
except Exception as e:
    st.error("Instalando los motores de conexión con tu Google Drive...")
