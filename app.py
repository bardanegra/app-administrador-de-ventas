import streamlit as st
import pandas as pd
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# ENLACE DE TU PLANILLA DE GOOGLE SHEETS
GSHEETS_URL = "https://google.com"

# FUNCIONES PARA LEER LOS DATOS DESDE GOOGLE SHEETS
def cargar_datos_clientes():
    try:
        return pd.read_csv(GSHEETS_URL + "Clientes")
    except:
        return pd.DataFrame(columns=["Apellido", "Nombre", "Correo", "Teléfono", "Direccion", "Ciudad", "Notas"])

def cargar_datos_productos():
    try:
        return pd.read_csv(GSHEETS_URL + "Productos")
    except:
        return pd.DataFrame(columns=["Nombre", "Tamaño", "Stock", "Precio", "Costo"])

# USUARIOS PROVISORIOS
if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None
if "rol_logueado" not in st.session_state:
    st.session_state.rol_logueado = None

# --- LOGIN ---
if st.session_state.usuario_logueado is None:
    st.title("🧪 Control de Perfumería")
    st.subheader("Iniciar Sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar", type="primary"):
        if usuario == "admin" and clave == "admin123":
            st.session_state.usuario_logueado = "admin"
            st.session_state.rol_logueado = "Admin"
            st.rerun()
        elif usuario == "vendedor" and clave == "vende123":
            st.session_state.usuario_logueado = "vendedor"
            st.session_state.rol_logueado = "Vendedor"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# --- SISTEMA ADENTRO ---
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None
        st.session_state.rol_logueado = None
        st.rerun()

    # Traer datos en vivo de Google Sheets
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()

    # MENÚ PRINCIPAL EN LA BARRA DE LA IZQUIERDA
    opcion_menu = st.sidebar.radio("Ir a la ventana:", ["📋 Clientes", "📦 Productos y Stock"])

    # ==================== VENTANA 1: CLIENTES ====================
    if opcion_menu == "📋 Clientes":
        st.title("📍 Módulo de Clientes y GPS")
        tab1, tab2 = st.tabs(["Lista de Clientes", "Registrar Nuevo"])
        
        with tab1:
            st.dataframe(df_clientes, use_container_width=True)
            
            st.subheader("🗺️ GPS para Repartidor (Rutas rápidas)")
            if not df_clientes.empty:
                for index, row in df_clientes.iterrows():
                    direccion_completa = f"{row['Direccion']}, {row['Ciudad']}, Argentina"
                    link_maps = f"https://google.com{urllib.parse.quote(direccion_completa)}"
                    with st.expander(f"📍 {row['Nombre']} - {row['Ciudad']}"):
                        st.write(f"🏠 Dirección: {row['Direccion']}")
                        st.link_button("🗺️ Abrir GPS Google Maps", link_maps, type="primary")

        with tab2:
            st.subheader("Cargar nuevo cliente")
            st.text_input("Apellido")
            st.text_input("Nombre")
            st.text_input("Dirección")
            st.button("Guardar en simulación")

    # ==================== VENTANA 2: PRODUCTOS ====================
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario de Perfumes Fabricados")
        
        # Mostrar la lista de perfumes cargados en Google Sheets
        st.dataframe(df_productos, use_container_width=True)
        
        # Muestra financiero automático solo para vos (Admin)
        if rol == "Admin":
            st.subheader("📊 Reporte Financiero de Fábrica")
            try:
                # Python calcula el valor del negocio multiplicando las columnas en vivo
                total_costo = (df_productos['Stock'] * df_productos['Costo']).sum()
                total_venta = (df_productos['Stock'] * df_productos['Precio']).sum()
                ganancia = total_venta - total_costo
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Costo de Inversión", f"${total_costo:,.2f}")
                col2.metric("Valor en Estantería", f"${total_venta:,.2f}")
                col3.metric("Ganancia Esperada", f"${ganancia:,.2f}")
            except:
                st.info("Escribe números en las columnas Stock, Precio y Costo de Google Sheets para ver las finanzas.")
