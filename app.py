import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Medcell Operaciones", layout="wide")

# 2. Estilos personalizados
st.markdown("""
    <style>
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    
    .medcell-header { 
        border-bottom: 3px solid #0070f3; 
        padding-bottom: 12px; 
        margin-bottom: 25px; 
    }
    .medcell-brand { 
        font-size: 34px; 
        font-weight: 900; 
        letter-spacing: 2px; 
        color: #ffffff; 
        text-transform: uppercase; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .medcell-brand span { color: #0070f3; }
    .medcell-subtitle { color: #aaaaaa; font-size: 13px; font-weight: 600; letter-spacing: 1px; margin-top: 2px; }
    .medcell-author { color: #777777; font-size: 11px; margin-top: 4px; font-style: italic; }

    /* Estilo de Tarjetas de Filtro por Semana */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
    div[data-testid="stRadio"] label {
        background-color: #141414 !important; border: 1px solid #2b2b2b !important;
        padding: 10px 22px !important; border-radius: 10px !important;
        cursor: pointer !important; transition: all 0.25s ease-in-out !important;
        color: #cccccc !important; font-weight: 600 !important; font-size: 14px !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: #0070f3 !important; background-color: #1e1e1e !important;
        color: #ffffff !important; transform: translateY(-2px);
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background-color: #0070f3 !important; border-color: #0070f3 !important;
        color: #ffffff !important; box-shadow: 0px 4px 14px rgba(0, 112, 243, 0.4);
    }

    /* Pestañas generales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background-color: #121212; padding: 8px 12px; border-radius: 10px; border: 1px solid #262626; margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; white-space: pre-wrap; background-color: #1a1a1a; border-radius: 8px; color: #888888; font-weight: 600; font-size: 14px; border: 1px solid #2b2b2b; padding: 0px 20px; transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #ffffff; background-color: #242424; border-color: #0070f3; }
    .stTabs [aria-selected="true"] { background-color: #0070f3 !important; color: #ffffff !important; border-color: #0070f3 !important; box-shadow: 0px 4px 12px rgba(0, 112, 243, 0.3); }
    
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 26px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #888888 !important; }
    div[data-testid="stDataFrame"] { background-color: #121212; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- Funciones auxiliares de formato ---
def fmt_sem(val):
    if pd.isna(val) or val == "" or val is None:
        return ""
    try:
        val_f = float(val)
        if val_f.is_integer():
            return str(int(val_f))
        return str(val_f)
    except (ValueError, TypeError):
        return str(val)

def fmt_code(val):
    """Preserva ceros a la izquierda y formatos de código de origen como 0007341.7"""
    if pd.isna(val) or val == "" or val is None or str(val).lower() == 'nan':
        return "S/N"
    val_str = str(val).strip()
    if val_str.endswith('.0'):
        val_str = val_str[:-2]
    return val_str

def formato_moneda(valor):
    try:
        val_int = int(round(valor))
        return f"${val_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"

def formato_unidades(valor):
    try:
        val_int = int(round(valor))
        return f"{val_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def aplicar_criticidad(column):
    is_total = column.index == (len(column) - 1)
    styles = []
    for i, val in enumerate(column):
        if is_total[i]: styles.append('font-weight: bold; background-color: #1a1a1a;')
        elif val >= 15.0: styles.append('background-color: #8b0000; color: #ffffff; font-weight: bold;')
        elif val >= 10.0: styles.append('background-color: #b91c1c; color: #ffffff; font-weight: bold;')
        elif val >= 5.0: styles.append('background-color: #c2410c; color: #ffffff;')
        elif val > 0: styles.append('background-color: #27272a; color: #d4d4d8;')
        else: styles.append('')
    return styles

# --- 3. CARGA DEL EXCEL ---
def buscar_excel():
    posibles_rutas = [
        "SQL Seba.xlsx", "SQL Seba.xls",
        r"C:\Users\sebastianperez\Desktop\QUERY REDSHIFT\SQL Seba.xlsx",
        r"C:\Users\sebastianperez\Desktop\QUERY REDSHIFT\SQL Seba.xls"
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta): return ruta
    return None

ruta_final = buscar_excel()

@st.cache_data(ttl=60)
def cargar_libro_excel(ruta):
    xls = pd.ExcelFile(ruta)
    hojas_dict = {}
    for hoja in xls.sheet_names:
        df_temp = pd.read_excel(xls, hoja, dtype=str)
        df_temp.columns = [str(c).strip() for c in df_temp.columns]
        df_temp = df_temp.loc[:, ~df_temp.columns.str.startswith('Unnamed')]
        df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
        hojas_dict[hoja] = df_temp
    return hojas_dict

if not ruta_final:
    st.error("⚠️ No se encontró el archivo 'SQL Seba.xlsx' en la ruta especificada.")
    st.stop()

try:
    hojas = cargar_libro_excel(ruta_final)
except Exception as e:
    st.error(f"Error al leer Excel: {e}")
    st.stop()

# --- 4. HEADER ---
st.markdown("""
    <div class="medcell-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <div class="medcell-brand">MEDCELL <span>OPERACIONES</span></div>
                <div class="medcell-subtitle">ANÁLISIS DE OPERACIÓN</div>
                <div class="medcell-author">Desarrollado por Sebastián Alexis Pérez López</div>
            </div>
            <div style="font-size: 28px; font-weight: 800; color: #ffffff; white-space: nowrap; padding-bottom: 2px;">
                💊 Cadena Operaciones
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

def crear_reloj_gauge(titulo, porcentaje, color_barra):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=porcentaje,
        number={'suffix': "%", 'font': {'size': 28, 'color': '#ffffff'}},
        title={'text': f"<b>{titulo}</b>", 'font': {'size': 16, 'color': '#cccccc'}},
        gauge={
            'axis': {'range': [0, 100], 'ticksuffix': '%'},
            'bar': {'color': color_barra, 'thickness': 0.4},
            'bgcolor': "#1a1a1a", 'borderwidth': 1, 'bordercolor': "#333333",
            'steps': [{'range': [0, 50], 'color': '#281a1a'}, {'range': [50, 80], 'color': '#28241a'}, {'range': [80, 100], 'color': '#1a281f'}],
            'threshold': {'line': {'color': "#ffffff", 'width': 3}, 'thickness': 0.8, 'value': porcentaje}
        }
    ))
    fig.update_layout(height=210, margin=dict(l=25, r=25, t=35, b=15), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"))
    return fig

# --- 5. PESTAÑAS ---
HOJAS_A_EXCLUIR = ["sku", "maestra", "precio", "nivel de servicio sb", "venta perdida sb", "nivel de servicio pu"]
nombres_hojas = [h for h in hojas.keys() if h.strip().lower() not in HOJAS_A_EXCLUIR]

tabs = st.tabs([f"📊 {h}" for h in nombres_hojas])

for i, nombre_hoja in enumerate(nombres_hojas):
    with tabs[i]:
        df = hojas[nombre_hoja].copy()
        nombre_clean = nombre_hoja.strip().upper()
        
        is_sb = (nombre_clean == "SB")
        is_pu = (nombre_clean == "PU")
        is_stock = (nombre_clean == "STOCK")
        is_si = (nombre_clean == "SI")

        # =================================================================
        # PESTAÑA VENTA SI (REDISEÑADA, VISUAL Y DINÁMICA CON PROYECCIÓN)
        # =================================================================
        if is_si:
            st.markdown("### 📈 Dashboard Operativo de Venta SI")

            # 1. Detección y conversión de columnas
            col_cliente = next((c for c in df.columns if 'cliente' in c.lower()), 'nombre_cliente')
            col_div = next((c for c in df.columns if 'division' in c.lower() or 'división' in c.lower()), 'Division')
            col_monto = next((c for c in df.columns if 'monto' in c.lower()), 'monto')
            col_unid = next((c for c in df.columns if 'unidad' in c.lower() or 'cantidad' in c.lower()), 'cantidad_unidades')
            col_pmp = next((c for c in df.columns if 'pmp' in c.lower()), 'pmp_mes_actual')
            col_inflamable = next((c for c in df.columns if 'inflamable' in c.lower()), 'es_inflamable')
            col_factura = next((c for c in df.columns if 'factura' in c.lower() or 'orden' in c.lower()), 'Factura')

            df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0) if col_monto in df.columns else 0
            df[col_unid] = pd.to_numeric(df[col_unid], errors='coerce').fillna(0) if col_unid in df.columns else 0
            df[col_pmp] = pd.to_numeric(df[col_pmp], errors='coerce').fillna(0) if col_pmp in df.columns else 0

            # 2. Panel de filtros interactivos
            st.markdown("#### 🎛️ Filtros de Control")
            f_col1, f_col2, f_col3 = st.columns(3)
            
            with f_col1:
                divs_unicas = ["Todas"] + sorted([str(x) for x in df[col_div].dropna().unique()]) if col_div in df.columns else ["Todas"]
                div_sel = st.selectbox("Filtrar por División:", divs_unicas, key=f"f_div_{i}")

            with f_col2:
                clientes_unicos = ["Todos"] + sorted([str(x) for x in df[col_cliente].dropna().unique()]) if col_cliente in df.columns else ["Todos"]
                cliente_sel = st.selectbox("Filtrar por Cliente:", clientes_unicos, key=f"f_cli_{i}")

            with f_col3:
                inflamable_opts = ["Todos"] + sorted([str(x) for x in df[col_inflamable].dropna().unique()]) if col_inflamable in df.columns else ["Todos"]
                inflamable_sel = st.selectbox("Producto Inflamable:", inflamable_opts, key=f"f_inf_{i}")

            # Aplicar filtros
            df_si_filt = df.copy()
            if div_sel != "Todas" and col_div in df_si_filt.columns:
                df_si_filt = df_si_filt[df_si_filt[col_div].astype(str) == div_sel]
            if cliente_sel != "Todos" and col_cliente in df_si_filt.columns:
                df_si_filt = df_si_filt[df_si_filt[col_cliente].astype(str) == cliente_sel]
            if inflamable_sel != "Todos" and col_inflamable in df_si_filt.columns:
                df_si_filt = df_si_filt[df_si_filt[col_inflamable].astype(str) == inflamable_sel]

            st.divider()

            # 3. Métricas Principales (KPIs)
            st.markdown("#### 📊 KPIs Generales")
            monto_total = df_si_filt[col_monto].sum()
            unidades_totales = df_si_filt[col_unid].sum()
            costo_pmp_total = (df_si_filt[col_unid] * df_si_filt[col_pmp]).sum()
            ticket_promedio = (monto_total / unidades_totales) if unidades_totales > 0 else 0
            num_facturas = df_si_filt[col_factura].nunique() if col_factura in df_si_filt.columns else len(df_si_filt)

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Monto Total Facturado", formato_moneda(monto_total))
            k2.metric("Unidades Vendidas", formato_unidades(unidades_totales))
            k3.metric("Ticket Promedio / Unid", formato_moneda(ticket_promedio))
            k4.metric("Costo PMP Total", formato_moneda(costo_pmp_total))
            k5.metric("N° Transacciones/Facturas", formato_unidades(num_facturas))

            st.divider()

            # =================================================================
            # SECCIÓN PROYECCIÓN DE SI (COLUMNAS T A Z)
            # =================================================================
            st.markdown("### 🎯 Proyección y Cumplimiento de Cierre SI")

            if df.shape[1] >= 26:
                df_tz = df.iloc[:, 19:26].copy()
                
                # --- Tabla 1: Proyección por Canal (Filas superiores) ---
                df_canal = df_tz.iloc[0:3, [0, 1, 3, 4, 5, 6]].copy()
                df_canal.columns = ["Canal", "Facturado x Canal", "Proyección x Canal", "Meta", "% Cumplimiento", "% Facturado Actual"]
                
                for col in ["Facturado x Canal", "Proyección x Canal", "Meta"]:
                    df_canal[col] = pd.to_numeric(df_canal[col].astype(str).str.replace(r'[\$,.]', '', regex=True), errors='coerce').fillna(0)
                
                # --- Tabla 2: Proyección Salida por OC (Filas inferiores) ---
                df_oc = df_tz.iloc[16:23, [0, 1, 2, 3, 4]].copy()
                df_oc.columns = ["Canal", "Monto OC", "FR", "Proyección Salida", "OC Extra"]
                
                for col in ["Monto OC", "Proyección Salida", "OC Extra"]:
                    df_oc[col] = pd.to_numeric(df_oc[col].astype(str).str.replace(r'[\$,.]', '', regex=True), errors='coerce').fillna(0)

                # --- Métricas de Cierre (Fondo de columna T) ---
                try:
                    cierre_val = float(str(df_tz.iloc[23, 1]).replace('$', '').replace('.', '').strip())
                    meta_val = float(str(df_tz.iloc[24, 1]).replace('$', '').replace('.', '').strip())
                    resultado_val = float(str(df_tz.iloc[25, 1]).replace('$', '').replace('.', '').replace('-', '').strip()) * -1
                    cumplimiento_val = str(df_tz.iloc[26, 1]).strip() if df_tz.shape[0] > 26 else "83.3%"
                except Exception:
                    cierre_val, meta_val, resultado_val, cumplimiento_val = 3787767869, 4549320124, -761552255, "83.3%"

                # KPIs de Proyección
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Cierre Proyectado", formato_moneda(cierre_val))
                c2.metric("Meta Total", formato_moneda(meta_val))
                c3.metric("Diferencia / Resultado", formato_moneda(resultado_val), delta=f"{resultado_val:,.0f}")
                c4.metric("% Cumplimiento Cierre", cumplimiento_val)

                p_col1, p_col2 = st.columns(2)

                with p_col1:
                    st.markdown("##### 🏢 Proyección por Canal (Agosto)")
                    st.dataframe(
                        df_canal,
                        column_config={
                            "Facturado x Canal": st.column_config.NumberColumn(format="$%,d"),
                            "Proyección x Canal": st.column_config.NumberColumn(format="$%,d"),
                            "Meta": st.column_config.NumberColumn(format="$%,d"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                with p_col2:
                    st.markdown("##### 📦 Proyección Salida por Orden de Compra")
                    st.dataframe(
                        df_oc,
                        column_config={
                            "Monto OC": st.column_config.NumberColumn(format="$%,d"),
                            "Proyección Salida": st.column_config.NumberColumn(format="$%,d"),
                            "OC Extra": st.column_config.NumberColumn(format="$%,d"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            else:
                st.warning("Las columnas T a Z no se encuentran disponibles en el archivo cargado para generar la proyección.")

            st.divider()

            # 4. Componentes Visuales y Tablas (División y Cliente)
            c_div_view, c_cli_view = st.columns([1, 1.2], gap="large")

            # --- SECCIÓN DIVISIÓN ---
            with c_div_view:
                st.markdown("#### 🏢 Venta por División")
                if col_div in df_si_filt.columns and not df_si_filt.empty:
                    grp_div = df_si_filt.groupby(col_div, as_index=False).agg({
                        col_monto: 'sum',
                        col_unid: 'sum'
                    })
                    grp_div['Participación'] = (grp_div[col_monto] / monto_total) if monto_total > 0 else 0
                    grp_div = grp_div.sort_values(by=col_monto, ascending=False)

                    # Gráfico Donut
                    fig_donut = px.pie(
                        grp_div, 
                        values=col_monto, 
                        names=col_div,
                        hole=0.5,
                        color_discrete_sequence=["#0070f3", "#109618", "#f97316", "#ff9900"]
                    )
                    fig_donut.update_traces(
                        textposition='inside', 
                        textinfo='percent+label',
                        marker=dict(line=dict(color='#0b0b0b', width=2))
                    )
                    fig_donut.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=220,
                        showlegend=False
                    )
                    st.plotly_chart(fig_donut, use_container_width=True, key=f"donut_div_{i}")

                    # Tabla con barra de progreso
                    grp_div_disp = pd.DataFrame({
                        "División": grp_div[col_div],
                        "Monto ($)": grp_div[col_monto],
                        "Unidades": grp_div[col_unid],
                        "Participación": grp_div['Participación']
                    })

                    st.dataframe(
                        grp_div_disp,
                        column_config={
                            "Monto ($)": st.column_config.NumberColumn("Monto ($)", format="$%,d"),
                            "Unidades": st.column_config.NumberColumn("Unidades", format="%,d"),
                            "Participación": st.column_config.ProgressColumn(
                                "Participación",
                                format="%.1f%%",
                                min_value=0,
                                max_value=1
                            ),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("No hay datos de división disponibles.")

            # --- SECCIÓN TOP CLIENTES ---
            with c_cli_view:
                st.markdown("#### 🏆 Top Clientes por Facturación")
                if col_cliente in df_si_filt.columns and not df_si_filt.empty:
                    grp_cli = df_si_filt.groupby(col_cliente, as_index=False).agg({
                        col_monto: 'sum',
                        col_unid: 'sum'
                    }).sort_values(by=col_monto, ascending=False).head(10)

                    # Gráfico de Barras Horizontales
                    grp_cli_sorted = grp_cli.sort_values(by=col_monto, ascending=True)
                    fig_bars = px.bar(
                        grp_cli_sorted,
                        x=col_monto,
                        y=col_cliente,
                        orientation='h',
                        text_auto='.2s',
                        color_discrete_sequence=["#00CC96"]
                    )
                    fig_bars.update_traces(
                        textfont_size=11, 
                        textposition="outside", 
                        cliponaxis=False
                    )
                    fig_bars.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=220,
                        xaxis_title="",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_bars, use_container_width=True, key=f"bars_cli_{i}")

                    # Tabla Detallada
                    grp_cli_disp = pd.DataFrame({
                        "Cliente": grp_cli[col_cliente],
                        "Monto Total ($)": grp_cli[col_monto],
                        "Unidades": grp_cli[col_unid]
                    })

                    st.dataframe(
                        grp_cli_disp,
                        column_config={
                            "Monto Total ($)": st.column_config.NumberColumn("Monto Total ($)", format="$%,d"),
                            "Unidades": st.column_config.NumberColumn("Unidades", format="%,d"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("No hay datos de clientes disponibles.")

            st.divider()

            # 5. Registro completo de transacciones
            st.subheader("📋 Registro Completo de Ventas SI")
            busqueda_si = st.text_input("🔍 Buscar en registros SI (Descripción, SKU, Factura, etc.):", key=f"search_si_{i}")
            
            df_si_det = df_si_filt.copy()
            if busqueda_si:
                mask_si = df_si_det.astype(str).apply(lambda x: x.str.contains(busqueda_si, case=False)).any(axis=1)
                df_si_det = df_si_det[mask_si]
            
            st.caption(f"Mostrando {len(df_si_det)} registros.")
            st.dataframe(df_si_det, hide_index=True, use_container_width=True)

        # =================================================================
        # DASHBOARD DE STOCK / CADUCIDAD
        # =================================================================
        elif is_stock:
            st.markdown("### 📦 Dashboard de Fecha de Caducidad")
            
            col_cod = next((c for c in df.columns if c.strip().lower() in ['codigo_articulo', 'id_producto', 'sku', 'codigo']), None)
            col_estado_sub = next((c for c in df.columns if c.strip().lower() in ['estado_subin', 'sub_inventario', 'estado sub inventario']), None)
            col_estado_lote = next((c for c in df.columns if c.strip().lower() in ['estado_lote', 'estado lote', 'estado_lote_prov']), None)
            col_lote = next((c for c in df.columns if c.strip().lower() == 'lote_proveedor'), None) or next((c for c in df.columns if c.strip().lower() in ['lote', 'lote_prov']), None)
            col_loc = next((c for c in df.columns if c.strip().lower() in ['localizador', 'ubicacion']), None)
            col_fecha = next((c for c in df.columns if c.strip().lower() in ['fecha_expiracion_lote', 'vencimiento', 'fecha expiracion', 'fecha_expiracion']), None)
            col_cant = next((c for c in df.columns if c.strip().lower() in ['cantidad', 'stock', 'unidades']), None)

            if col_cod and col_cod in df.columns:
                df[col_cod] = df[col_cod].apply(fmt_code)

            if col_cant:
                df[col_cant] = pd.to_numeric(df[col_cant], errors='coerce').fillna(0)

            hoy = pd.Timestamp.today()
            limite_6m = hoy + pd.DateOffset(months=6)
            limite_13m = hoy + pd.DateOffset(months=13)

            if col_fecha:
                df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
                
                def calcular_alerta(fecha):
                    if pd.isna(fecha): return "Sin Fecha"
                    if fecha < limite_6m: return "Menos de 6 meses"
                    elif fecha <= limite_13m: return "Pronto vence (6-13m)"
                    else: return "Vigente (> 13m)"
                
                df["Alerta_Caducidad"] = df[col_fecha].apply(calcular_alerta)
            else:
                df["Alerta_Caducidad"] = "Sin Fecha"
                df[col_fecha] = "N/A"

            col_dash1, col_dash2, col_dash3 = st.columns([1, 1.5, 1.5])

            with col_dash3:
                if col_cod:
                    lista_prods = sorted([str(x) for x in df[col_cod].dropna().unique()])
                    prod_sel = st.selectbox("Elija un producto (Código / SKU):", ["Seleccione..."] + lista_prods, key=f"sel_prod_{i}")
                else:
                    prod_sel = "Seleccione..."

            if prod_sel != "Seleccione...":
                df_dash = df[df[col_cod].astype(str) == prod_sel].copy()
            else:
                df_dash = df.copy()

            if col_cant:
                total_unidades = df_dash[col_cant].sum()
                total_menos_6m = df_dash[df_dash["Alerta_Caducidad"] == "Menos de 6 meses"][col_cant].sum()
                total_pronto = df_dash[df_dash["Alerta_Caducidad"] == "Pronto vence (6-13m)"][col_cant].sum()
                total_vigentes = df_dash[df_dash["Alerta_Caducidad"] == "Vigente (> 13m)"][col_cant].sum()
            else:
                total_unidades = len(df_dash)
                total_menos_6m = len(df_dash[df_dash["Alerta_Caducidad"] == "Menos de 6 meses"])
                total_pronto = len(df_dash[df_dash["Alerta_Caducidad"] == "Pronto vence (6-13m)"])
                total_vigentes = len(df_dash[df_dash["Alerta_Caducidad"] == "Vigente (> 13m)"])

            with col_dash1:
                st.markdown("""
                <style>
                .stock-card { border-radius: 5px; padding: 15px; margin-bottom: 10px; text-align: center; color: white; font-weight: bold; }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="stock-card" style="background-color: #333; color: white;">Unidades Registradas<br><span style="font-size:24px;">{formato_unidades(total_unidades)}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stock-card" style="background-color: #e74c3c;">Unidades < 6 meses<br><span style="font-size:24px;">{formato_unidades(total_menos_6m)}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stock-card" style="background-color: #f1c40f; color: black;">Pronto vence (6 a 13 meses)<br><span style="font-size:24px;">{formato_unidades(total_pronto)}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stock-card" style="background-color: #2ecc71;">Vigentes (> 13 meses)<br><span style="font-size:24px;">{formato_unidades(total_vigentes)}</span></div>', unsafe_allow_html=True)

            with col_dash2:
                st.markdown("#### Estado de caducidad")
                labels = ['< 6 meses', '6 a 13 meses', 'Vigente (> 13m)']
                values = [total_menos_6m, total_pronto, total_vigentes]
                colors = ['#e74c3c', '#f1c40f', '#2ecc71']
                
                if sum(values) > 0:
                    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker=dict(colors=colors))])
                    fig_pie.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"), showlegend=True, legend=dict(orientation="h", y=-0.1))
                    st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_stock_{i}")
                else:
                    st.info("Sin registros para mostrar.")

            with col_dash3:
                if prod_sel != "Seleccione...":
                    stock_actual = df_dash[col_cant].sum() if col_cant else 0
                    prox_vencer = df_dash[df_dash[col_fecha].notna()][col_fecha].min() if col_fecha else None
                    dias_vencer = (prox_vencer - hoy).days if pd.notna(prox_vencer) else "N/A"
                    
                    st.markdown(f'<div class="stock-card" style="background-color: #7f8c8d;">Stock actual<br><span style="font-size:24px;">{formato_unidades(stock_actual)}</span></div>', unsafe_allow_html=True)
                    
                    if isinstance(dias_vencer, int):
                        if prox_vencer < limite_6m:
                            texto_vence = f"Vence en {dias_vencer} días" if dias_vencer >= 0 else f"Venció hace {abs(dias_vencer)} días"
                            color_vence = "#e74c3c"
                            color_texto = "color: white;"
                        elif prox_v¡Hola! Veo que me compartiste el código completo de tu dashboard "Medcell Operaciones" construido con Streamlit[cite: 1]. El script está súper completo: ya maneja la carga y limpieza de datos desde tu archivo Excel, aplica estilos personalizados con CSS y genera visualizaciones interactivas utilizando Plotly[cite: 1].

Sin embargo, **parece que olvidaste mencionar qué es exactamente lo que deseas que agregue** a este código. 

Para poder integrarlo de forma limpia y sin romper lo que ya tienes estructurado en tus pestañas (como Venta SI, Stock, SB y PU)[cite: 1], ¿podrías contarme qué nueva función, gráfico, filtro o lógica matemática necesitas incorporar? Apenas me des ese detalle, te entregaré el código actualizado y te indicaré exactamente en qué sección debes pegarlo.
