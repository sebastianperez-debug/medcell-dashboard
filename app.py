import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. Configuración de la página
st.set_page_config(page_title="Medcell Operaciones", layout="wide")

# 2. Estilos personalizados adaptados al logo de Medcell
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

    /* Pestañas */
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

# --- 3. CARGA DEL EXCEL ---
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
        df_temp = pd.read_excel(xls, hoja)
        df_temp.columns = [str(c).strip() for c in df_temp.columns]
        df_temp = df_temp.loc[:, ~df_temp.columns.str.startswith('Unnamed')]
        df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
        hojas_dict[hoja] = df_temp
    return hojas_dict

if not ruta_final:
    st.error("⚠️ No se encontró el archivo 'SQL Seba.xlsx' en el servidor.")
    st.stop()

try:
    hojas = cargar_libro_excel(ruta_final)
except Exception as e:
    st.error(f"Error al leer Excel: {e}")
    st.stop()

# --- 4. HEADER ---
st.markdown("""
    <div class="medcell-header">
        <div class="medcell-brand">MEDCELL <span>OPERACIONES</span></div>
        <div class="medcell-subtitle">SEGUIMIENTO DE CAMPAÑAS Y CONTROL DE FILL RATE</div>
        <div class="medcell-author">Desarrollado por Sebastián Alexis Pérez López</div>
    </div>
""", unsafe_allow_html=True)

def crear_reloj_gauge(titulo, porcentaje, color_barra):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=porcentaje,
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
        
        if nombre_hoja == "SB":
            # --- TITULO "SALCOBRAND (SB)" EN LA ESQUINA DERECHA ---
            _, c_head_right = st.columns([3, 2])
            with c_head_right:
                st.markdown("<h2 style='text-align: right; margin-bottom: 15px;'>💊 Salcobrand (SB)</h2>", unsafe_allow_html=True)

            # Detección de columnas
            col_semana = next((c for c in df.columns if c.strip().lower() == 'semana'), None) or next((c for c in df.columns if 'semana' in c.lower()), None)
            col_sku = next((c for c in df.columns if c.strip().lower() == 'sku'), None)
            col_oc = next((c for c in df.columns if c.strip().lower() in ['oc', 'orden_compra', 'orden de compra']), None) or next((c for c in df.columns if 'oc' in c.lower()), None)
            col_desc = next((c for c in df.columns if c.strip().lower() == 'descripcion'), None) or next((c for c in df.columns if 'desc' in c.lower()), col_sku)
            col_div = next((c for c in df.columns if c.strip().lower() == 'division'), None) or next((c for c in df.columns if 'divis' in c.lower()), None)
            
            # Columna Marca
            col_marca = next((c for c in df.columns if c.strip().lower() == 'marca'), None)
            if not col_marca:
                col_marca = next((c for c in df.columns if any(k in c.lower() for k in ['marca', 'brand', 'lab', 'proveedor'])), None)

            col_u_compra = next((c for c in df.columns if c.strip().lower() == 'unidades_compra'), None) or \
                           next((c for c in df.columns if 'comp' in c.lower() and 'unid' in c.lower()), "unidades_compra")
            col_u_recib = next((c for c in df.columns if c.strip().lower() == 'unidades_recibidas'), None) or \
                          next((c for c in df.columns if 'recib' in c.lower() and 'unid' in c.lower()), "unidades_recibidas")

            col_m_compra = next((c for c in df.columns if c.lower().strip() in ['compra total', 'monto_compra', 'monto compra', 'total_compra', 'costo_total']), None) or \
                           next((c for c in df.columns if any(k in c.lower() for k in ['monto', 'val', 'cost', 'total', '$']) and 'comp' in c.lower()), None)

            col_m_recib = next((c for c in df.columns if c.lower().strip() in ['recibidas', 'monto_recibido', 'monto recibido', 'total_recibido', 'monto_facturado']), None) or \
                          next((c for c in df.columns if any(k in c.lower() for k in ['recib', 'fact']) and any(k in c.lower() for k in ['monto', 'val', 'cost', 'total', '$'])), None)

            col_precio = next((c for c in df.columns if any(k in c.lower() for k in ['precio', 'costo_unitario', 'p_unitario'])), None)
            col_quiebre = next((c for c in df.columns if 'quiebre' in c.lower()), None)
            col_rechazado = next((c for c in df.columns if 'rechaz' in c.lower()), None)

            cols_a_num = [c for c in [col_u_compra, col_u_recib, col_m_compra, col_m_recib, col_precio, col_quiebre, col_rechazado] if c and c in df.columns]
            for c_num in cols_a_num:
                df[c_num] = pd.to_numeric(df[c_num], errors='coerce').fillna(0)

            if (not col_m_compra or col_m_compra not in df.columns) and col_precio:
                df["monto_compra_calc"] = df[col_u_compra] * df[col_precio]
                col_m_compra = "monto_compra_calc"

            if (not col_m_recib or col_m_recib not in df.columns) and col_precio:
                df["monto_recibido_calc"] = df[col_u_recib] * df[col_precio]
                col_m_recib = "monto_recibido_calc"
            elif (not col_m_recib or col_m_recib not in df.columns) and col_m_compra and col_m_compra in df.columns:
                precio_linea = (df[col_m_compra] / df[col_u_compra]).fillna(0)
                df["monto_recibido_calc"] = df[col_u_recib] * precio_linea
                col_m_recib = "monto_recibido_calc"

            if col_quiebre and col_quiebre in df.columns:
                df["quiebre_monto_calc"] = df[col_quiebre].abs()
            else:
                df["quiebre_monto_calc"] = (df[col_m_compra] - df[col_m_recib]).clip(lower=0)
                
            df["quiebre_unid_calc"] = (df[col_u_compra] - df[col_u_recib]).clip(lower=0)

            semanas_todas = sorted(list(df[col_semana].dropna().unique())) if col_semana else []
            ultimas_4_semanas = semanas_todas[-4:] if semanas_todas else []

            st.subheader("🔍 Filtros General de Consulta")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                semanas_disp = ["Todas"] + semanas_todas
                semana_sel = st.selectbox("Filtrar por Semana:", semanas_disp, key=f"sb_semana_{i}")
            with c_f2:
                skus_disp = ["Todos"] + sorted(list(df[col_sku].dropna().astype(str).unique())) if col_sku else ["Todos"]
                sku_sel = st.selectbox("Filtrar por SKU General:", skus_disp, key=f"sb_sku_{i}")

            df_filt = df.copy()
            if semana_sel != "Todas" and col_semana:
                df_filt = df_filt[df_filt[col_semana] == semana_sel]
            if sku_sel != "Todos" and col_sku:
                df_filt = df_filt[df_filt[col_sku].astype(str) == sku_sel]

            st.divider()

            # --- RELOJES (GAUGES) ---
            if col_semana and col_div:
                sem_actual = semana_sel if semana_sel != "Todas" else (semanas_todas[-1] if semanas_todas else None)
                if sem_actual:
                    df_sem_curr = df[df[col_semana] == sem_actual].copy()
                    if sku_sel != "Todos" and col_sku:
                        df_sem_curr = df_sem_curr[df_sem_curr[col_sku].astype(str) == sku_sel]

                    grp_curr = df_sem_curr.groupby(col_div)[[col_m_compra, col_m_recib]].sum().reset_index()

                    fr_consumo_monto = 0.0
                    fr_farma_monto = 0.0

                    for _, row in grp_curr.iterrows():
                        div_name = str(row[col_div]).upper()
                        m_c = row[col_m_compra]
                        m_r = row[col_m_recib]
                        pct = (m_r / m_c * 100) if m_c > 0 else 0.0
                        if "CONSUMO" in div_name: fr_consumo_monto = pct
                        elif "FARMA" in div_name: fr_farma_monto = pct

                    st.markdown(f"### ⏱️ Fill rate W{sem_actual}")
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        fig_g_cons = crear_reloj_gauge("CONSUMO MASIVO", fr_consumo_monto, "#f97316")
                        st.plotly_chart(fig_g_cons, use_container_width=True, key=f"gauge_cons_{i}")
                    with col_r2:
                        fig_g_farma = crear_reloj_gauge("FARMA", fr_farma_monto, "#00adb5")
                        st.plotly_chart(fig_g_farma, use_container_width=True, key=f"gauge_farma_{i}")

                    st.divider()

            # --- TOP 15 ---
            st.subheader("🔥 TOP 15 Quiebres por División")
            crit_orden = st.radio("Ordenar Top 15 por:", options=["Monto ($)", "Unidades"], horizontal=True, key=f"crit_top15_{i}")
            sem_top = semana_sel if semana_sel != "Todas" else (semanas_todas[-1] if semanas_todas else None)

            if sem_top and col_div and col_sku:
                sem_sig = None
                try:
                    idx_curr = semanas_todas.index(sem_top)
                    if idx_curr + 1 < len(semanas_todas): sem_sig = semanas_todas[idx_curr + 1]
                    elif isinstance(sem_top, (int, float)): sem_sig = sem_top + 1
                except ValueError:
                    if isinstance(sem_top, (int, float)): sem_sig = sem_top + 1

                oc_abierta_map = {}
                if sem_sig is not None:
                    df_sig = df[df[col_semana] == sem_sig]
                    oc_abierta_map = df_sig.groupby(col_sku)[col_u_compra].sum().to_dict()

                df_sem_top = df[df[col_semana] == sem_top].copy()
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
                        st.metric(
                            label=f"Fill Rate {div_nombre} (Sem {sem_top})", 
                            value=f"{fr_div_pct:.1f}%",
                            delta=f"{tot_recib_m - tot_compra_m:,.0f} $ (Dif)".replace(",", ".")
                        )

                        grp_top = df_div.groupby([col_sku, col_desc]).agg({
                            col_u_compra: 'sum', col_m_compra: 'sum',
                            'quiebre_monto_calc': 'sum', 'quiebre_unid_calc': 'sum'
                        }).reset_index()

                        if col_rechazado and col_rechazado in df_div.columns:
                            grp_rech = df_div.groupby([col_sku, col_desc])[col_rechazado].sum().reset_index()
                            grp_top = pd.merge(grp_top, grp_rech, on=[col_sku, col_desc], how='left')
                            grp_top[col_rechazado] = grp_top[col_rechazado].fillna(0)
                        else:
                            grp_top["Suma de RECHAZADO"] = 0

                        grp_top["OC abierta"] = grp_top[col_sku].map(oc_abierta_map).fillna(0)
                        col_sort = 'quiebre_monto_calc' if crit_orden == "Monto ($)" else 'quiebre_unid_calc'
                        grp_top = grp_top.sort_values(by=col_sort, ascending=False).head(15)

                        grp_top_disp = pd.DataFrame()
                        grp_top_disp["SKU"] = grp_top[col_sku].astype(str)
                        grp_top_disp["Descripción"] = grp_top[col_desc]
                        grp_top_disp["Unidades Compra"] = grp_top[col_u_compra].apply(formato_unidades)
                        grp_top_disp["Compra Total ($)"] = grp_top[col_m_compra].apply(formato_moneda)
                        grp_top_disp["Quiebre ($)"] = grp_top['quiebre_monto_calc'].apply(lambda x: f"-{formato_moneda(abs(x))}" if x > 0 else "$0")
                        
                        col_r_name = col_rechazado if (col_rechazado and col_rechazado in grp_top.columns) else "Suma de RECHAZADO"
                        grp_top_disp["Rechazado (Unds)"] = grp_top[col_r_name].apply(formato_unidades)
                        lbl_oc = f"OC Abierta Sem {sem_sig}" if sem_sig else "OC Abierta"
                        grp_top_disp[lbl_oc] = grp_top["OC abierta"].apply(formato_unidades)

                        st.dataframe(grp_top_disp, hide_index=True, use_container_width=True)

            st.divider()

            # --- TABLAS DINÁMICAS: QUIEBRE POR MARCA CON CRITICIDAD ---
            if sem_top and col_div and col_marca:
                st.subheader("🏷️ Resumen Quiebres por Marca")

                df_sem_marca = df[df[col_semana] == sem_top].copy()
                
                col_m1, col_m2 = st.columns(2)
                cols_marca_ui = [col_m1, col_m2]

                for idx, div_nombre in enumerate(lista_divs):
                    if idx >= 2: break

                    with cols_marca_ui[idx]:
                        st.markdown(f"#### {str(div_nombre).upper()}")

                        df_div_m = df_sem_marca[df_sem_marca[col_div] == div_nombre].copy()

                        grp_m = df_div_m.groupby(col_marca).agg({
                            col_m_compra: 'sum',
                            'quiebre_monto_calc': 'sum'
                        }).reset_index()

                        grp_m = grp_m[grp_m['quiebre_monto_calc'] > 0]

                        if not grp_m.empty:
                            total_quiebre_div = grp_m['quiebre_monto_calc'].sum()

                            grp_m['pct_quiebre'] = (grp_m['quiebre_monto_calc'] / total_quiebre_div * 100) if total_quiebre_div > 0 else 0.0
                            grp_m = grp_m.sort_values(by='quiebre_monto_calc', ascending=False)

                            grp_m_disp = pd.DataFrame()
                            grp_m_disp["Etiquetas de fila"] = grp_m[col_marca].astype(str)
                            grp_m_disp["TOTAL COMPRA"] = grp_m[col_m_compra].apply(formato_moneda)
                            grp_m_disp["MONTO QUIEBRE"] = grp_m['quiebre_monto_calc'].apply(lambda x: f"-{formato_moneda(abs(x))}")
                            grp_m_disp["QUIEBRE %"] = grp_m['pct_quiebre']

                            total_compra_div = grp_m[col_m_compra].sum()
                            fila_total = pd.DataFrame([{
                                "Etiquetas de fila": "Total general",
                                "TOTAL COMPRA": formato_moneda(total_compra_div),
                                "MONTO QUIEBRE": f"-{formato_moneda(abs(total_quiebre_div))}",
                                "QUIEBRE %": 100.0
                            }])

                            grp_m_final = pd.concat([grp_m_disp, fila_total], ignore_index=True)

                            def aplicar_criticidad(column):
                                is_total = grp_m_final["Etiquetas de fila"] == "Total general"
                                styles = []
                                for val, total in zip(column, is_total):
                                    if total:
                                        styles.append('font-weight: bold; background-color: #1a1a1a;')
                                    elif val >= 15.0:
                                        styles.append('background-color: #8b0000; color: #ffffff; font-weight: bold;')
                                    elif val >= 10.0:
                                        styles.append('background-color: #b91c1c; color: #ffffff; font-weight: bold;')
                                    elif val >= 5.0:
                                        styles.append('background-color: #c2410c; color: #ffffff;')
                                    elif val > 0:
                                        styles.append('background-color: #27272a; color: #d4d4d8;')
                                    else:
                                        styles.append('')
                                return styles

                            styled_df = grp_m_final.style.format({
                                "QUIEBRE %": "{:.2f}%"
                            }).apply(aplicar_criticidad, subset=["QUIEBRE %"])

                            st.dataframe(styled_df, hide_index=True, use_container_width=True)
                        else:
                            st.info(f"No hay quiebres registrados para {div_nombre} en la semana {sem_top}.")

                st.divider()

            # --- RESUMEN 4 SEMANAS ---
            if col_semana and col_div:
                df_base_fr = df.copy()
                if sku_sel != "Todos" and col_sku:
                    df_base_fr = df_base_fr[df_base_fr[col_sku].astype(str) == sku_sel]

                df_4sem = df_base_fr[df_base_fr[col_semana].isin(ultimas_4_semanas)].copy()

                grp = df_4sem.groupby([col_semana, col_div])[
                    [col_u_compra, col_u_recib, col_m_compra, col_m_recib]
                ].sum().reset_index()

                grp["FR_Unds_pct"] = (grp[col_u_recib] / grp[col_u_compra] * 100).fillna(0)
                grp["FR_Monto_pct"] = (grp[col_m_recib] / grp[col_m_compra] * 100).fillna(0)

                st.subheader("📊 Resumen Fill Rate (Últimas 4 Semanas)")
                
                df_disp = grp.copy()
                df_disp[col_u_compra] = df_disp[col_u_compra].apply(formato_unidades)
                df_disp[col_u_recib] = df_disp[col_u_recib].apply(formato_unidades)
                df_disp[col_m_compra] = df_disp[col_m_compra].apply(formato_moneda)
                df_disp[col_m_recib] = df_disp[col_m_recib].apply(formato_moneda)
                df_disp["FR_Unds_pct"] = df_disp["FR_Unds_pct"].apply(lambda x: f"{x:.2f}%")
                df_disp["FR_Monto_pct"] = df_disp["FR_Monto_pct"].apply(lambda x: f"{x:.2f}%")

                df_disp.columns = [
                    "Semana", "División", "Unidades Compra", "Unidades Recibidas", 
                    "Monto Compra ($)", "Monto Recibido ($)", "Fill Rate Unidades", "Fill Rate Monto"
                ]

                st.dataframe(df_disp, hide_index=True, use_container_width=True)
                st.divider()

                # --- GRÁFICOS ---
                col_g1, col_g2 = st.columns(2)
                p_unds = grp.pivot(index=col_semana, columns=col_div, values="FR_Unds_pct").reset_index()
                p_monto = grp.pivot(index=col_semana, columns=col_div, values="FR_Monto_pct").reset_index()

                tot_sem = df_4sem.groupby(col_semana)[[col_u_compra, col_u_recib, col_m_compra, col_m_recib]].sum().reset_index()
                tot_sem["Total_FR_Unds"] = (tot_sem[col_u_recib] / tot_sem[col_u_compra] * 100).fillna(0)
                tot_sem["Total_FR_Monto"] = (tot_sem[col_m_recib] / tot_sem[col_m_compra] * 100).fillna(0)

                with col_g1:
                    st.markdown("##### Fill Rate por Unidades")
                    fig_unds = go.Figure()

                    for col_d in [c for c in p_unds.columns if c != col_semana]:
                        color_bar = "#f97316" if "CONSUMO" in str(col_d).upper() else "#00adb5"
                        fig_unds.add_trace(go.Bar(x=[f"Sem {s}" for s in p_unds[col_semana]], y=p_unds[col_d], name=str(col_d).title(), marker_color=color_bar))

                    fig_unds.add_trace(go.Scatter(x=[f"Sem {s}" for s in tot_sem[col_semana]], y=tot_sem["Total_FR_Unds"], name="Total Semana", mode="lines+markers+text", text=[f"{v:.1f}%" for v in tot_sem["Total_FR_Unds"]], textposition="top center", line=dict(color="#e2e8f0", width=3)))
                    fig_unds.update_layout(barmode="group", height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"), yaxis=dict(range=[0, 115], gridcolor="#222222", ticksuffix="%"), xaxis=dict(gridcolor="#222222"), legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_unds, use_container_width=True, key=f"plot_unds_{i}")

                with col_g2:
                    st.markdown("##### Fill Rate por Monto")
                    fig_monto = go.Figure()

                    for col_d in [c for c in p_monto.columns if c != col_semana]:
                        color_bar = "#f97316" if "CONSUMO" in str(col_d).upper() else "#00adb5"
                        fig_monto.add_trace(go.Bar(x=[f"Sem {s}" for s in p_monto[col_semana]], y=p_monto[col_d], name=str(col_d).title(), marker_color=color_bar))

                    fig_monto.add_trace(go.Scatter(x=[f"Sem {s}" for s in tot_sem[col_semana]], y=tot_sem["Total_FR_Monto"], name="Total Semana", mode="lines+markers+text", text=[f"{v:.1f}%" for v in tot_sem["Total_FR_Monto"]], textposition="top center", line=dict(color="#e2e8f0", width=3)))
                    fig_monto.update_layout(barmode="group", height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"), yaxis=dict(range=[0, 115], gridcolor="#222222", ticksuffix="%"), xaxis=dict(gridcolor="#222222"), legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_monto, use_container_width=True, key=f"plot_monto_{i}")

            st.divider()

            # --- DETALLE DE REGISTRO CON SUS PROPIOS FILTROS (OC Y SKU) ---
            st.subheader("📋 Detalle de Registro de Compras")
            
            # Filtros específicos para la tabla de detalle
            col_det_f1, col_det_f2 = st.columns(2)
            with col_det_f1:
                ocs_disponibles = ["Todas"] + sorted([str(x) for x in df_filt[col_oc].dropna().unique()]) if col_oc and col_oc in df_filt.columns else ["Todas"]
                oc_seleccionada = st.selectbox("Filtrar Detalle por OC:", ocs_disponibles, key=f"det_oc_{i}")
            with col_det_f2:
                skus_det_disponibles = ["Todos"] + sorted([str(x) for x in df_filt[col_sku].dropna().unique()]) if col_sku and col_sku in df_filt.columns else ["Todos"]
                sku_det_seleccionado = st.selectbox("Filtrar Detalle por SKU:", skus_det_disponibles, key=f"det_sku_{i}")

            # Filtrado del detalle
            df_detalle = df_filt.copy()
            if col_oc and oc_seleccionada != "Todas":
                df_detalle = df_detalle[df_detalle[col_oc].astype(str) == oc_seleccionada]
            if col_sku and sku_det_seleccionado != "Todos":
                df_detalle = df_detalle[df_detalle[col_sku].astype(str) == sku_det_seleccionado]

            if col_rechazado and col_rechazado in df_detalle.columns:
                idx_corte = list(df_detalle.columns).index(col_rechazado) + 1
                df_corte_final = df_detalle.iloc[:, :idx_corte]
            else:
                df_corte_final = df_detalle

            st.dataframe(df_corte_final, hide_index=True, use_container_width=True)

        else:
            busqueda = st.text_input(f"🔍 Buscar en {nombre_hoja}:", key=f"search_{nombre_hoja}_{i}")
            if busqueda:
                mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
                df = df[mask]

            st.caption(f"Mostrando {len(df)} registros en {nombre_hoja}.")
            st.dataframe(df, hide_index=True, use_container_width=True)
