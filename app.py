import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Fábrica de Perfumes", page_icon="🧪", layout="wide")

CIUDADES_ENTREGA = ["Neuquén", "Plottier", "Cipolletti", "Centenario", "General Roca", "Cutral Co"]
MEDIOS_PAGO = ["Efectivo 💵", "Tarjeta de Débito 💳", "Crédito (3 Cuotas) 💳", "Transferencia Bancaria 🏦", "MercadoPago 📱"]
TIPOS_VENTA = ["Presencial / Local", "Online (Requiere envío)", "Manual vendedor"]

if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario_logueado" not in st.session_state: st.session_state["usuario_logueado"] = None
if "rol_logueado" not in st.session_state: st.session_state["rol_logueado"] = None

if "correlativo_os" not in st.session_state: st.session_state["correlativo_os"] = 4000000000
if "correlativo_ot" not in st.session_state: st.session_state["correlativo_ot"] = 5000000000

if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = pd.DataFrame([
        {"usuario": "admin", "clave": "admin123", "rol": "Administradora"},
        {"usuario": "vane", "clave": "vane123", "rol": "Vendedor"},
        {"usuario": "repa_juan", "clave": "juan123", "rol": "Repartidor"}
    ])

if "db_clientes" not in st.session_state:
    st.session_state["db_clientes"] = pd.DataFrame([
        {"Nombre": "María López", "Correo": "maria@gmail.com", "Teléfono": "299123456", "Dirección": "Av. Argentina 500", "Ciudad": "Neuquén", "Notas": "Cliente inicial"}
    ])

if "db_productos" not in st.session_state:
    st.session_state["db_productos"] = pd.DataFrame([
        {"Nombre": "Perfume Nuit", "Tamaño": "100ml", "Stock_Lab": 40, "Stock_Tienda": 15, "Precio": 15000.0, "Costo": 6000.0, "Fecha_Creacion": "2026-06-01", "Dias_Maceracion": 5},
        {"Nombre": "Esencia Floral", "Tamaño": "50ml", "Stock_Lab": 25, "Stock_Tienda": 0, "Precio": 9500.0, "Costo": 3500.0, "Fecha_Creacion": "2026-06-12", "Dias_Maceracion": 15}
    ])

if "db_ventas" not in st.session_state: st.session_state["db_ventas"] = pd.DataFrame(columns=["ID_Venta", "Cliente", "Producto", "Cantidad", "Total", "Medio_Pago", "Tipo"])
if "db_entrega" not in st.session_state: st.session_state["db_entrega"] = pd.DataFrame(columns=["ID_Pedido", "Cliente", "Dirección", "Repartidor", "Estado"])
if "db_traspasos" not in st.session_state: st.session_state["db_traspasos"] = pd.DataFrame(columns=["ID_Traspaso", "Producto", "Cantidad", "Vendedora", "Estado"])
if "db_movimientos" not in st.session_state: st.session_state["db_movimientos"] = pd.DataFrame(columns=["ID_Movimiento", "Fecha_Hora", "Usuario", "Detalle"])
if "notificacion_emergente" not in st.session_state: st.session_state["notificacion_emergente"] = None
  def registrar_movimiento(detalle_movimiento):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = st.session_state["usuario_logueado"] if st.session_state["usuario_logueado"] else "Sistema"
    id_m = f"MOV-{random.randint(10000,99999)}"
    nuevo_mov = {"ID_Movimiento": id_m, "Fecha_Hora": ahora, "Usuario": usuario, "Detalle": detalle_movimiento}
    st.session_state["db_movimientos"] = pd.concat([st.session_state["db_movimientos"], pd.DataFrame([nuevo_mov])], ignore_index=True)
    st.session_state["notificacion_emergente"] = {"fecha_hora": ahora, "usuario": usuario, "detalle": detalle_movimiento}

@st.dialog("🔔 Movimiento Registrado")
def mostrar_modal_notificacion(datos):
    st.write(f"📅 **Fecha:** {datos['fecha_hora']}")
    st.write(f"👤 **Usuario:** {datos['usuario']}")
    st.info(f"📝 **Detalle:** {datos['detalle']}")
    if st.button("Entendido", use_container_width=True):
        st.session_state["notificacion_emergente"] = None
        st.rerun()

if st.session_state["notificacion_emergente"] is not None: 
    mostrar_modal_notificacion(st.session_state["notificacion_emergente"])

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns()
    with col2:
        st.title("🧪 Fábrica de Perfumes")
        st.subheader("Control de Planta e Inventarios")
        input_usuario = st.text_input("Usuario")
        input_clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar Sistema", use_container_width=True):
            df_u = st.session_state["db_usuarios"]
            coincidencias = df_u[(df_u["usuario"] == input_usuario) & (df_u["clave"] == input_clave)]
            if not coincidencias.empty:
                st.session_state["autenticado"] = True
                st.session_state["usuario_logueado"] = input_usuario
                st.session_state["rol_logueado"] = coincidencias.iloc[0]["rol"]
                st.success("¡Ingreso exitoso!")
                st.balloons()
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
else:
    st.sidebar.title("🧪 Perfumería Panel")
    st.sidebar.write(f"**Usuario:** {st.session_state['usuario_logueado']}")
    st.sidebar.write(f"**Rol:** {st.session_state['rol_logueado']}")
    st.sidebar.markdown("---")
    
    opciones_menu = []
    if st.session_state["rol_logueado"] == "Administradora": 
        opciones_menu = ["🔬 Laboratorio", "📊 Auditoría", "📦 Inventario", "💰 Finanzas", "👥 Empleados"]
    elif st.session_state["rol_logueado"] == "Vendedor": 
        opciones_menu = ["📥 Traspasos", "🛒 Caja Registradora", "👥 Clientes"]
    elif st.session_state["rol_logueado"] == "Repartidor": 
        opciones_menu = ["🚚 Entregas"]
        
    seleccion = st.sidebar.radio("Navegación", opciones_menu)
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario_logueado"] = None
        st.session_state["rol_logueado"] = None
        st.rerun()
      # =============================================================================
    # MÓDULOS DE ADMINISTRADORA
    # =============================================================================
    if seleccion == "🔬 Laboratorio":
        st.header("🔬 Laboratorio Central")
        tab1, tab2 = st.tabs(["Fabricar Stock (OS)", "Generar Traspaso (OT)"])
        
        with tab1:
            with st.form("fabricar_lote_nuevo"):
                n_p = st.text_input("Nombre Fragancia")
                t_p = st.selectbox("Tamaño", ["30ml", "50ml", "100ml", "200ml"])
                c_f = st.number_input("Cantidad Fabricada", min_value=1, step=1, value=10)
                p_p = st.number_input("Precio Público ($)", min_value=0.0, step=100.0, value=12000.0)
                cos_p = st.number_input("Costo Manufactura ($)", min_value=0.0, step=100.0, value=5000.0)
                f_c = st.date_input("Fecha Creación", value=datetime.now())
                d_m = st.number_input("Días Maceración", min_value=0, value=15, step=1)
                
                if st.form_submit_button("Generar Orden de Ingreso"):
                    if n_p:
                        folio_os = f"OS-{st.session_state['correlativo_os']}"
                        st.session_state["correlativo_os"] += 1
                        df_prod = st.session_state["db_productos"]
                        idx = df_prod[(df_prod["Nombre"] == n_p) & (df_prod["Tamaño"] == t_p)].index
                        if not idx.empty: 
                            st.session_state["db_productos"].at[idx, "Stock_Lab"] += c_f
                        else:
                            nuevo = {"Nombre": n_p, "Tamaño": t_p, "Stock_Lab": c_f, "Stock_Tienda": 0, "Precio": p_p, "Costo": cos_p, "Fecha_Creacion": str(f_c), "Dias_Maceracion": d_m}
                            st.session_state["db_productos"] = pd.concat([st.session_state["db_productos"], pd.DataFrame([nuevo])], ignore_index=True)
                        registrar_movimiento(f"Emitida {folio_os}. Añadidos {c_f} u. de {n_p} a Lab.")
                        st.rerun()

        with tab2:
            if st.session_state["db_productos"].empty:
                st.warning("No hay productos.")
            else:
                df_u = st.session_state["db_usuarios"]
                lista_v = df_u[df_u["rol"] == "Vendedor"]["usuario"].tolist()
                st.markdown("##### ⏳ Estado de Maceración")
                filas_c = []
                hoy = datetime.now().date()
                for _, r in st.session_state["db_productos"].iterrows():
                    f_crea = datetime.strptime(str(r["Fecha_Creacion"]), "%Y-%m-%d").date()
                    f_listo = f_crea + timedelta(days=int(r["Dias_Maceracion"]))
                    dias_r = (f_listo - hoy).days
                    est = "✨ Listo para Tienda" if dias_r <= 0 else f"⏳ Macerando ({dias_r} d)"
                    filas_c.append({"Perfume": f"{r['Nombre']} ({r['Tamaño']})", "Stock Lab": r["Stock_Lab"], "Estado": est})
                st.dataframe(pd.DataFrame(filas_c), use_container_width=True)
                
                with st.form("orden_traspaso_form"):
                    list_op = [f"{r['Nombre']} ({r['Tamaño']})" for _, r in st.session_state["db_productos"].iterrows()]
                    perf_sel = st.selectbox("Perfume a Traspasar", list_op)
                    cant_t = st.number_input("Cantidad a enviar", min_value=1, step=1, value=5)
                    vend_d = st.selectbox("Vendedora Destino", lista_v if lista_v else ["Sin Vendedoras"])
                    
                    if st.form_submit_button("Enviar Traspaso"):
                        partes = perf_sel.split(" (")
                        p_nom = partes[0]
                        p_tam = partes[1].replace(")", "")
                        df_prod = st.session_state["db_productos"]
                        idx_p = df_prod[(df_prod["Nombre"] == p_nom) & (df_prod["Tamaño"] == p_tam)].index
                        if not idx_p.empty and df_prod.at[idx_p, "Stock_Lab"] >= cant_t:
                            st.session_state["db_productos"].at[idx_p, "Stock_Lab"] -= cant_t
                            folio_ot = f"OT-{st.session_state['correlativo_ot']}"
                            st.session_state["correlativo_ot"] += 1
                            nuevo_t = {"ID_Traspaso": folio_ot, "Producto": p_nom, "Cantidad": cant_t, "Vendedora": vend_d, "Estado": "Pendiente de Confirmación"}
                            st.session_state["db_traspasos"] = pd.concat([st.session_state["db_traspasos"], pd.DataFrame([nuevo_t])], ignore_index=True)
                            registrar_movimiento(f"Emitida {folio_ot}. Enviadas {cant_t} u. de {p_nom} a {vend_d}.")
                            st.rerun()
                        else:
                            st.error("Stock insuficiente en Laboratorio.")

    elif seleccion == "📊 Auditoría":
        st.header("📊 Historial de Movimientos")
        st.dataframe(st.session_state["db_movimientos"].sort_index(ascending=False), use_container_width=True)

    elif seleccion == "📦 Inventario":
        st.header("📦 Inventario General")
        st.dataframe(st.session_state["db_productos"], use_container_width=True)
        st.subheader("Traspasos Emitidos")
        st.dataframe(st.session_state["db_traspasos"], use_container_width=True)

    elif seleccion == "💰 Finanzas":
        st.header("💰 Finanzas de Fábrica")
        tot = st.session_state["db_ventas"]["Total"].sum() if not st.session_state["db_ventas"].empty else 0.0
        st.metric(label="Ingresos por Ventas", value=f"${tot:,.2f}")
        st.dataframe(st.session_state["db_ventas"], use_container_width=True)

    elif seleccion == "👥 Empleados":
        st.header("👥 Personal de Fábrica")
        with st.form("nuevo_emp"):
            u_e = st.text_input("Usuario")
            c_e = st.text_input("Clave", type="password")
            r_e = st.selectbox("Rol", ["Vendedor", "Repartidor"])
            if st.form_submit_button("Dar de Alta Empleado"):
                if u_e and c_e:
                    nuevo_u = {"usuario": u_e, "clave": c_e, "rol": r_e}
                    st.session_state["db_usuarios"] = pd.concat([st.session_state["db_usuarios"], pd.DataFrame([nuevo_u])], ignore_index=True)
                    registrar_movimiento(f"Alta de empleado: '{u_e}' ({r_e}).")
                    st.rerun()
        st.dataframe(st.session_state["db_usuarios"], use_container_width=True)
         # =============================================================================
    # MÓDULOS DE VENDEDOR
    # =============================================================================
    elif seleccion == "📥 Traspasos":
        st.header("📥 Órdenes de Traspaso (OT)")
        df_t = st.session_state["db_traspasos"]
        m_t = df_t[(df_t["Vendedora"] == st.session_state["usuario_logueado"]) & (df_t["Estado"] == "Pendiente de Confirmación")]
        if m_t.empty:
            st.info("No tenés traspasos pendientes de recibir.")
        else:
            for idx, fila in m_t.iterrows():
                with st.expander(f"📦 {fila['ID_Traspaso']} -> {fila['Producto']} (Cant: {fila['Cantidad']})", expanded=True):
                    pass_c = st.text_input("Contraseña para Firmar Recepción", type="password", key=f"p_{fila['ID_Traspaso']}")
                    if st.button("Confirmar Recepción ✅", key=f"b_{fila['ID_Traspaso']}"):
                        df_user = st.session_state["db_usuarios"]
                        # Se usa values[0] para extraer la contraseña exacta de forma segura sin romper la estructura de Pandas
                        c_real = df_user[df_user["usuario"] == st.session_state["usuario_logueado"]]["clave"].values[0]
                        if pass_c == c_real:
                            df_p = st.session_state["db_productos"]
                            idx_p = df_p[df_p["Nombre"] == fila["Producto"]].index
                            if not idx_p.empty:
                                st.session_state["db_productos"].at[idx_p, "Stock_Tienda"] += fila["Cantidad"]
                                st.session_state["db_traspasos"].at[idx, "Estado"] = "Recibido y Confirmado"
                                registrar_movimiento(f"Vendedora '{st.session_state['usuario_logueado']}' recibió {fila['Cantidad']} u. de {fila['Producto']} ({fila['ID_Traspaso']}).")
                                st.rerun()
                        else:
                            st.error("Contraseña incorrecta.")

    elif seleccion == "🛒 Caja Registradora":
        st.header("🛒 Caja Registradora")
        df_u = st.session_state["db_usuarios"]
        lista_rep = df_u[df_u["rol"] == "Repartidor"]["usuario"].tolist()
        with st.form("registro_venta"):
            c_nom = st.text_input("Cliente", value="Juan Pérez")
            c_dir = st.text_input("Dirección (Online)", value="Calle Falsa 123")
            c_ciu = st.selectbox("Ciudad", CIUDADES_ENTREGA)
            perf_s = st.selectbox("Perfume", st.session_state["db_productos"]["Nombre"].tolist() if not st.session_state["db_productos"].empty else [])
            cant_v = st.number_input("Cantidad", min_value=1, step=1, value=1)
            m_pago = st.selectbox("Método de Pago", MEDIOS_PAGO)
            t_venta = st.selectbox("Modalidad", TIPOS_VENTA)
            rep_asig = st.selectbox("Asignar Repartidor (Online)", lista_rep if lista_rep else ["Sin Repartidores"])
            if st.form_submit_button("Procesar Venta"):
                df_p = st.session_state["db_productos"]
                idx_prod = df_p[df_p["Nombre"] == perf_s].index
                if not idx_prod.empty and df_p.at[idx_prod, "Stock_Tienda"] >= cant_v:
                    st.session_state["db_productos"].at[idx_prod, "Stock_Tienda"] -= cant_v
                    precio_u = df_p.at[idx_prod, "Precio"].values[0]
                    tot_v = float(precio_u) * cant_v
                    id_v = f"V-{random.randint(1000,9999)}"
                    nuevo_v = {"ID_Venta": id_v, "Cliente": c_nom, "Producto": perf_s, "Cantidad": cant_v, "Total": tot_v, "Medio_Pago": m_pago, "Tipo": t_venta}
                    st.session_state["db_ventas"] = pd.concat([st.session_state["db_ventas"], pd.DataFrame([nuevo_v])], ignore_index=True)
                    nuevo_c = {"Nombre": c_nom, "Correo": "", "Teléfono": "", "Dirección": c_dir, "Ciudad": c_ciu, "Notas": ""}
                    st.session_state["db_clientes"] = pd.concat([st.session_state["db_clientes"], pd.DataFrame([nuevo_c])], ignore_index=True)
                    env_msg = ""
                    if t_venta == "Online (Requiere envío)":
                        id_p = f"PED-{random.randint(1000,9999)}"
                        nuevo_e = {"ID_Pedido": id_p, "Cliente": c_nom, "Dirección": f"{c_dir}, {c_ciu}", "Repartidor": rep_asig, "Estado": "En Camino"}
                        st.session_state["db_entrega"] = pd.concat([st.session_state["db_entrega"], pd.DataFrame([nuevo_e])], ignore_index=True)
                        env_msg = f" Pedido generado ({id_p}) con repartidor '{rep_asig}'."
                    registrar_movimiento(f"Venta {id_v}. {cant_v} u. de {perf_s}. Total: ${tot_v:,.2f}.{env_msg}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("No hay suficiente stock en mostrador.")

    elif seleccion == "👥 Clientes":
        st.header("👥 Clientes Registrados")
        st.dataframe(st.session_state["db_clientes"], use_container_width=True)

    # =============================================================================
    # MÓDULOS DE REPARTIDOR
    # =============================================================================
    elif seleccion == "🚚 Entregas":
        st.header("🚚 Mis Entregas Asignadas")
        df_e = st.session_state["db_entrega"]
        m_ped = df_e[df_e["Repartidor"] == st.session_state["usuario_logueado"]]
        if m_ped.empty:
            st.info("No tenés despachos agendados.")
        else:
            for idx, fila in m_ped.iterrows():
                with st.expander(f"📦 Pedido: {fila['ID_Pedido']} ({fila['Estado']})", expanded=True):
                    st.write(f"**Cliente:** {fila['Cliente']} | **Dirección:** {fila['Dirección']}")
                    st.link_button("🗺️ Abrir GPS", f"https://google.com{fila['Dirección'].replace(' ', '+')}")
                    if fila["Estado"] != "Entregado":
                        if st.button("Marcar como Entregado ✅", key=f"rep_{fila['ID_Pedido']}"):
                            st.session_state["db_entrega"].at[idx, "Estado"] = "Entregado"
                            registrar_movimiento(f"Repartidor '{st.session_state['usuario_logueado']}' entregó pedido {fila['ID_Pedido']}.")
                            st.rerun()
                          
