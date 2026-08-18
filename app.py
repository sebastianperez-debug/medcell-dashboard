import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y PALETA CORPORATIVA
# ==============================================================================
st.set_page_config(
    page_title="Medcell Operaciones | Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definición de Colores Corporativos
COLOR_AZUL_MARINO = "#0A2540"
COLOR_AZUL_ACCENT = "#0052CC"
COLOR_NARANJA_CONSUMO = "#FF7A00"
COLOR_CALIPSO_FARMA = "#00ADB5"
COLOR_VERDE_SUCCESS = "#10B981"
COLOR_AMARILLO_WARN = "#F59E0B"
COLOR_ROJO_DANGER = "#EF4444"
COLOR_BG_DARK = "#0B0F19"
COLOR_CARD_BG = "#131B2E"
COLOR_BORDER = "#1F2D47"

# ==============================================================================
# 2. ESTILOS CSS PERSONALIZADOS (DARK THEME MEDCELL)
# ==============================================================================
st.markdown(f"""
    <style>
    /* Fondo General Dark Dashboard */
    .stApp {{
        background-color: {COLOR_BG_DARK};
        color: #E2E8F0;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* Header Corporativo Medcell */
    .medcell-header {{
        background: linear-gradient(135deg, #0A2540 0%, #131B2E 100%);
        border-bottom: 3px solid {COLOR_AZUL_ACCENT};
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.4);
    }}
    .medcell-brand {{
        font-size: 32px;
        font-weight: 900;
        letter-spacing: 2px;
        color: #FFFFFF;
        text-transform: uppercase;
    }}
    .medcell-brand span {{
        color: {COLOR_CALIPSO_FARMA};
    }}
    .medcell-subtitle {{
        color: #94A3B8;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }}
    .medcell-author {{
        color: #64748B;
        font-size: 11px;
        margin-top: 4px;
        font-style: italic;
    }}

    /* Estilo de Botones / Tarjetas de Filtro por Semana (Pill Buttons) */
    div[data-testid="stRadio"] > label {{ display: none; }}
    div[data-testid="stRadio"] > div {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 6px;
    }}
    div[data-testid="stRadio"] label {{
        background-color: {COLOR_CARD_BG} !important;
        border: 1px solid {COLOR_BORDER} !important;
        padding: 8px 20px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.25s ease-in-out !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    div[data-testid="stRadio"] label:hover {{
        border-color: {COLOR_AZUL_ACCENT} !important;
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }}
    div[data-testid="stRadio"] label[data-checked="true"] {{
        background-color: {COLOR_AZUL_ACCENT} !important;
        border-color: {COLOR_AZUL_ACCENT} !important;
        color: #FFFFFF !important;
        box-shadow: 0px 4px 12px rgba(0, 82, 204, 0.4);
    }}

    /* Estilos de Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: #0F172A;
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid {COLOR_BORDER};
        margin-bottom: 24px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 44px;
        background-color: {COLOR_CARD_BG};
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid {COLOR_BORDER};
        padding: 0px 22px;
        transition: all 0.3s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: #FFFFFF;
        background-color: #1E293B;
        border-color: {COLOR_AZUL_ACCENT};
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLOR_AZUL_ACCENT} 0%, #003399 100%) !important;
        color: #FFFFFF !important;
        border-color: {COLOR_AZUL_ACCENT} !important;
        box-shadow: 0px 4px 14px rgba(0, 82, 204, 0.35);
    }}

    /* Tarjetas de Métricas Personalizadas (KPIs) */
    .kpi-card {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        border-color: {COLOR_AZUL_ACCENT};
    }}
    .kpi-title {{
        color: #94A3B8;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .kpi-value {{
        color: #FFFFFF;
        font-size: 24px;
        font-weight: 800;
        margin-top: 6px;
    }}

    /* Dataframe y Tablas */
    div[data-testid="stDataFrame"] {{
        background-color: {COLOR_CARD_BG};
        border-radius: 10px;
        border: 1px solid {COLOR_BORDER};
    }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNCIONES AUXILIARES Y DEDUPLICACIÓN DE COLUMNAS
# ==============================================================================
def asegurar_columnas_unicas(df_in):
    """Garantiza que el DataFrame no tenga columnas duplicadas para evitar errores en Streamlit."""
    if df_in is None or df_in.empty:
        return df_in
    df_out = df_in.copy()
    # 1. Elimina duplicadas idénticas
    df_out = df_out.loc[:, ~df_out.columns.duplicated()]
    # 2. Asigna sufijos si existen nombres idénticos tras renombrar
    cols_series = pd.Series(df_out.columns)
    if cols_series.duplicated().any():
        for dup in cols_series[cols_series.duplicated()].unique():
            cols_series[cols_series == dup] = [f"{dup}" if idx == 0 else f"{dup}_{idx+1}" for idx in range((cols_series == dup).sum())]
        df_out.columns = cols_series
    return df_out

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
        if is_total[i]: 
            styles.append('font-weight: bold; background-color: #1E293B; color: #FFFFFF;')
        elif val >= 15.0: 
            styles.append(f'background-color: {COLOR_ROJO_DANGER}; color: #FFFFFF; font-weight: bold;')
        elif val >= 10.0: 
            styles.append('background-color: #B91C1C; color: #FFFFFF; font-weight: bold;')
        elif val >= 5.0: 
            styles.append('background-color: #C2410C; color: #FFFFFF;')
        elif val > 0: 
            styles.append('background-color: #1E293B; color: #CBD5E1;')
        else: 
            styles.append('')
    return styles

# ==============================================================================
# 4. CARGA DEL ARCHIVO EXCEL
# ==============================================================================
def buscar_excel():
    posibles_rutas = [
        "SQL Seba.xlsx", "SQL Seba.xls",
        r"C:\Users\sebastianperez\Desktop\QUERY REDSHIFT\SQL Seba.xlsx",
        r"C:\Users\sebastianperez\Desktop\QUERY REDSHIFT\SQL Seba.xls"
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta): 
            return ruta
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

# ==============================================================================
# 5. HEADER CORPORATIVO
# ==============================================================================
st.markdown(f"""
    <div class="medcell-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <div class="medcell-brand">MEDCELL <span>OPERACIONES</span></div>
                <div class="medcell-subtitle">DASHBOARD DE CONTROL Y NIVEL DE SERVICIO</div>
                <div class="medcell-author">Desarrollado por Sebastián Alexis Pérez López</div>
            </div>
            <div style="font-size: 26px; font-weight: 800; color: #FFFFFF; white-space: nowrap;">
                💊 Cadena Operaciones
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

def crear_reloj_gauge(titulo, porcentaje, color_barra):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=porcentaje,
        number={'suffix': "%", 'font': {'size': 30, 'color': '#FFFFFF', 'family': 'Segoe UI'}},
        title={'text': f"<b>{titulo}</b>", 'font': {'size': 15, 'color': '#94A3B8'}},
        gauge={
            'axis': {'range': [0, 100], 'ticksuffix': '%', 'tickcolor': '#64748B'},
            'bar': {'color': color_barra, 'thickness': 0.45},
            'bgcolor': "#0F172A",
            'borderwidth': 1,
            'bordercolor': COLOR_BORDER,
            'steps': [
                {'range': [0, 60], 'color': '#2A1B1B'},
                {'range': [60, 85], 'color': '#2A241B'},
                {'range': [85, 100], 'color': '#1B2A20'}
            ],
            'threshold': {
                'line': {'color': "#FFFFFF", 'width': 3},
                'thickness': 0.8,
                'value': porcentaje
            }
        }
    ))
    fig.update_layout(
        height=210,
        margin=dict(l=25, r=25, t=35, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF")
    )
    return fig

# ==============================================================================
# 6. PESTAÑAS PRINCIPALES DEL DASHBOARD
# ==============================================================================
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

        # ----------------------------------------------------------------------
        # PESTAÑA VENTA SI
        # ----------------------------------------------------------------------
        if is_si:
            st.markdown("### 📈 Dashboard Operativo de Venta SI")

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

            # Filtros
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

            df_si_filt = df.copy()
            if div_sel != "Todas" and col_div in df_si_filt.columns:
                df_si_filt = df_si_filt[df_si_filt[col_div].astype(str) == div_sel]
            if cliente_sel != "Todos" and col_cliente in df_si_filt.columns:
                df_si_filt = df_si_filt[df_si_filt[col_cliente].astype(str) == cliente_sel]
            if inflamable_sel != "Todos" and col_inflamable in df_si_filt.columns:
                df_si_filt = df_si_filt[df_si_filt[col_inflamable].astype(str) == inflamable_sel]

            st.divider()

            # KPIs
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

            # Gráficos Venta SI
            c_div_view, c_cli_view = st.columns([1, 1.2], gap="large")

            with c_div_view:
                st.markdown("#### 🏢 Venta por División")
                if col_div in df_si_filt.columns and not df_si_filt.empty:
                    grp_div = df_si_filt.groupby(col_div, as_index=False).agg({
                        col_monto: 'sum',
                        col_unid: 'sum'
                    })
                    grp_div['Participación'] = (grp_div[col_monto] / monto_total) if monto_total > 0 else 0
                    grp_div = grp_div.sort_values(by=col_monto, ascending=False)

                    fig_donut = px.pie(
                        grp_div, 
                        values=col_monto, 
                        names=col_div,
                        hole=0.55,
                        color_discrete_sequence=[COLOR_AZUL_ACCENT, COLOR_NARANJA_CONSUMO, COLOR_CALIPSO_FARMA, COLOR_VERDE_SUCCESS]
                    )
                    fig_donut.update_traces(
                        textposition='inside', 
                        textinfo='percent+label',
                        marker=dict(line=dict(color=COLOR_BG_DARK, width=2))
                    )
                    fig_donut.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=230,
                        showlegend=False
                    )
                    st.plotly_chart(fig_donut, use_container_width=True, key=f"donut_div_{i}")

                    df_grp_disp = pd.DataFrame({
                        "División": grp_div[col_div],
                        "Monto ($)": grp_div[col_monto],
                        "Unidades": grp_div[col_unid],
                        "Participación": grp_div['Participación']
                    })
                    st.dataframe(
                        asegurar_columnas_unicas(df_grp_disp),
                        column_config={
                            "Monto ($)": st.column_config.NumberColumn("Monto ($)", format="$%,d"),
                            "Unidades": st.column_config.NumberColumn("Unidades", format="%,d"),
                            "Participación": st.column_config.ProgressColumn("Participación", format="%.1f%%", min_value=0, max_value=1),
                        },
                        hide_index=True,
                        use_container_width=True
                    )

            with c_cli_view:
                st.markdown("#### 🏆 Top Clientes por Facturación")
                if col_cliente in df_si_filt.columns and not df_si_filt.empty:
                    grp_cli = df_si_filt.groupby(col_cliente, as_index=False).agg({
                        col_monto: 'sum',
                        col_unid: 'sum'
                    }).sort_values(by=col_monto, ascending=False).head(10)

                    fig_bars = px.bar(
                        grp_cli.sort_values(by=col_monto, ascending=True),
                        x=col_monto,
                        y=col_cliente,
                        orientation='h',
                        text_auto='.2s',
                        color_discrete_sequence=[COLOR_CALIPSO_FARMA]
                    )
                    fig_bars.update_traces(textfont_size=11, textposition="outside", cliponaxis=False)
                    fig_bars.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=230,
                        xaxis_title="",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_bars, use_container_width=True, key=f"bars_cli_{i}")

                    df_cli_disp = pd.DataFrame({
                        "Cliente": grp_cli[col_cliente],
                        "Monto Total ($)": grp_cli[col_monto],
                        "Unidades": grp_cli[col_unid]
                    })
                    st.dataframe(
                        asegurar_columnas_unicas(df_cli_disp),
                        column_config={
                            "Monto Total ($)": st.column_config.NumberColumn("Monto Total ($)", format="$%,d"),
                            "Unidades": st.column_config.NumberColumn("Unidades", format="%,d"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )

            st.divider()
            st.subheader("📋 Registro Completo de Ventas SI")
            busqueda_si = st.text_input("🔍 Buscar en registros SI (Descripción, SKU, Factura, etc.):", key=f"search_si_{i}")
            df_si_det = df_si_filt.copy()
            if busqueda_si:
                mask_si = df_si_det.astype(str).apply(lambda x: x.str.contains(busqueda_si, case=False)).any(axis=1)
                df_si_det = df_si_det[mask_si]
            st.dataframe(asegurar_columnas_unicas(df_si_det), hide_index=True, use_container_width=True)

        # ----------------------------------------------------------------------
        # PESTAÑA STOCK / CADUCIDAD
        # ----------------------------------------------------------------------
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

            df_dash = df[df[col_cod].astype(str) == prod_sel].copy() if prod_sel != "Seleccione..." else df.copy()

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
                st.markdown(f'''
                <div class="kpi-card" style="margin-bottom:10px;">
                    <div class="kpi-title">Unidades Registradas</div>
                    <div class="kpi-value" style="color:#FFFFFF;">{formato_unidades(total_unidades)}</div>
                </div>
                <div class="kpi-card" style="margin-bottom:10px; border-color:{COLOR_ROJO_DANGER};">
                    <div class="kpi-title" style="color:{COLOR_ROJO_DANGER};">Unidades &lt; 6 Meses</div>
                    <div class="kpi-value" style="color:{COLOR_ROJO_DANGER};">{formato_unidades(total_menos_6m)}</div>
                </div>
                <div class="kpi-card" style="margin-bottom:10px; border-color:{COLOR_AMARILLO_WARN};">
                    <div class="kpi-title" style="color:{COLOR_AMARILLO_WARN};">Pronto Vence (6-13m)</div>
                    <div class="kpi-value" style="color:{COLOR_AMARILLO_WARN};">{formato_unidades(total_pronto)}</div>
                </div>
                <div class="kpi-card" style="border-color:{COLOR_VERDE_SUCCESS};">
                    <div class="kpi-title" style="color:{COLOR_VERDE_SUCCESS};">Vigentes (&gt; 13m)</div>
                    <div class="kpi-value" style="color:{COLOR_VERDE_SUCCESS};">{formato_unidades(total_vigentes)}</div>
                </div>
                ''', unsafe_allow_html=True)

            with col_dash2:
                st.markdown("#### Estado de Caducidad")
                labels = ['< 6 meses', '6 a 13 meses', 'Vigente (> 13m)']
                values = [total_menos_6m, total_pronto, total_vigentes]
                colors = [COLOR_ROJO_DANGER, COLOR_AMARILLO_WARN, COLOR_VERDE_SUCCESS]
                
                if sum(values) > 0:
                    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.55, marker=dict(colors=colors))])
                    fig_pie.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF"), showlegend=True, legend=dict(orientation="h", y=-0.1))
                    st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_stock_{i}")
                else:
                    st.info("Sin registros para mostrar.")

            with col_dash3:
                if prod_sel != "Seleccione...":
                    stock_actual = df_dash[col_cant].sum() if col_cant else 0
                    prox_vencer = df_dash[df_dash[col_fecha].notna()][col_fecha].min() if col_fecha else None
                    dias_vencer = (prox_vencer - hoy).days if pd.notna(prox_vencer) else "N/A"
                    
                    st.markdown(f'''
                    <div class="kpi-card" style="margin-bottom:10px;">
                        <div class="kpi-title">Stock Actual</div>
                        <div class="kpi-value">{formato_unidades(stock_actual)}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if isinstance(dias_vencer, int):
                        if prox_vencer < limite_6m:
                            texto_vence = f"Vence en {dias_vencer} días" if dias_vencer >= 0 else f"Venció hace {abs(dias_vencer)} días"
                            c_card = COLOR_ROJO_DANGER
                        elif prox_vencer <= limite_13m:
                            texto_vence = f"Vence en {dias_vencer} días"
                            c_card = COLOR_AMARILLO_WARN
                        else:
                            texto_vence = f"Vence en {dias_vencer} días"
                            c_card = COLOR_VERDE_SUCCESS
                    else:
                        texto_vence = "Sin fecha registrada"
                        c_card = COLOR_BORDER

                    st.markdown(f'''
                    <div class="kpi-card" style="border-color:{c_card};">
                        <div class="kpi-title">Plazo de Vencimiento</div>
                        <div class="kpi-value" style="color:{c_card};">{texto_vence}</div>
                    </div>
                    ''', unsafe_allow_html=True)

            st.divider()

            if col_estado_lote and col_estado_lote in df_dash.columns:
                st.markdown("##### 🏷️ Unidades por Estado de Lote")
                df_est_grp = df_dash.groupby(col_estado_lote, dropna=False)[col_cant].sum().reset_index() if col_cant else df_dash[col_estado_lote].value_counts().reset_index()
                
                if not df_est_grp.empty:
                    c_e, c_q = df_est_grp.columns[0], df_est_grp.columns[1]
                    num_items = len(df_est_grp)
                    cols_est = st.columns(min(num_items, 6))
                    for idx_e, row_e in df_est_grp.iterrows():
                        nombre_est = str(row_e[c_e]) if pd.notna(row_e[c_e]) else "Sin Estado"
                        cant_est = row_e[c_q]
                        with cols_est[idx_e % min(num_items, 6)]:
                            st.markdown(f'''
                                <div class="kpi-card">
                                    <div class="kpi-title">{nombre_est}</div>
                                    <div class="kpi-value" style="font-size:20px;">{formato_unidades(cant_est)}</div>
                                </div>
                            ''', unsafe_allow_html=True)

            st.subheader(f"📋 Detalle de Stock y Lotes {f'(SKU: {prod_sel})' if prod_sel != 'Seleccione...' else '(General)'}")
            
            cols_mostrar = []
            nombres_amigables = {}
            if col_cod: cols_mostrar.append(col_cod); nombres_amigables[col_cod] = "Código Artículo"
            if col_estado_sub: cols_mostrar.append(col_estado_sub); nombres_amigables[col_estado_sub] = "Estado Sub-Inv"
            if col_estado_lote: cols_mostrar.append(col_estado_lote); nombres_amigables[col_estado_lote] = "Estado Lote"
            if col_lote: cols_mostrar.append(col_lote); nombres_amigables[col_lote] = "Lote Proveedor"
            if col_loc: cols_mostrar.append(col_loc); nombres_amigables[col_loc] = "Localizador"
            if col_cant: cols_mostrar.append(col_cant); nombres_amigables[col_cant] = "Cantidad"
            if col_fecha: cols_mostrar.append(col_fecha); nombres_amigables[col_fecha] = "Fecha Expiración"
            cols_mostrar.append("Alerta_Caducidad"); nombres_amigables["Alerta_Caducidad"] = "Rango Caducidad"
            
            df_vista_stock = df_dash[cols_mostrar].copy()
            df_vista_stock = df_vista_stock.rename(columns=nombres_amigables)
            if "Fecha Expiración" in df_vista_stock.columns:
                df_vista_stock["Fecha Expiración"] = pd.to_datetime(df_vista_stock["Fecha Expiración"], errors='coerce').dt.strftime('%d-%m-%Y')
            
            st.dataframe(asegurar_columnas_unicas(df_vista_stock), hide_index=True, use_container_width=True)

        # ----------------------------------------------------------------------
        # PESTAÑAS SB Y PU (FILL RATE Y QUIEBRES)
        # ----------------------------------------------------------------------
        elif is_sb or is_pu:
            col_semana = next((c for c in df.columns if c.strip().lower() in ['semana', 'sem', 'wk', 'week']), None) or next((c for c in df.columns if 'semana' in c.lower() or 'sem' in c.lower()), None)
            col_sku = next((c for c in df.columns if c.strip().lower() in ['id_producto', 'id_product', 'id_prod', 'sku', 'cod_sku', 'codigo_sku', 'codigo', 'cod_prod', 'material']), None) or next((c for c in df.columns if any(k in c.lower() for k in ['id_prod', 'producto_id', 'sku', 'cod_prod'])), None)
            col_oc = next((c for c in df.columns if c.strip().lower() in ['oc', 'orden_compra', 'orden de compra', 'num_oc', 'numero_oc', 'orden', 'numero_orden']), None) or next((c for c in df.columns if 'oc' in c.lower() or 'orden' in c.lower()), None)
            col_desc = next((c for c in df.columns if c.strip().lower() in ['descripcion', 'desc_producto', 'producto', 'desc', 'nombre']), None) or next((c for c in df.columns if 'desc' in c.lower() or 'nombre' in c.lower() or 'prod' in c.lower()), None)
            col_div = next((c for c in df.columns if c.strip().lower() in ['division', 'categoría', 'categoria', 'linea', 'div', 'cat']), None) or next((c for c in df.columns if 'divis' in c.lower() or 'categ' in c.lower() or 'linea' in c.lower()), None)
            col_marca = next((c for c in df.columns if c.strip().lower() in ['marca', 'brand', 'lab', 'laboratorio', 'proveedor']), None) or next((c for c in df.columns if any(k in c.lower() for k in ['marca', 'brand', 'lab', 'proveedor'])), None)
            
            col_u_compra = next((c for c in df.columns if c.lower().strip() in ['unidades_compra', 'unidades compra', 'unid_compra', 'cant_compra', 'unidades_pedidas', 'unidades_solicitadas']), None) or next((c for c in df.columns if 'compra' in c.lower() and 'unid' in c.lower()), None)
            col_u_recib = next((c for c in df.columns if c.lower().strip() in ['unidades_recibidas', 'unidades recibidas', 'unid_recibidas', 'cant_recibida', 'unidades_entregadas']), None) or next((c for c in df.columns if 'recib' in c.lower() and 'unid' in c.lower()), None)
            
            col_m_compra = next((c for c in df.columns if c.lower().strip() in ['monto_compra', 'monto compra', 'total_compra', 'monto_pedido', 'monto_solicitado', 'val_compra', 'valor_compra']), None) or next((c for c in df.columns if any(k in c.lower() for k in ['comp', 'pedi', 'solic', 'total']) and any(k in c.lower() for k in ['monto', 'val', 'cost', '$'])), None)
            col_m_recib = next((c for c in df.columns if c.lower().strip() in ['recibidas', 'monto_recibido', 'monto recibido', 'total_recibido', 'monto_facturado', 'monto_entregado', 'val_recibido', 'valor_recibido']), None) or next((c for c in df.columns if any(k in c.lower() for k in ['recib', 'fact', 'entre']) and any(k in c.lower() for k in ['monto', 'val', 'cost', 'total', '$'])), None)
            col_precio = next((c for c in df.columns if any(k in c.lower() for k in ['precio', 'costo_unitario', 'p_unitario', 'precio_costo', 'puc', 'precio_final'])), None)
            col_quiebre = next((c for c in df.columns if 'quiebre' in c.lower() or 'monto_falta' in c.lower()), None)
            col_rechazado = next((c for c in df.columns if 'rechaz' in c.lower() or 'devuel' in c.lower()), None)

            if not col_sku or col_sku not in df.columns: col_sku = df.columns[0]
            if not col_desc or col_desc not in df.columns: col_desc = col_sku

            df[col_sku] = df[col_sku].apply(fmt_code)
            df[col_desc] = df[col_desc].fillna("Sin Descripción").astype(str)
            if col_semana and col_semana in df.columns: df[col_semana] = df[col_semana].apply(fmt_sem)

            if not col_u_compra or col_u_compra not in df.columns: df["unidades_compra_calc"] = 0; col_u_compra = "unidades_compra_calc"
            if not col_u_recib or col_u_recib not in df.columns: df["unidades_recibidas_calc"] = 0; col_u_recib = "unidades_recibidas_calc"
            if not col_precio or col_precio not in df.columns: df["precio_calc"] = 0; col_precio = "precio_calc"

            cols_a_num = [c for c in [col_u_compra, col_u_recib, col_m_compra, col_m_recib, col_precio, col_quiebre, col_rechazado] if c and c in df.columns]
            for c_num in cols_a_num: df[c_num] = pd.to_numeric(df[c_num], errors='coerce').fillna(0)

            if not col_m_compra or col_m_compra not in df.columns:
                df["monto_compra_calc"] = df[col_u_compra] * df[col_precio]
                col_m_compra = "monto_compra_calc"
            if not col_m_recib or col_m_recib not in df.columns:
                df["monto_recibido_calc"] = df[col_u_recib] * df[col_precio]
                col_m_recib = "monto_recibido_calc"

            df['quiebre_monto_calc'] = (df[col_m_compra] - df[col_m_recib]).clip(lower=0)
            df['quiebre_unid_calc'] = (df[col_u_compra] - df[col_u_recib]).clip(lower=0)

            # Filtro por Semanas (Botones Pill Tabs)
            semanas_todas = sorted([s for s in df[col_semana].unique() if pd.notna(s) and s != ""], key=lambda x: float(x) if str(x).replace('.','',1).isdigit() else 0) if col_semana else []
            opciones_semanas = ["Todas"] + [f"Semana {s}" for s in semanas_todas]
            
            idx_defecto = len(opciones_semanas) - 1 if len(opciones_semanas) > 1 else 0
            
            st.markdown("#### 📅 Selección de Semana Operativa")
            semana_sel_raw = st.radio("Semana", list(range(len(opciones_semanas))), format_func=lambda x: opciones_semanas[x], index=idx_defecto, horizontal=True, key=f"semana_sel_{nombre_hoja}_{i}")
            semana_sel = opciones_semanas[semana_sel_raw].replace("Semana ", "")

            df_filt = df.copy()
            if semana_sel != "Todas" and col_semana:
                df_filt = df_filt[df_filt[col_semana] == semana_sel]

            st.divider()

            # Relojes Gauge de Fill Rate
            if col_semana:
                sem_actual = semana_sel if semana_sel != "Todas" else (semanas_todas[-1] if semanas_todas else None)
                if sem_actual is not None:
                    df_sem_curr = df[df[col_semana] == sem_actual].copy()
                    
                    if is_pu:
                        tot_c = df_sem_curr[col_m_compra].sum()
                        tot_r = df_sem_curr[col_m_recib].sum()
                        fr_tot = (tot_r / tot_c * 100) if tot_c > 0 else 0.0
                        
                        st.markdown(f"### ⏱️ Fill Rate W{fmt_sem(sem_actual)} (PU General)")
                        _, col_r2, _ = st.columns([1, 2, 1])
                        with col_r2:
                            fig_g = crear_reloj_gauge("FILL RATE GLOBAL", fr_tot, COLOR_AZUL_ACCENT)
                            st.plotly_chart(fig_g, use_container_width=True, key=f"gauge_pu_{nombre_hoja}_{i}")
                            
                    elif is_sb and col_div:
                        grp_curr = df_sem_curr.groupby(col_div)[[col_m_compra, col_m_recib]].sum().reset_index()
                        fr_consumo_monto, fr_farma_monto = 0.0, 0.0
                        for _, row in grp_curr.iterrows():
                            div_name = str(row[col_div]).upper()
                            pct = (row[col_m_recib] / row[col_m_compra] * 100) if row[col_m_compra] > 0 else 0.0
                            if "CONSUMO" in div_name: fr_consumo_monto = pct
                            elif "FARMA" in div_name: fr_farma_monto = pct

                        st.markdown(f"### ⏱️ Fill Rate W{fmt_sem(sem_actual)}")
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            fig_g_cons = crear_reloj_gauge("CONSUMO MASIVO", fr_consumo_monto, COLOR_NARANJA_CONSUMO)
                            st.plotly_chart(fig_g_cons, use_container_width=True, key=f"gauge_cons_{nombre_hoja}_{i}")
                        with col_r2:
                            fig_g_farma = crear_reloj_gauge("FARMA", fr_farma_monto, COLOR_CALIPSO_FARMA)
                            st.plotly_chart(fig_g_farma, use_container_width=True, key=f"gauge_farma_{nombre_hoja}_{i}")

            st.divider()

            # TOP 15 QUIEBRES
            st.subheader(f"🔥 TOP 15 Quiebres {'(Global)' if is_pu else '(Por División)'}")
            crit_orden = st.radio("Ordenar TOP 15 por:", ["Monto ($)", "Unidades"], horizontal=True, key=f"top_crit_{nombre_hoja}_{i}")

            sem_top = semana_sel if semana_sel != "Todas" else (semanas_todas[-1] if semanas_todas else None)
            df_sem_top = df[df[col_semana] == sem_top].copy() if (sem_top is not None and col_semana) else df.copy()

            # Mapeo OC Abierta Siguiente Semana
            try:
                sem_curr_num = float(sem_top)
                semanas_nums = [float(s) for s in semanas_todas if str(s).replace('.','',1).isdigit()]
                semanas_futuras = [s for s in semanas_nums if s > sem_curr_num]
                sem_sig = fmt_sem(min(semanas_futuras)) if semanas_futuras else None
            except (ValueError, TypeError):
                sem_sig = None

            oc_abierta_map = {}
            if sem_sig and col_semana:
                df_sig = df[df[col_semana] == sem_sig]
                grp_sig = df_sig.groupby(col_sku)[col_u_compra].sum()
                oc_abierta_map = grp_sig.to_dict()

            if is_pu:
                grp_top = df_sem_top.groupby([col_sku, col_desc], as_index=False).agg({
                    col_u_compra: 'sum',
                    col_m_compra: 'sum',
                    'quiebre_monto_calc': 'sum',
                    'quiebre_unid_calc': 'sum'
                })
                if col_rechazado and col_rechazado in df_sem_top.columns:
                    grp_r = df_sem_top.groupby([col_sku, col_desc], as_index=False)[col_rechazado].sum()
                    grp_top = pd.merge(grp_top, grp_r, on=[col_sku, col_desc], how='left')
                else:
                    grp_top["Suma de RECHAZADO"] = 0

                grp_top["OC abierta"] = grp_top[col_sku].map(oc_abierta_map).fillna(0)
                col_sort = 'quiebre_monto_calc' if crit_orden == "Monto ($)" else 'quiebre_unid_calc'
                grp_top = grp_top.sort_values(by=col_sort, ascending=False).head(15)

                if not grp_top.empty:
                    grp_top_disp = pd.DataFrame()
                    grp_top_disp["SKU"] = grp_top[col_sku].astype(str)
                    grp_top_disp["Descripción"] = grp_top[col_desc]
                    grp_top_disp["Unidades Compra"] = grp_top[col_u_compra].apply(formato_unidades)
                    grp_top_disp["Compra Total ($)"] = grp_top[col_m_compra].apply(formato_moneda)
                    grp_top_disp["Quiebre ($)"] = grp_top['quiebre_monto_calc'].apply(lambda x: f"-{formato_moneda(abs(x))}" if x > 0 else "$0")
                    col_r_name = col_rechazado if (col_rechazado and col_rechazado in grp_top.columns) else "Suma de RECHAZADO"
                    grp_top_disp["Rechazado (Unds)"] = grp_top[col_r_name].apply(formato_unidades)
                    lbl_oc = f"OC Abierta Sem {fmt_sem(sem_sig)}" if sem_sig else "OC Abierta"
                    grp_top_disp[lbl_oc] = grp_top["OC abierta"].apply(formato_unidades)

                    st.dataframe(asegurar_columnas_unicas(grp_top_disp), hide_index=True, use_container_width=True)

            elif is_sb and col_div:
                divisiones_unicas = [d for d in df_sem_top[col_div].dropna().unique()]
                div_cons = next((d for d in divisiones_unicas if "CONSUMO" in str(d).upper()), None)
                div_farm = next((d for d in divisiones_unicas if "FARMA" in str(d).upper()), None)
                lista_divs = [d for d in [div_cons, div_farm] if d is not None]
                if not lista_divs and len(divisiones_unicas) > 0: lista_divs = divisiones_unicas[:2]

                col_t1, col_t2 = st.columns(2)
                columnas_ui = [col_t1, col_t2]

                for idx, div_nombre in enumerate(lista_divs):
                    if idx >= 2: break
                    with columnas_ui[idx]:
                        df_div = df_sem_top[df_sem_top[col_div] == div_nombre].copy()
                        tot_compra_m = df_div[col_m_compra].sum()
                        tot_recib_m = df_div[col_m_recib].sum()
                        fr_div_pct = (tot_recib_m / tot_compra_m * 100) if tot_compra_m > 0 else 0.0
                        
                        st.markdown(f"#### 📌 {str(div_nombre).upper()}")
                        st.metric(label=f"Fill Rate (Sem {fmt_sem(sem_top)})", value=f"{fr_div_pct:.1f}%", delta=f"{tot_recib_m - tot_compra_m:,.0f} $ (Dif)".replace(",", "."))

                        grp_top = df_div.groupby([col_sku, col_desc], as_index=False).agg({
                            col_u_compra: 'sum',
                            col_m_compra: 'sum',
                            'quiebre_monto_calc': 'sum',
                            'quiebre_unid_calc': 'sum'
                        })
                        if col_rechazado and col_rechazado in df_div.columns:
                            grp_r = df_div.groupby([col_sku, col_desc], as_index=False)[col_rechazado].sum()
                            grp_top = pd.merge(grp_top, grp_r, on=[col_sku, col_desc], how='left')
                        else:
                            grp_top["Suma de RECHAZADO"] = 0

                        grp_top["OC abierta"] = grp_top[col_sku].map(oc_abierta_map).fillna(0)
                        col_sort = 'quiebre_monto_calc' if crit_orden == "Monto ($)" else 'quiebre_unid_calc'
                        grp_top = grp_top.sort_values(by=col_sort, ascending=False).head(15)

                        if not grp_top.empty:
                            grp_top_disp = pd.DataFrame()
                            grp_top_disp["SKU"] = grp_top[col_sku].astype(str)
                            grp_top_disp["Descripción"] = grp_top[col_desc]
                            grp_top_disp["Quiebre ($)"] = grp_top['quiebre_monto_calc'].apply(lambda x: f"-{formato_moneda(abs(x))}" if x > 0 else "$0")
                            col_r_name = col_rechazado if (col_rechazado and col_rechazado in grp_top.columns) else "Suma de RECHAZADO"
                            grp_top_disp["Rechazado (Unds)"] = grp_top[col_r_name].apply(formato_unidades)
                            lbl_oc = f"OC Abierta Sem {fmt_sem(sem_sig)}" if sem_sig else "OC Abierta"
                            grp_top_disp[lbl_oc] = grp_top["OC abierta"].apply(formato_unidades)

                            st.dataframe(asegurar_columnas_unicas(grp_top_disp), hide_index=True, use_container_width=True)

            st.divider()

            # 📊 EVOLUTIVO DE 4 SEMANAS
            st.subheader("📊 Evolutivo Fill Rate (Últimas 4 Semanas)")
            
            semanas_4 = semanas_todas[-4:] if len(semanas_todas) >= 4 else semanas_todas
            df_4sem = df[df[col_semana].isin(semanas_4)].copy() if col_semana else pd.DataFrame()

            if not df_4sem.empty:
                if is_pu:
                    grp = df_4sem.groupby(col_semana, as_index=False).agg({
                        col_u_compra: 'sum', col_u_recib: 'sum',
                        col_m_compra: 'sum', col_m_recib: 'sum'
                    })
                    grp["FR_Unds_pct"] = (grp[col_u_recib] / grp[col_u_compra] * 100).fillna(0)
                    grp["FR_Monto_pct"] = (grp[col_m_recib] / grp[col_m_compra] * 100).fillna(0)

                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        st.markdown("##### Fill Rate por Unidades (Evolutivo)")
                        fig_unds = go.Figure(go.Bar(
                            x=[f"Sem {fmt_sem(s)}" for s in grp[col_semana]],
                            y=grp["FR_Unds_pct"],
                            text=[f"{v:.1f}%" for v in grp["FR_Unds_pct"]],
                            textposition="auto",
                            marker_color=COLOR_AZUL_ACCENT
                        ))
                        fig_unds.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF"), yaxis=dict(range=[0, 115], gridcolor=COLOR_BORDER, ticksuffix="%"))
                        st.plotly_chart(fig_unds, use_container_width=True, key=f"plot_unds_{nombre_hoja}_{i}")

                    with col_g2:
                        st.markdown("##### Fill Rate por Monto (Evolutivo)")
                        fig_monto = go.Figure(go.Bar(
                            x=[f"Sem {fmt_sem(s)}" for s in grp[col_semana]],
                            y=grp["FR_Monto_pct"],
                            text=[f"{v:.1f}%" for v in grp["FR_Monto_pct"]],
                            textposition="auto",
                            marker_color=COLOR_CALIPSO_FARMA
                        ))
                        fig_monto.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF"), yaxis=dict(range=[0, 115], gridcolor=COLOR_BORDER, ticksuffix="%"))
                        st.plotly_chart(fig_monto, use_container_width=True, key=f"plot_monto_{nombre_hoja}_{i}")

                elif is_sb and col_div:
                    grp = df_4sem.groupby([col_semana, col_div], as_index=False)[[col_m_compra, col_m_recib]].sum()
                    grp["FR_Monto"] = (grp[col_m_recib] / grp[col_m_compra] * 100).fillna(0)
                    
                    tot_sem = df_4sem.groupby(col_semana, as_index=False)[[col_m_compra, col_m_recib]].sum()
                    tot_sem["Total_FR_Monto"] = (tot_sem[col_m_recib] / tot_sem[col_m_compra] * 100).fillna(0)

                    p_monto = grp.pivot(index=col_semana, columns=col_div, values="FR_Monto").fillna(0).reset_index()

                    fig_monto = go.Figure()
                    for col_d in p_monto.columns:
                        if col_d == col_semana: continue
                        color_bar = COLOR_NARANJA_CONSUMO if "CONSUMO" in str(col_d).upper() else COLOR_CALIPSO_FARMA
                        fig_monto.add_trace(go.Bar(
                            x=[f"Sem {fmt_sem(s)}" for s in p_monto[col_semana]],
                            y=p_monto[col_d],
                            name=str(col_d).title(),
                            marker_color=color_bar
                        ))

                    fig_monto.add_trace(go.Scatter(
                        x=[f"Sem {fmt_sem(s)}" for s in tot_sem[col_semana]],
                        y=tot_sem["Total_FR_Monto"],
                        name="Total Semana",
                        mode="lines+markers+text",
                        text=[f"{v:.1f}%" for v in tot_sem["Total_FR_Monto"]],
                        textposition="top center",
                        line=dict(color="#E2E8F0", width=3)
                    ))

                    fig_monto.update_layout(
                        barmode="group",
                        height=360,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#FFFFFF"),
                        yaxis=dict(range=[0, 115], gridcolor=COLOR_BORDER, ticksuffix="%"),
                        legend=dict(orientation="h", y=-0.2)
                    )
                    st.plotly_chart(fig_monto, use_container_width=True, key=f"plot_monto_sb_{i}")

            st.divider()

            # RESUMEN QUIEBRES POR MARCA
            if sem_top is not None and col_marca:
                st.subheader("🏷️ Resumen Quiebres por Marca")
                df_sem_marca = df[df[col_semana] == sem_top].copy()
                
                grp_m = df_sem_marca.groupby(col_marca, as_index=False).agg({col_m_compra: 'sum', 'quiebre_monto_calc': 'sum'})
                grp_m = grp_m[grp_m['quiebre_monto_calc'] > 0]
                
                if not grp_m.empty:
                    total_quiebre_div = grp_m['quiebre_monto_calc'].sum()
                    grp_m['pct_quiebre'] = (grp_m['quiebre_monto_calc'] / total_quiebre_div * 100) if total_quiebre_div > 0 else 0.0
                    grp_m = grp_m.sort_values(by='quiebre_monto_calc', ascending=False)
                    
                    fila_total = pd.DataFrame({
                        col_marca: ['TOTAL GENERAL'],
                        col_m_compra: [grp_m[col_m_compra].sum()],
                        'quiebre_monto_calc': [total_quiebre_div],
                        'pct_quiebre': [100.0]
                    })
                    grp_m_final = pd.concat([grp_m, fila_total], ignore_index=True)
                    
                    grp_m_disp = pd.DataFrame()
                    grp_m_disp["Marca"] = grp_m_final[col_marca]
                    grp_m_disp["Compra ($)"] = grp_m_final[col_m_compra].apply(formato_moneda)
                    grp_m_disp["Quiebre ($)"] = grp_m_final['quiebre_monto_calc'].apply(formato_moneda)
                    grp_m_disp["% Quiebre"] = grp_m_final['pct_quiebre']

                    st.dataframe(
                        asegurar_columnas_unicas(grp_m_disp).style.apply(aplicar_criticidad, subset=['% Quiebre']),
                        column_config={"% Quiebre": st.column_config.NumberColumn("% Quiebre", format="%.1f%%")},
                        hide_index=True,
                        use_container_width=True
                    )

            st.divider()

            # DETALLE Y REGISTROS FILTRADOS CON DESDUPLICACIÓN
            st.subheader(f"📋 Registro de Órdenes y Filas ({nombre_hoja})")
            
            f1, f2 = st.columns(2)
            with f1:
                ocs_disponibles = ["Todas"] + sorted([str(x) for x in df_filt[col_oc].dropna().unique()]) if col_oc and col_oc in df_filt.columns else ["Todas"]
                oc_seleccionada = st.selectbox("Filtrar por Orden de Compra (OC):", ocs_disponibles, key=f"det_oc_{nombre_hoja}_{i}")
            with f2:
                skus_det_disponibles = ["Todos"] + sorted([str(x) for x in df_filt[col_sku].dropna().unique()]) if col_sku and col_sku in df_filt.columns else ["Todos"]
                sku_det_seleccionado = st.selectbox("Filtrar Detalle por SKU:", skus_det_disponibles, key=f"det_sku_{nombre_hoja}_{i}")

            df_detalle = df_filt.copy()
            if col_oc and oc_seleccionada != "Todas":
                df_detalle = df_detalle[df_detalle[col_oc].astype(str) == oc_seleccionada]
            if col_sku and sku_det_seleccionado != "Todos":
                df_detalle = df_detalle[df_detalle[col_sku].astype(str) == sku_det_seleccionado]

            renombrar_columnas = {
                "id_producto": "SKU", "sku": "SKU", "codigo": "SKU",
                "semana": "Semana", "sem": "Semana", "num_oc": "OC",
                "orden_compra": "OC", "descripcion": "Descripción", "unidades_compra": "Unidades Compra",
                "unidades_recibidas": "Unidades Recibidas", "unidades_rechazadas": "Unidades Rechazadas",
                "cantidad": "Unidades Compra", "cantidad_recibida": "Unidades Recibidas",
                "fecha_hora_despacho_default": "Fecha Despacho", "precio_final": "Precio Final",
                "precio_total": "Precio Total"
            }

            # Aplicar renombrado seguro
            df_corte_final = df_detalle.copy()
            nuevas_columnas = {}
            for col in df_corte_final.columns:
                col_lower = str(col).strip().lower()
                if col_lower in renombrar_columnas:
                    nuevas_columnas[col] = renombrar_columnas[col_lower]
                else:
                    nuevas_columnas[col] = str(col).replace('_', ' ').strip().title()

            df_corte_final = df_corte_final.rename(columns=nuevas_columnas)

            # APLICAR DESDUPLICACIÓN DE COLUMNAS PARA EVITAR ERROR DE STREAMLIT
            df_corte_final = asegurar_columnas_unicas(df_corte_final)

            st.dataframe(df_corte_final, hide_index=True, use_container_width=True)

        # ----------------------------------------------------------------------
        # PARA OTRAS PESTAÑAS AUXILIARES
        # ----------------------------------------------------------------------
        else:
            busqueda = st.text_input(f"🔍 Buscar en {nombre_hoja}:", key=f"search_{nombre_hoja}_{i}")
            df_aux = df.copy()
            if busqueda:
                mask = df_aux.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
                df_aux = df_aux[mask]
            st.dataframe(asegurar_columnas_unicas(df_aux), hide_index=True, use_container_width=True)
