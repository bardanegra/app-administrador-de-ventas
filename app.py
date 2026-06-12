import streamlit as st
import pandas as pd
import requests
import json
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# ENLACES DE TU PLANILLA DE GOOGLE SHEETS (LECTURA)
GSHEETS_URL = "https://google.com"

# TU ENLACE MÁGICO DE ESCRITURA REAL (El de Apps Script que creaste de forma exitosa)
SCRIPT_URL = "https://google.com"

# FUNCIONES PARA LEER DATOS DESDE EL EXCEL DE GOOGLE
def cargar_datos_clientes():
    try: return pd.read_csv(GSHEETS_URL + "Clientes")
    except: return pd.DataFrame(columns=["Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Notas"])

def cargar_datos_productos():
    try: return pd.read_csv(GSHEETS_URL + "Productos")
    except: return pd.DataFrame(columns=["Nombre", "Tamaño", "Stock", "Precio", "Costo"])

def cargar_datos_usuarios():
    try: 
        df = pd.read_csv(GSHEETS_URL + "Usuario")
        df.columns = df.columns.str.strip()
        return df
    except: 
        return pd.DataFrame([{"Usuario": "admin", "Clave": "admin123", "Rol": "Admin"}])

def cargar_datos_ventas():
    try: return pd.read_csv(GSHEETS_URL + "Ventas")
    except: return pd.DataFrame(columns=["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"])

# FUNCIÓN MÁGICA DE ESCRITURA CORREGIDA AL 100%
def guardar_en_google_sheets(pestaña, datos_lista):
    try:
        url_final = f"{SCRIPT_URL}?sheet={pestaña}"
        # Convertimos la lista de datos a un formato JSON plano e ideal para Google
        headers = {"Content-Type": "application/json"}
        respuesta = requests.post(url_final, data=json.dumps(datos_lista), headers=headers, timeout=15)
        
        # Si Google responde exitosamente, devolvemos verdadero
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
        u_limpio = str(usuario_ingresado).strip()
        c_limpia = str(clave_ingresada).strip()
        
        # Respaldo local por si las celdas de Sheets están tardando en cargar
        if u_limpio == "admin" and c_limpia == "admin123":
            st.session_state.usuario_logueado = "admin"
            st.session_state.rol_logueado = "Admin"
            st.rerun()
            
        elif not df_usuarios.empty and "Usuario" in df_usuarios.columns and "Clave" in df_usuarios.columns:
            df_usuarios['Usuario'] = df_usuarios['Usuario'].astype(str).str.strip()
            df_usuarios['Clave'] = df_usuarios['Clave'].astype(str).str.strip()
            
            user_row = df_usuarios[df_usuarios['Usuario'] == u_limpio]
            
            if not user_row.empty and str(user_row.iloc[0]['Clave']) == c_limpia:
                st.session_state.usuario_logueado = u_limpio
                st.session_state.rol_logueado = user_row.iloc[0]['Rol']
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
        else: st.error("Usuario o contraseña incorrectos")
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None; st.session_state.rol_logueado = None; st.rerun()

    # Recargar datos en vivo de Google Sheets
    df_clientes = cargar_datos_clientes()
    df_productos = cargar_datos_productos()
    df_ventas = cargar_datos_ventas()

    # MENÚ
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
            if not df_clientes.empty and "Dirección" in df_clientes.columns and "Ciudad" in df_clientes.columns:
                for index, row in df_clientes.iterrows():
                    direccion_completa = f"{row['Dirección']}, {row['Ciudad']}, Argentina"
                    link_maps = f"https://google.com{urllib.parse.quote(direccion_completa)}"
                    with st.expander(f"📍 {row['Nombre']} - {row['Ciudad']}"):
                        st.link_button("🗺️ Abrir GPS Google Maps", link_maps, type="primary")

        with tab2:
            st.subheader("Cargar nuevo cliente")
            c_nombre = st.text_input("Nombre Completo")
            c_correo = st.text_input("Correo electrónico")
            c_telefono = st.text_input("Teléfono")
            c_direccion = st.text_input("Dirección (Calle y Nro)")
            c_ciudad = st.selectbox("Ciudad", ciudades_argentina)
            c_notas = st.text_area("Notas / Indicaciones")
            
            if st.button("Guardar Cliente de verdad", type="primary"):
                if c_nombre and c_direccion:
                    # Fila ordenada según tus columnas: Nombre, Correo, Teléfono, Dirección, Ciudad, Notas
                    nueva_fila = [c_nombre, c_correo, c_telefono, c_direccion, c_ciudad, c_notas]
                    with st.spinner("Guardando cliente en Google Sheets..."):
                        if guardar_en_google_sheets("Clientes", nueva_fila):
                            st.success(f"🎉 ¡ÉXITO! El cliente '{c_nombre}' se guardó correctamente.")
                            st.balloons()
                        else: st.error("🛑 Error de comunicación. Verifica los permisos de tu Excel.")

    # ==================== VENTANA: PRODUCTOS ====================
    elif opcion_menu == "📦 Productos y Stock":
        st.title("📦 Inventario de Perfumes")
        st.dataframe(df_productos, use_container_width=True)

    # ==================== VENTANA: CAJA REGISTRADORA ====================
    elif opcion_menu == "💰 Caja Registradora / Ventas":
        st.title("💰 Caja Registradora")
        tab1, tab2 = st.tabs(["🛒 Nueva Venta", "📜 Historial de Ventas"])
        
        with tab1:
            lista_clientes = [r['Nombre'] for i, r in df_clientes.iterrows()] if not df_clientes.empty else ["Cliente General"]
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
                with st.spinner("Registrando venta..."):
                    if guardar_en_google_sheets("Ventas", nueva_venta):
                        st.success("💰 ¡VENTA CONFIRMADA EN GOOGLE SHEETS!")
                        st.balloons()
                    else: st.error("🛑 Error al registrar la venta.")

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
                    with st.spinner("Guardando en Google Sheets..."):
                        if guardar_en_google_sheets("Usuario", nueva_fila):
