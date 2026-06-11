import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Perfumes", page_icon="🧪", layout="centered")

# SISTEMA DE SEGURIDAD (Simulación de Base de Datos temporal)
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "admin": {"clave": "admin123", "rol": "Admin"},
        "vendedor": {"clave": "vende123", "rol": "Vendedor"},
        "repartidor": {"clave": "reparte123", "rol": "Repartidor"}
    }

if "stock" not in st.session_state:
    st.session_state.stock = [
        {"Perfume": "Rosa Dulce", "Tamaño": "50ml", "Stock": 15, "Precio": 25.0},
        {"Perfume": "Cítrico Sol", "Tamaño": "100ml", "Stock": 8, "Precio": 40.0},
        {"Perfume": "Madera Real", "Tamaño": "100ml", "Stock": 20, "Precio": 45.0}
    ]

if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None
if "rol_logueado" not in st.session_state:
    st.session_state.rol_logueado = None

# --- PANTALLA DE INGRESO (LOGIN) ---
if st.session_state.usuario_logueado is None:
    st.title("🧪 Control de Perfumería")
    st.subheader("Iniciar Sesión")
    
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar", type="primary"):
        if usuario in st.session_state.usuarios and st.session_state.usuarios[usuario]["clave"] == clave:
            st.session_state.usuario_logueado = usuario
            st.session_state.rol_logueado = st.session_state.usuarios[usuario]["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# --- SISTEMA ADENTRO (LOGUEADO) ---
else:
    rol = st.session_state.rol_logueado
    st.sidebar.title(f"👤 {st.session_state.usuario_logueado.upper()}")
    st.sidebar.write(f"Rol: **{rol}**")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None
        st.session_state.rol_logueado = None
        st.rerun()

    st.title("✨ Sistema de Gestión a tu Manera")

    # ==================== VISTA ADMIN ====================
    if rol == "Admin":
        st.header("📊 Panel de Control (Administradora)")
        
        # Mostrar el stock actual en una tabla limpia
        st.subheader("📦 Stock General de Perfumes")
        df_stock = pd.DataFrame(st.session_state.stock)
        st.dataframe(df_stock, use_container_width=True)
        
        # Resumen financiero rápido
        total_dinero = sum(p["Stock"] * p["Precio"] for p in st.session_state.stock)
        st.metric(label="Valor total del stock en estantería", value=f"${total_dinero:,.2f}")
        
        # Historial general de entregas
        st.subheader("🚚 Monitoreo Global de Envíos")
        if not st.session_state.pedidos:
            st.info("No hay pedidos registrados en el sistema todavía.")
        else:
            df_pedidos = pd.DataFrame(st.session_state.pedidos)
            st.dataframe(df_pedidos, use_container_width=True)

    # ==================== VISTA VENDEDOR ====================
    elif rol == "Vendedor":
        st.header("🛒 Módulo de Ventas y Envíos")
        
        tab1, tab2 = st.tabs(["Registrar Nueva Venta", "Coordinar Entregas"])
        
        with tab1:
            perfumes_disponibles = [p["Perfume"] for p in st.session_state.stock if p["Stock"] > 0]
            perfume_sel = st.selectbox("Seleccione el perfume vendido", perfumes_disponibles)
            tipo_venta = st.radio("Tipo de venta", ["Manual / Presencial", "Online"])
            direccion = ""
            
            if tipo_venta == "Online":
                direccion = st.text_input("Dirección de envío para el repartidor")
                
            cantidad = st.number_input("Cantidad", min_value=1, value=1)
            
            if st.button("Confirmar y Guardar Venta", type="primary"):
                # Buscar perfume en el stock y descontar
                for p in st.session_state.stock:
                    if p["Perfume"] == perfume_sel:
                        if p["Stock"] >= cantidad:
                            p["Stock"] -= cantidad
                            
                            # Si es online, se genera la entrega pendiente
                            if tipo_venta == "Online":
                                st.session_state.pedidos.append({
                                    "ID": len(st.session_state.pedidos) + 1,
                                    "Perfume": perfume_sel,
                                    "Cantidad": cantidad,
                                    "Dirección": direccion,
                                    "Repartidor": "No asignado",
                                    "Estado": "⏳ Pendiente"
                                })
                                st.success("¡Venta guardada! Envío generado en la pestaña 'Coordinar Entregas'.")
                            else:
                                st.success("¡Venta presencial registrada con éxito! Stock actualizado.")
                            st.rerun()
                        else:
                            st.error("No hay suficiente stock disponible.")

        with tab2:
            st.subheader("📦 Envíos generados sin asignar")
            pedidos_sin_asignar = [p for p in st.session_state.pedidos if p["Repartidor"] == "No asignado"]
            
            if not pedidos_sin_asignar:
                st.info("No tienes envíos pendientes de asignar.")
            else:
                for idx, ped in enumerate(pedidos_sin_asignar):
                    st.write(f"**Pedido #{ped['ID']}**: {ped['Cantidad']}x {ped['Perfume']} para la dirección: *{ped['Dirección']}*")
                    # Botón para que la vendedora le asigne el trabajo al repartidor
                    if st.button(f"Asignar al Repartidor 🚗 (Pedido #{ped['ID']})", key=f"asig_{idx}"):
                        for real_ped in st.session_state.pedidos:
                            if real_ped["ID"] == ped["ID"]:
                                real_ped["Repartidor"] = "repartidor"
                                real_ped["Estado"] = "🚗 En Ruta"
                        st.success("¡Pedido asignado al repartidor con éxito!")
                        st.rerun()

    # ==================== VISTA REPARTIDOR ====================
    elif rol == "Repartidor":
        st.header("🚗 Hoja de Ruta (Repartidor)")
        st.subheader("Mis Entregas Asignadas")
        
        mis_entregas = [p for p in st.session_state.pedidos if p["Repartidor"] == "repartidor" and p["Estado"] == "🚗 En Ruta"]
        
        if not mis_entregas:
            st.success("🎉 ¡Felicitaciones! No tienes entregas pendientes por el momento.")
        else:
            for idx, ped in enumerate(mis_entregas):
                st.info(f"📍 **Entregar en**: {ped['Dirección']} \n\n Pack: {ped['Cantidad']}x {ped['Perfume']}")
                if st.button(f"✅ Marcar como Entregado", key=f"ent_{idx}"):
                    for real_ped in st.session_state.pedidos:
                        if real_ped["ID"] == ped["ID"]:
                            real_ped["Estado"] = "✅ Entregado"
                    st.success("¡Entrega completada!")
                    st.rerun()
