import streamlit as st
import pandas as pd
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# ENLACE DE TU PLANILLA DE GOOGLE SHEETS
# Reemplazamos el final para que Python pueda leerlo directamente como un archivo CSV
GSHEETS_URL = "https://google.com"

# FUNCIÓN PARA LEER LOS DATOS DESDE GOOGLE SHEETS
def cargar_datos_clientes():
    try:
        # Intentamos leer la pestaña 'Clientes' de tu Google Sheets
        url = GSHEETS_URL + "Clientes"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        # Si da error o está vacía, creamos una estructura de respaldo
        return pd.DataFrame(columns=["Apellido", "Nombre", "Correo", "Teléfono", "Direccion", "Ciudad", "Notas"])

# SISTEMA DE SEGURIDAD TEMPORAL PARA COMPROBAR USUARIOS
if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None
if "rol_logueado" not in st.session_state:
    st.session_state.rol_logueado = None

# --- PANTALLA DE INGRESO (LOGIN) ---
if st.session_state.usuario_logueado is None:
    st.title("🧪 Control de Perfumería")
    st.subheader("Iniciar Sesión")
    
    usuario = st.text_input("Usuario (Prueba: admin)")
    clave = st.text_input("Contraseña (Prueba: admin123)", type="password")
    
    if st.button("Ingresar", type="primary"):
        # Credenciales provisorias para que puedas entrar a probar
        if usuario == "admin" and clave == "admin123":
            st.session_state.usuario_logueado = "admin"
            st.session_state.rol_logueado = "Admin"
            st.rerun()
        elif usuario == "vendedor" and clave == "vende123":
            st.session_state.usuario_logueado = "vendedor"
            st.session_state.rol_logueado = "Vendedor"
            st.rerun()
        elif usuario == "repartidor" and clave == "reparte123":
            st.session_state.usuario_logueado = "repartidor"
            st.session_state.rol_logueado = "Repartidor"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# --- SISTEMA INTERNO ---
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None
        st.session_state.rol_logueado = None
        st.rerun()

    st.title("✨ Módulo de Clientes y Envíos con GPS")

    # Cargar los datos desde tu Google Sheets en tiempo real
    df_clientes = cargar_datos_clientes()

    # LISTA DE CIUDADES DE TU ZONA (Puedes agregar más a esta lista en el código)
    ciudades_argentina = ["Neuquén", "Plottier", "Cipolletti", "Centenario", "General Roca", "Cutral Co"]

    # ==================== VISTA ADMIN O VENDEDOR (GESTIONAR CLIENTES) ====================
    if rol in ["Admin", "Vendedor"]:
        tab1, tab2 = st.tabs(["📋 Lista de Clientes en Google Sheets", "➕ Registrar Nuevo Cliente"])
        
        with tab1:
            st.subheader("Clientes Registrados Actuales")
            if df_clientes.empty:
                st.info("No hay clientes guardados en tu planilla de Google Sheets.")
            else:
                # Mostramos la tabla tal cual está en tu Google Drive
                st.dataframe(df_clientes, use_container_width=True)

        with tab2:
            st.subheader("Cargar un cliente al negocio")
            
            # Formulario con los campos exactos de tu planilla
            apellido = st.text_input("Apellido")
            nombre = st.text_input("Nombre")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")
            direccion = st.text_input("Dirección (Calle y Número)")
            
            # Menú desplegable para que la vendedora elija sin equivocarse
            ciudad_sel = st.selectbox("Ciudad / Localidad", ciudades_argentina)
            notas = st.text_area("Notas / Indicaciones extras")
            
            # Enlace para que la vendedora simule cómo lo guardaría en el Sheets
            if st.button("Simular Guardado de Cliente", type="primary"):
                st.success(f"¡Cliente {nombre} {apellido} procesado correctamente!")
                st.info("Para que escriba directo en tu Google Sheets, en el próximo paso agregaremos las claves de escritura.")

    # ==================== VISTA REPARTIDOR (SISTEMA DE GPS AUTOMÁTICO) ====================
    elif rol == "Repartidor":
        st.header("🚗 Hoja de Ruta del Repartidor")
        st.subheader("Envíos a entregar")
        
        if df_clientes.empty:
            st.success("No hay rutas asignadas para hoy.")
        else:
            st.write("Selecciona un cliente para abrir su ubicación en el GPS de tu celular:")
            
            # Recorremos la lista de clientes de tu Google Sheets para generar los mapas
            for index, row in df_clientes.iterrows():
                # Combinamos dirección y ciudad para armar la búsqueda del mapa
                direccion_completa = f"{row['Direccion']}, {row['Ciudad']}, Argentina"
                # Codificamos el texto para que internet lo entienda como un link válido
                link_maps = f"https://google.com{urllib.parse.quote(direccion_completa)}"
                
                # Caja de información para el repartidor
                with st.expander(f"📍 {row['Nombre']} {row['Apellido']} - {row['Ciudad']}"):
                    st.write(f"📞 **Teléfono:** {row['Teléfono']}")
                    st.write(f"🏠 **Dirección:** {row['Direccion']}")
                    st.write(f"📝 **Notas:** {row['Notas']}")
                    
                    # El botón mágico con flecha que abre Google Maps directamente
                    st.link_button("🗺️ Abrir en Google Maps / GPS", link_maps, type="primary")

