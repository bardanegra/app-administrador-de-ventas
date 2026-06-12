import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Sistema de Gestión - Fábrica de Perfumes",
    page_icon="🧪",
    layout="wide"
)

# =============================================================================
# VARIABLES DE CONFIGURACIÓN Y ENLACES (GOOGLE SHEETS / FORMS)
# =============================================================================
GSHEET_BASE_URL = "https://google.com" 
GOOGLE_FORM_USUARIO_URL = "https://google.com"

CIUDADES_ENTREGA = ["Neuquén", "Plottier", "Cipolletti", "Centenario", "General Roca", "Cutral Co"]
MEDIOS_PAGO = ["Efectivo 💵", "Tarjeta de Débito 💳", "Crédito (3 Cuotas) 💳", "Transferencia Bancaria 🏦", "MercadoPago 📱"]
TIPOS_VENTA = ["Presencial / Local", "Online (Requiere envío)", "Manual vendedor"]

# =============================================================================
# FUNCIONES AUXILIARES: LECTURA CON CACHE-BUSTER Y ESCRITURA FORMS
# =============================================================================
def cargar_datos_pestana(nombre_pestana):
    cb = random.randint(100000, 999999)
    url_final = f"{GSHEET_BASE_URL}?sheet={nombre_pestana}&nocache={cb}"
    try:
        columnas_dict = {
            "Usuario": ["usuario", "clave", "rol"],
            "Clientes": ["Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Notas"],
            "Productos": ["Nombre", "Tamaño", "Stock_Lab", "Stock_Tienda", "Precio", "Costo", "Fecha_Creacion", "Dias_Maceracion"],
            "Ventas": ["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"],
            "Entrega": ["ID_Pedido", "Cliente", "Dirección", "Repartidor", "Estado"],
            "Traspasos": ["ID_Traspaso", "Producto", "Cantidad", "Vendedora", "Estado"],
            "Movimientos": ["ID_Movimiento", "Fecha_Hora", "Usuario", "Detalle"]
        }
        return pd.DataFrame(columns=columnas_dict.get(nombre_pestana, []))
    except Exception:
        columnas_dict = {
            "Usuario": ["usuario", "clave", "rol"],
            "Clientes": ["Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Notas"],
            "Productos": ["Nombre", "Tamaño", "Stock_Lab", "Stock_Tienda", "Precio", "Costo", "Fecha_Creacion", "Dias_Maceracion"],
            "Ventas": ["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"],
            "Entrega": ["ID_Pedido", "Cliente", "Dirección", "Repartidor", "Estado"],
            "Traspasos": ["ID_Traspaso", "Producto", "Cantidad", "Vendedora", "Estado"],
            "Movimientos": ["ID_Movimiento", "Fecha_Hora", "Usuario", "Detalle"]
        }
        return pd.DataFrame(columns=columnas_dict.get(nombre_pestana, []))

# =============================================================================
# MANEJO DEL ESTADO DE LA SESIÓN (AUTENTICACIÓN Y BASE DE DATOS SIMULADA)
# =============================================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None
if "rol_logueado" not in st.session_state:
    st.session_state["rol_logueado"] = None

# Contadores de auditoría regulatoria (Folios Correlativos)
if "correlativo_os" not in st.session_state:
    st.session_state["correlativo_os"] = 4000
if "correlativo_ot" not in st.session_state:
    st.session_state["correlativo_ot"] = 5000

# Almacenamiento Remoto / Local Simulado
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = pd.DataFrame([
        {"usuario": "admin", "clave": "admin123", "rol": "Administradora"},
        {"usuario": "vane", "clave": "vane123", "rol": "Vendedor"},
        {"usuario": "repa_juan", "clave": "juan123", "rol": "Repartidor"},
        {"usuario": "repa_pedro", "clave": "pedro123", "rol": "Repartidor"}
    ])
if "db_clientes" not in st.session_state:
    st.session_state["db_clientes"] = pd.DataFrame(columns=["Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Notas"])
if "db_productos" not in st.session_state:
    st.session_state["db_productos"] = pd.DataFrame([
        {"Nombre": "Perfume Nuit", "Tamaño": "100ml", "Stock_Lab": 50, "Stock_Tienda": 10, "Precio": 15000.0, "Costo": 6000.0, "Fecha_Creacion": "2026-06-01", "Dias_Maceracion": 5},
        {"Nombre": "Esencia Floral", "Tamaño": "50ml", "Stock_Lab": 30, "Stock_Tienda": 5, "Precio": 9500.0, "Costo": 3500.0, "Fecha_Creacion": "2026-06-11", "Dias_Maceracion": 10}
    ])
if "db_ventas" not in st.session_state:
    st.session_state["db_ventas"] = pd.DataFrame(columns=["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"])
if "db_entrega" not in st.session_state:
    st.session_state["db_entrega"] = pd.DataFrame(columns=["ID_Pedido", "Cliente", "Dirección", "Repartidor", "Estado"])
if "db_traspasos" not in st.session_state:
    st.session_state["db_traspasos"] = pd.DataFrame(columns=["ID_Traspaso", "Producto", "Cantidad", "Vendedora", "Estado"])
if "db_movimientos" not in st.session_state:
    st.session_state["db_movimientos"] = pd.DataFrame(columns=["ID_Movimiento", "Fecha_Hora", "Usuario", "Detalle"])

# Estado de notificación para ventana emergente
if "notificacion_emergente" not in st.session_state:
    st.session_state["notificacion_emergente"] = None

# =============================================================================
# DETECTAR MOVIMIENTO Y ENVIAR ALERTA EMERGENTE
# =============================================================================
def registrar_movimiento(detalle_movimiento):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = st.session_state["usuario_logueado"] if st.session_state["usuario_logueado"] else "Sistema"
    id_m = f"MOV-{random.randint(10000,99999)}"
    
    nuevo_mov = {"ID_Movimiento": id_m, "Fecha_Hora": ahora, "Usuario": usuario, "Detalle": detalle_movimiento}
    st.session_state["db_movimientos"] = pd.concat([st.session_state["db_movimientos"], pd.DataFrame([nuevo_mov])], ignore_index=True)
    
    st.session_state["notificacion_emergente"] = {
        "fecha_hora": ahora,
        "usuario": usuario,
        "detalle": detalle_movimiento
    }

@st.dialog("🔔 Alerta de Movimiento de Sistema")
def mostrar_modal_notificacion(datos):
    st.markdown(f"### **¡Operación Ejecutada con Éxito!**")
    st.write(f"📅 **Fecha y Hora:** {datos['fecha_hora']}")
    st.write(f"👤 **Usuario Actante:** {datos['usuario']}")
    st.info(f"📝 **Detalle del Movimiento:**\n{datos['detalle']}")
    if st.button("Entendido / Cerrar", use_container_width=True):
        st.session_state["notificacion_emergente"] = None
        st.rerun()

if st.session_state["notificacion_emergente"] is not None:
    mostrar_modal_notificacion(st.session_state["notificacion_emergente"])

# =============================================================================
# INTERFAZ DE LOGIN
# =============================================================================
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns()
    with col2:
        st.title("🧪 Fábrica de Perfumes")
        st.subheader("Control Operacional de Planta")
        input_usuario = st.text_input("Usuario")
        input_clave = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar Sistema", use_container_width=True):
            df_usuarios_total = st.session_state["db_usuarios"]
            coincidencia = df_usuarios_total[
                (df_usuarios_total["usuario"] == input_usuario) & 
                (df_usuarios_total["clave"] == input_clave)
            ]
            
            if not coincidencia.empty:
                rol_encontrado = coincidencia.iloc[0]["rol"]
                st.session_state["autenticado"] = True
                st.session_state["usuario_logueado"] = input_usuario
                st.session_state["rol_logueado"] = rol_encontrado
                st.success(f"¡Bienvenido/a {input_usuario}!")
                st.balloons()
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
else:
    # =============================================================================
    # MENÚ LATERAL SEGÚN PERMISOS POR ROL
    # =============================================================================
    st.sidebar.title("🧪 Perfumería Panel")
    st.sidebar.write(f"**Usuario:** {st.session_state['usuario_logueado']}")
    st.sidebar.write(f"**Rol:** {st.session_state['rol_logueado']}")
    st.sidebar.markdown("---")
    
    opciones_menu = []
    if st.session_state["rol_logueado"] == "Administradora":
        opciones_menu = ["🔬 Laboratorio y Fabricación", "📊 Auditoría de Movimientos", "📦 Inventario General", "💰 Finanzas de Fábrica", "👥 Gestión de Empleados", "🛒 Caja Registradora", "🚚 Entregas y Logística"]
    elif st.session_state["rol_logueado"] == "Vendedor":
        opciones_menu = ["📥 Traspasos Pendientes", "🛒 Caja Registradora", "👥 Gestión de Clientes", "📦 Ver Stock Tienda"]
    elif st.session_state["rol_logueado"] == "Repartidor":
        opciones_menu = ["🚚 Mis Hojas de Ruta / Entregas"]
        
    seleccion = st.sidebar.radio("Navegación", opciones_menu)
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario_logueado"] = None
        st.session_state["rol_logueado"] = None
        st.rerun()

    # =============================================================================
    # MÓDULOS DE ADMINISTRADORA
    # ================
