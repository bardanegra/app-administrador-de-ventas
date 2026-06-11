import streamlit as st
import pandas as pd
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# ENLACE DE TU PLANILLA DE GOOGLE SHEETS
GSHEETS_URL = "https://google.com"

# FUNCIONES PARA LEER LOS DATOS DESDE GOOGLE SHEETS
def cargar_datos_clientes():
    try: return pd.read_csv(GSHEETS_URL + "Clientes")
    except: return pd.DataFrame(columns=["Apellido", "Nombre", "Correo", "Teléfono", "Direccion", "Ciudad", "Notas"])

def cargar_datos_productos():
    try: return pd.read_csv(GSHEETS_URL + "Productos")
    except: return pd.DataFrame(columns=["Nombre", "Tamaño", "Stock", "Precio", "Costo"])

def cargar_datos_usuarios():
    try: 
        # Lee los usuarios reales de tu Google Sheets
        df = pd.read_csv(GSHEETS_URL + "Usuario")
        return df
    except: 
        # Si falla, deja estos de respaldo para que no te quedes afuera
        return pd.DataFrame([{"Usuario": "admin", "Clave": "admin123", "Rol": "Admin"}])

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
        # Verificamos si el usuario existe en tu Google Sheets
        user_row = df_usuarios[df_usuarios['Usuario'] == usuario_ingresado]
        if not user_row.empty and str(user_row.iloc[0]['Clave']) == clave_ingresada:
            st.session_state.usuario_logueado = usuario_ingresado
            st.session_state.rol_logueado = user_row.iloc[0]['Rol']
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None; st.session_state.rol_logueado = None; st.rerun()

    # Cargar datos generales
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()

    # MENÚ ADAPTADO AL ROL
    opciones = ["📋 Clientes", "📦 Productos y Stock", "💰 Caja Registradora / Ventas"]
    if rol == "Admin":
        opciones.append("👥 Gestión de Empleados") # Opción exclusiva para vos
    
    opcion_menu = st.sidebar.radio("Ir a la ventana:", opciones)

    # ==================== VENTANA: CLIENTES ====================
    if opcion_menu == "📋 Clientes":
        st.title("📍 Lista de Clientes Registrados")
        st.dataframe(df_clientes, use_container_width=True)

    # ==================== VENTANA: PRODUCTOS ====================
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario de Perfumes")
        st.dataframe(df_productos, use_container_width=True)

    # ==================== VENTANA: CAJA REGISTRADORA ====================
    elif opcion_menu == "💰 Caja Registradora / Ventas":
        st.title("💰 Caja Registradora")
        st.write("Módulo de ventas activo.")

    # ==================== VENTANA EXCLUSIVA: GESTIÓN DE EMPLEADOS (NUEVA) ====================
    elif opcion_menu == "👥 Gestión de Empleados" and rol == "Admin":
        st.title("👥 Control de Personal y Contraseñas")
        
        tab1, tab2 = st.tabs(["🔒 Ver y Controlar Empleados", "➕ Dar de Alta Nuevo Empleado"])
        
        with tab1:
            st.subheader("Lista de cuentas activas en Google Sheets")
            # Te muestra la tabla de quiénes tienen acceso y podés ver sus claves de Sheets
            st.dataframe(df_usuarios, use_container_width=True)
            
            st.write("---")
            st.subheader("🔑 Cambiar clave o resetear cuenta")
            empleado_sel = st.selectbox("Seleccione el empleado a modificar", df_usuarios['Usuario'].values)
            nueva_clave = st.text_input("Nueva contraseña para este usuario", type="password")
            if st.button("Aplicar nuevo cambio de contraseña"):
                st.success(f"Contraseña de '{empleado_sel}' procesada. En el próximo paso se grabará directo en el Sheets.")

        with tab2:
            st.subheader("Crear un nuevo Vendedor o Repartidor")
            nuevo_user = st.text_input("Nombre de Usuario (ej: vendedora_maria)")
            nueva_pass = st.text_input("Contraseña Inicial", type="password")
            nuevo_rol = st.selectbox("Asignar Rol de Trabajo", ["Vendedor", "Repartidor"])
            
            if st.button("Crear cuenta de empleado", type="primary"):
                st.success(f"¡Usuario '{nuevo_user}' procesado con el rol de {nuevo_rol}!")
                st.info("Nota: Cuando configuremos la escritura, este botón agregará la fila automáticamente a tu Google Sheets.")
