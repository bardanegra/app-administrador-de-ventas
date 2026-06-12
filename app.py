import streamlit as st
import pandas as pd
import requests
import json
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# ENLACES DE TU PLANILLA DE GOOGLE SHEETS
GSHEETS_URL = "https://google.com"

# TU ENLACE MÁGICO DE ESCRITURA ACTUALIZADO
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwH67JIytMVOwpAF3IaNBOUX7M4RWsI1qx3bgAYKWJgdmdP83R5pX_DX_APLXv4qoUi/exec"

# FUNCIONES PARA LEER DATOS DESDE GOOGLE SHEETS
def cargar_datos_clientes():
    try: return pd.read_csv(GSHEETS_URL + "Clientes")
    except: return pd.DataFrame(columns=["Apellido", "Nombre", "Correo", "Teléfono", "Direccion", "Ciudad", "Notas"])

def cargar_datos_productos():
    try: return pd.read_csv(GSHEETS_URL + "Productos")
    except: return pd.DataFrame(columns=["Nombre", "Tamaño", "Stock", "Precio", "Costo"])

def cargar_datos_usuarios():
    try: 
        df = pd.read_csv(GSHEETS_URL + "Usuario")
        return df
    except: 
        return pd.DataFrame([{"Usuario": "admin", "Clave": "admin123", "Rol": "Admin"}])

def cargar_datos_ventas():
    try: return pd.read_csv(GSHEETS_URL + "Ventas")
    except: return pd.DataFrame(columns=["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"])

# FUNCIÓN PARA ESCRIBIR EN TU PLANILLA EN VIVO
def guardar_en_google_sheets(pestaña, datos_lista):
    try:
        url_final = f"{SCRIPT_URL}?sheet={pestaña}"
        respuesta = requests.post(url_final, data=json.dumps(datos_lista))
        if respuesta.status_code == 200:
            return True
        return False
    except:
        return False

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
        df_usuarios['Usuario'] = df_usuarios['Usuario'].astype(str)
        df_usuarios['Clave'] = df_usuarios['Clave'].astype(str)
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

    # Recargar datos desde el Excel de Google en vivo
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()
    df_ventas = cargar_datos_ventas()

    # MENÚ ADAPTADO AL ROL
    opciones = ["📋 Clientes", "📦 Productos y Stock", "💰 Caja Registradora / Ventas"]
    if rol == "Admin":
        opciones.append("👥 Gestión de Empleados")
    
    opcion_menu = st.sidebar.radio("Ir a la ventana:", opciones)
    ciudades_argentina = ["Neuquén", "Plottier", "Cipolletti", "Centenario", "General Roca", "Cutral Co"]

    # ==================== VENTANA: CLIENTES ====================
    if opcion_menu == "📋 Clientes":
        st.title("📍 Módulo de Clientes y GPS")
        tab1, tab2 = st.tabs(["Lista de Clientes", "➕ Registrar Nuevo Cliente"])
        
        with tab1:
            st.dataframe(df_clientes, use_container_width=True)
            st.subheader("🗺️ GPS para Repartidor")
            if not df_clientes.empty:
                for index, row in df_clientes.iterrows():
                    direccion_completa = f"{row['Direccion']}, {row['Ciudad']}, Argentina"
                    link_maps = f"https://google.com{urllib.parse.quote(direccion_completa)}"
                    with st.expander(f"📍 {row['Nombre']} {row['Apellido']} - {row['Ciudad']}"):
                        st.write(f"🏠 Dirección: {row['Direccion']}")
                        st.link_button("🗺️ Abrir GPS Google Maps", link_maps, type="primary")

        with tab2:
            st.subheader("Cargar nuevo cliente")
            c_apellido = st.text_input("Apellido")
            c_nombre = st.text_input("Nombre")
            c_correo = st.text_input("Correo electrónico")
            c_telefono = st.text_input("Teléfono")
            c_direccion = st.text_input("Dirección")
            c_ciudad = st.selectbox("Ciudad", ciudades_argentina)
            c_notas = st.text_area("Notas")
            
            if st.button("Guardar Cliente de verdad", type="primary"):
                if c_nombre and c_apellido and c_direccion:
                    nueva_fila = [c_nombre, c_apellido, c_correo, c_telefono, c_direccion, c_ciudad, c_notas]
                    if guardar_en_google_sheets("Clientes", nueva_fila):
                        st.success(f"¡Cliente {c_nombre} guardado exitosamente en Google Sheets!")
                        st.rerun()
                    else: st.error("Error de conexión con Google Sheets.")

    # ==================== VENTANA: PRODUCTOS ====================
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario de Perfumes")
        st.dataframe(df_productos, use_container_width=True)

    # ==================== VENTANA: CAJA REGISTRADORA ====================
    elif opcion_menu == "💰 Caja Registradora / Ventas":
        st.title("💰 Caja Registradora")
        tab1, tab2 = st.tabs(["🛒 Nueva Venta", "📜 Historial de Ventas"])
        
        with tab1:
            lista_clientes = [f"{r['Nombre']} {r['Apellido']}" for i, r in df_clientes.iterrows()] if not df_clientes.empty else ["Cliente General"]
            lista_perfumes = [r['Nombre'] for i, r in df_productos.iterrows()] if not df_productos.empty else ["No hay perfumes"]
            
            v_cliente = st.selectbox("Seleccione el Cliente", lista_clientes)
            v_producto = st.selectbox("Seleccione el Perfume", lista_perfumes)
            v_cantidad = st.number_input("Cantidad de unidades", min_value=1, value=1)
            
            precio_unitario = 0.0
            if not df_productos.empty and v_producto in df_productos['Nombre'].values:
                precio_unitario = float(df_productos[df_productos['Nombre'] == v_producto]['Precio'].values)
            
            total_operacion = v_cantidad * precio_unitario
            st.info(f"💵 Total a Cobrar: ${total_operacion:,.2f}")
            v_medio = st.selectbox("Método de Pago", ["Efectivo 💵", "Tarjeta de Débito 💳", "Crédito 💳", "Transferencia 🏦", "MercadoPago 📱"])
            v_tipo = st.radio("Modalidad", ["Presencial / Local", "Online (Requiere envío)"])
            
            if st.button("Confirmar Transacción Real", type="primary"):
                id_v = len(df_ventas) + 1
                nueva_venta = [id_v, v_cliente, v_producto, v_cantidad, total_operacion, v_medio, v_tipo]
                if guardar_en_google_sheets("Ventas", nueva_venta):
                    st.success("¡Venta registrada con éxito en tu Google Sheets!")
                    st.balloons()
                    st.rerun()
                else: st.error("No se pudo escribir en Google Sheets.")

        with tab2:
            st.dataframe(df_ventas, use_container_width=True)

    # ==================== VENTANA: GESTIÓN DE EMPLEADOS ====================
    elif opcion_menu == "👥 Gestión de Empleados" and rol == "Admin":
        st.title("👥 Control de Personal")
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
                    nueva_fila = [nuevo_user, nueva_pass, nuevo_rol]
                    if guardar_en_google_sheets("Usuario", nueva_fila):
                        st.success(f"¡Usuario '{nuevo_user}' guardado con éxito en tu planilla!")
                        st.rerun()
                    else: st.error("Error al escribir el empleado.")
