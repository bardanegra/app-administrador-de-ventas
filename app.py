import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

st.title("🧪 Control de Perfumería")

# CONEXIÓN DIRECTA Y NATIVA A TU GOOGLE SHEETS
# Reemplaza la dirección de abajo por el link completo de tu planilla de Google Sheets
URL_TU_EXCEL = "https://google.com"

try:
    # Usamos el motor oficial de Streamlit para conectar planillas
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # CONTROL DE INICIO DE SESIÓN SIMPLIFICADO DE RESPALDO
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
            st.subheader("Cuentas actuales leídas desde Google Drive")
            try:
                # Leemos la pestaña de usuarios directamente de forma nativa
                df_usuarios = conn.read(spreadsheet=URL_TU_EXCEL, worksheet="Usuario")
                st.dataframe(df_usuarios, use_container_width=True)
            except:
                st.info("Aún no hay datos cargados en la pestaña Usuario de tu Google Sheets.")
                
        with tab2:
            st.subheader("Crear cuenta de empleado real")
            nuevo_user = st.text_input("Nombre de Usuario (sin espacios)")
            nueva_pass = st.text_input("Contraseña")
            nuevo_rol = st.selectbox("Rol", ["Vendedor", "Repartidor"])
            
            if st.button("Guardar Empleado en Google Sheets", type="primary"):
                if nuevo_user and nueva_pass:
                    try:
                        # Creamos la nueva fila con los datos ingresados
                        nueva_fila = pd.DataFrame([{"Usuario": nuevo_user, "Clave": nueva_pass, "Rol": nuevo_rol}])
                        
                        # Leemos lo que ya hay en la pestaña para no borrar nada
                        try: df_actual = conn.read(spreadsheet=URL_TU_EXCEL, worksheet="Usuario")
                        except: df_actual = pd.DataFrame(columns=["Usuario", "Clave", "Rol"])
                        
                        # Unimos el empleado nuevo al listado existente
                        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        
                        # ORDEN MÁGICA: Python escribe directamente en tu Google Drive sin Apps Script
                        conn.update(spreadsheet=URL_TU_EXCEL, worksheet="Usuario", data=df_final)
                        
                        # CONFIRMACIÓN VISUAL CON GLOBOS
                        st.success(f"✅ ¡ÉXITO TOTAL! El empleado '{nuevo_user}' se guardó directamente en tu Excel.")
                        st.balloons()
                    except Exception as error_guardado:
                        st.error(f"🛑 Error de permisos de Google. Asegúrate de que el Excel esté compartido como 'Cualquier persona con el enlace'.")
                else:
                    st.warning("Completa el usuario y la contraseña.")
except Exception as e:
    st.error("Configurando los motores de conexión internos de la base de datos...")
