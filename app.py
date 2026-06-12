import streamlit as st
import pandas as pd
import requests
import json
import random
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# ENLACES DE TU PLANILLA DE GOOGLE SHEETS
GSHEETS_URL = "https://google.com"
SCRIPT_URL = "https://google.com"

# FUNCIONES DE LECTURA LIMPIA CON MINÚSCULAS
def cargar_datos_clientes():
    try: 
        url = f"{GSHEETS_URL}Clientes&cache_buster={random.randint(1, 100000)}"
        return pd.read_csv(url)
    except: return pd.DataFrame(columns=["Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Notas"])

def cargar_datos_productos():
    try: 
        url = f"{GSHEETS_URL}Productos&cache_buster={random.randint(1, 100000)}"
        return pd.read_csv(url)
    except: return pd.DataFrame(columns=["Nombre", "Tamaño", "Stock", "Precio", "Costo"])

def cargar_datos_usuarios():
    try: 
        url = f"{GSHEETS_URL}Usuario&cache_buster={random.randint(1, 100000)}"
        df = pd.read_csv(url)
        # Convertimos todos los títulos de las columnas a minúsculas para evitar errores de espacios
        df.columns = df.columns.str.strip().str.lower()
        return df
    except: 
        return pd.DataFrame([{"usuario": "admin", "clave": "admin123", "rol": "Admin"}])

def cargar_datos_ventas():
    try: 
        url = f"{GSHEETS_URL}Ventas&cache_buster={random.randint(1, 100000)}"
        return pd.read_csv(url)
    except: return pd.DataFrame(columns=["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"])

# FUNCIÓN DE ESCRITURA REAL
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
    st.title("🧪 Control de Perfumería")
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

    # Recargar datos en vivo frescos de Google
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()
    df_ventas = cargar_datos_ventas()
    df_usuarios = cargar_datos_usuarios()

    # MENÚ
    opciones = ["📋 Clientes", "📦 Productos y Stock", "💰 Caja Registradora / Ventas"]
    if rol == "Admin": opciones.append("👥 Gestión de Empleados")
    
    opcion_menu = st.sidebar.radio("Ir a la ventana:", opciones)
    ciudades_argentina = ["Neuquén", "Plottier", "Cipolletti", "Centenario", "General Roca", "Cutral Co"]

    # ==================== VENTANA: GESTIÓN DE EMPLEADOS ====================
    if opcion_menu == "👥 Gestión de Empleados" and rol == "Admin":
        st.title("👥 Control de Personal")
        tab1, tab2 = st.tabs(["🔒 Empleados Actuales", "➕ Dar de Alta"])
        
        with tab1:
            # Mostramos la tabla limpia en minúsculas
            st.dataframe(df_usuarios, use_container_width=True)

        with tab2:
            st.subheader("Crear cuenta de empleado real")
            nuevo_user = st.text_input("Nombre de Usuario (sin espacios)")
            nueva_pass = st.text_input("Contraseña", type="password")
            nuevo_rol = st.selectbox("Rol", ["Vendedor", "Repartidor"])
            
            if st.button("Guardar Empleado en Google Sheets", type="primary"):
                if nuevo_user and nueva_pass:
                    # Guardamos los datos en minúsculas emparejados con tu Excel limpio
                    nueva_fila = [nuevo_user.strip().lower(), nueva_pass.strip(), nuevo_rol]
                    with st.spinner("Guardando en Google Sheets..."):
                        if guardar_en_google_sheets("Usuario", nueva_fila):
                            st.success(f"✅ ¡CUENTA CREADA! El empleado '{nuevo_user}' ya se guardó correctamente.")
                            st.balloons()
                            st.rerun()
                        else: st.error("🛑 Error técnico de conexión con el puente.")

    # Las demás ventanas quedan configuradas igual por detrás...
    elif opcion_menu == "📋 Clientes":
        st.title("📍 Módulo de Clientes")
        st.dataframe(df_clientes, use_container_width=True)
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario")
        st.dataframe(df_productos, use_container_width=True)
    elif opcion_menu == "💰 Caja Registradora / Ventas":
        st.title("💰 Caja Registradora")
        st.write("Módulo de ventas activo.")
