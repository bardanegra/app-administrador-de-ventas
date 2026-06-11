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

def cargar_datos_entregas():
    try: return pd.read_csv(GSHEETS_URL + "stock")
    except: return pd.DataFrame(columns=["ID_Pedido", "Cliente", "Dirección", "Repartidor", "Estado"])

# CONTROL DE SESIÓN PROVISORIO
if "usuario_logueado" not in st.session_state: st.session_state.usuario_logueado = None
if "rol_logueado" not in st.session_state: st.session_state.rol_logueado = None

# --- LOGIN ---
if st.session_state.usuario_logueado is None:
    st.title("🧪 Control de Perfumería")
    st.subheader("Iniciar Sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Ingresar", type="primary"):
        if usuario == "admin" and clave == "admin123":
            st.session_state.usuario_logueado = "admin"; st.session_state.rol_logueado = "Admin"; st.rerun()
        elif usuario == "vendedor" and clave == "vende123":
            st.session_state.usuario_logueado = "vendedor"; st.session_state.rol_logueado = "Vendedor"; st.rerun()
        elif usuario == "repartidor" and clave == "reparte123":
            st.session_state.usuario_logueado = "repartidor"; st.session_state.rol_logueado = "Repartidor"; st.rerun()
        else: st.error("Usuario o contraseña incorrectos")
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None; st.session_state.rol_logueado = None; st.rerun()

    # Cargar datos en vivo de todas las pestañas de Google Sheets
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()
    df_ventas = cargar_datos_ventas()
    df_entregas = cargar_datos_entregas()

    # MENÚ ADAPTADO AL ROL DEL USUARIO
    if rol == "Repartidor":
        opcion_menu = st.sidebar.radio("Ir a la ventana:", ["🚚 Mis Entregas (GPS)"])
    else:
        opcion_menu = st.sidebar.radio("Ir a la ventana:", ["📋 Clientes", "📦 Productos y Stock", "💰 Caja Registradora / Ventas", "🚚 Coordinar Entregas"])

    # ==================== VENTANA: CLIENTES ====================
    if opcion_menu == "📋 Clientes":
        st.title("📍 Lista de Clientes Registrados")
        st.dataframe(df_clientes, use_container_width=True)

    # ==================== VENTANA: PRODUCTOS ====================
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario de Perfumes")
        st.dataframe(df_productos, use_container_width=True)
        if rol == "Admin":
            st.subheader("📊 Reporte Financiero de Fábrica")
            try:
                total_costo = (df_productos['Stock'] * df_productos['Costo']).sum()
                total_venta = (df_productos['Stock'] * df_productos['Precio']).sum()
                st.columns(3).metric("Costo Inversión", f"${total_costo:,.2f}")
                st.columns(3).metric("Valor Estantería", f"${total_venta:,.2f}")
                st.columns(3).metric("Ganancia Esperada", f"${total_venta - total_costo:,.2f}")
            except: st.info("Agrega costos y precios en Google Sheets para activar los gráficos financieros.")

    # ==================== VENTANA: CAJA REGISTRADORA ====================
    elif opcion_menu == "💰 Caja Registradora / Ventas":
        st.title("💰 Caja Registradora")
        lista_clientes = [f"{r['Nombre']} {r['Apellido']}" for i, r in df_clientes.iterrows()] if not df_clientes.empty else ["Cliente General"]
        lista_perfumes = [r['Nombre'] for i, r in df_productos.iterrows()] if not df_productos.empty else ["No hay perfumes"]
        
        v_cliente = st.selectbox("Seleccione el Cliente", lista_clientes)
        v_producto = st.selectbox("Seleccione el Perfume", lista_perfumes)
        v_cantidad = st.number_input("Cantidad", min_value=1, value=1)
        
        precio_unitario = 0.0
        if not df_productos.empty and v_producto in df_productos['Nombre'].values:
            precio_unitario = float(df_productos[df_productos['Nombre'] == v_producto]['Precio'].values)
        
        st.info(f"**Total a Cobrar: ${v_cantidad * precio_unitario:,.2f}**")
        v_medio = st.selectbox("Método de Pago", ["Efectivo 💵", "Tarjeta de Débito 💳", "Crédito 💳", "Transferencia 🏦", "MercadoPago 📱"])
        v_tipo = st.radio("Modalidad de Entrega", ["Presencial / Local", "Online (Requiere envío)"])
        
        if st.button("Confirmar Transacción", type="primary"):
            st.success("¡Venta procesada con éxito! Operación registrada en el sistema simulado.")
            st.balloons()

    # ==================== VENTANA: COORDINAR ENTREGAS (ADMIN Y VENDEDOR) ====================
    elif opcion_menu == "🚚 Coordinar Entregas":
        st.title("🚚 Coordinación Logística de Envíos")
        st.subheader("Historial General de Repartos")
        if df_entregas.empty:
            st.info("No hay entregas registradas en la pestaña 'stock' de Google Sheets.")
        else:
            st.dataframe(df_entregas, use_container_width=True)
            
        st.subheader("Asignar Repartidor a Envíos Pendientes")
        st.write("Aquí el vendedor podrá elegir qué repartidor lleva cada paquete con un clic.")

    # ==================== VENTANA: MIS ENTREGAS (REPARTIDOR) ====================
    elif opcion_menu == "🚚 Mis Entregas (GPS)":
        st.title("🚗 Hoja de Ruta del Repartidor")
        st.subheader("Envíos Asignados para Entrega")
        
        if df_clientes.empty:
            st.info("No tienes entregas pendientes asignadas para el día de hoy.")
        else:
            st.write("Haz clic en el botón de cada cliente para abrir el GPS en tu celular:")
            for index, row in df_clientes.iterrows():
                direccion_completa = f"{row['Direccion']}, {row['Ciudad']}, Argentina"
                link_maps = f"https://google.com{urllib.parse.quote(direccion_completa)}"
                
                with st.expander(f"📦 Entrega para: {row['Nombre']} {row['Apellido']} ({row['Ciudad']})"):
                    st.write(f"🏠 **Dirección:** {row['Direccion']}")
                    st.write(f"📝 **Notas de envío:** {row['Notas']}")
                    st.link_button("🗺️ Abrir en Google Maps / GPS", link_maps, type="primary")
                    st.button("✅ Marcar como Entregado", key=f"entregado_{index}")
