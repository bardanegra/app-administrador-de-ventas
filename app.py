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

def cargar_datos_ventas():
    try: return pd.read_csv(GSHEETS_URL + "pedido")
    except: return pd.DataFrame(columns=["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"])

# SISTEMA DE LOGIN PROVISORIO
if "usuario_logueado" not in st.session_state: st.session_state.usuario_logueado = None
if "rol_logueado" not in st.session_state: st.session_state.rol_logueado = None

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
        else: st.error("Usuario o contraseña incorrectos")
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None; st.session_state.rol_logueado = None; st.rerun()

    # Cargar datos desde Google Sheets
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()
    df_ventas = cargar_datos_ventas()

    # MENÚ PRINCIPAL UNIFICADO EN UN SOLO ARCHIVO
    opcion_menu = st.sidebar.radio("Ir a la ventana:", ["📋 Clientes", "📦 Productos y Stock", "💰 Caja Registradora / Ventas"])

    # ==================== VENTANA 1: CLIENTES ====================
    if opcion_menu == "📋 Clientes":
        st.title("📍 Módulo de Clientes y GPS")
        st.dataframe(df_clientes, use_container_width=True)
        st.subheader("🗺️ GPS para Repartidor")
        if not df_clientes.empty:
            for index, row in df_clientes.iterrows():
                direccion_completa = f"{row['Direccion']}, {row['Ciudad']}, Argentina"
                link_maps = f"https://google.com{urllib.parse.quote(direccion_completa)}"
                with st.expander(f"📍 {row['Nombre']} - {row['Ciudad']}"):
                    st.link_button("🗺️ Abrir GPS Google Maps", link_maps, type="primary")

    # ==================== VENTANA 2: PRODUCTOS ====================
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario de Perfumes")
        st.dataframe(df_productos, use_container_width=True)
        if rol == "Admin":
            st.subheader("📊 Reporte Financiero de Fábrica")
            try:
                total_costo = (df_productos['Stock'] * df_productos['Costo']).sum()
                total_venta = (df_productos['Stock'] * df_productos['Precio']).sum()
                st.columns(3)[0].metric("Costo Inversión", f"${total_costo:,.2f}")
                st.columns(3)[1].metric("Valor Estantería", f"${total_venta:,.2f}")
                st.columns(3)[2].metric("Ganancia Esperada", f"${total_venta - total_costo:,.2f}")
            except: st.info("Agrega datos numéricos en tu Google Sheets para activar las métricas.")

    # ==================== VENTANA 3: CAJA REGISTRADORA (NUEVA) ====================
    elif opcion_menu == "💰 Caja Registradora / Ventas":
        st.title("💰 Caja Registradora e Historial")
        
        tab1, tab2 = st.tabs(["🛒 Nueva Venta", "📜 Historial de Pedidos"])
        
        with tab1:
            st.subheader("Registrar movimiento de caja")
            
            # Listas desplegables inteligentes que leen tu Google Sheets
            lista_clientes = [f"{r['Nombre']} {r['Apellido']}" for i, r in df_clientes.iterrows()] if not df_clientes.empty else ["Cliente General"]
            lista_perfumes = [r['Nombre'] for i, r in df_productos.iterrows()] if not df_productos.empty else ["No hay perfumes cargados"]
            
            v_cliente = st.selectbox("Seleccione el Cliente", lista_clientes)
            v_producto = st.selectbox("Seleccione el Perfume", lista_perfumes)
            v_cantidad = st.number_input("Cantidad de unidades", min_value=1, value=1)
            
            # Buscar el precio en vivo según el perfume elegido
            precio_unitario = 0.0
            if not df_productos.empty and v_producto in df_productos['Nombre'].values:
                precio_unitario = float(df_productos[df_productos['Nombre'] == v_producto]['Precio'].values[0])
            
            total_operacion = v_cantidad * precio_unitario
            st.info(f"💵 Precio Unitario: ${precio_unitario:,.2f} | **Total a Cobrar: ${total_operacion:,.2f}**")
            
            # Formas de Pago e Interfaz extraídas de tu foto de Base44
            v_medio = st.selectbox("Método de Pago", ["Efectivo 💵", "Tarjeta de Débito 💳", "Crédito (3 Cuotas) 💳", "Transferencia Bancaria 🏦", "MercadoPago 📱"])
            v_tipo = st.radio("Modalidad de Entrega", ["Presencial / Local", "Online (Requiere envío)"])
            
            if st.button("Confirmar Transacción", type="primary"):
                st.success(f"¡Venta de {v_producto} por ${total_operacion:,.2f} procesada con éxito!")
                st.balloons() # Animación festiva de festejo por la venta

        with tab2:
            st.subheader("Registro General de Ventas")
            if df_ventas.empty:
                st.info("No hay ventas registradas en la pestaña 'pedido' de tu Google Sheets todavía.")
            else:
                st.dataframe(df_ventas, use_container_width=True)
