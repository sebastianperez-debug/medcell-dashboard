import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. Configuración de la página
st.set_page_config(page_title="Medcell Operaciones", layout="wide")

# 2. Estilos personalizados
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


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
  if pd.isna(val) or val == "" or val is None or str(val).lower() == "nan":
    return "S/N"
  val_str = str(val).strip()
  if val_str.endswith(".0"):
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
      styles.append("font-weight: bold; background-color: #1a1a1a;")
    elif val >= 15.0:
      styles.append(
          "background-color: #8b0000; color: #ffffff; font-weight: bold;"
      )
    elif val >= 10.0:
      styles.append(
          "background-color: #b91c1c; color: #ffffff; font-weight: bold;"
      )
    elif val >= 5.0:
      styles.append("background-color: #c2410c; color: #ffffff;")
    elif val > 0:
      styles.append("background-color: #27272a; color: #d4d4d8;")
    else:
      styles.append("")
  return styles


# --- 3. CARGA DEL EXCEL ---
def buscar_excel():
  posibles_rutas = [
      "SQL Seba.xlsx",
      "SQL Seba.xls",
      r"C:\Users\sebastianperez\Desktop\QUERY REDSHIFT\SQL Seba.xlsx",
      r"C:\Users\sebastianperez\Desktop\QUERY REDSHIFT\SQL Seba.xls",
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
    df_temp = df_temp.loc[:, ~df_temp.columns.str.startswith("Unnamed")]
    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
    hojas_dict[hoja] = df_temp
  return hojas_dict


if not ruta_final:
  st.error(
      "⚠️ No se encontró el archivo 'SQL Seba.xlsx' en la ruta especificada."
  )
  st.stop()

try:
  hojas = cargar_libro_excel(ruta_final)
except Exception as e:
  st.error(f"Error al leer Excel: {e}")
  st.stop()

# --- 4. HEADER ---
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


def crear_reloj_gauge(titulo, porcentaje, color_barra):
  fig = go.Figure(
      go.Indicator(
          mode="gauge+number",
          value=porcentaje,
          number={"suffix": "%", "font": {"size": 28, "color": "#ffffff"}},
          title={
              "text": f"<b>{titulo}</b>",
              "font": {"size": 16, "color": "#cccccc"},
          },
          gauge={
              "axis": {"range": [0, 100], "ticksuffix": "%"},
              "bar": {"color": color_barra, "thickness": 0.4},
              "bgcolor": "#1a1a1a",
              "borderwidth": 1,
              "bordercolor": "#333333",
              "steps": [
                  {"range": [0, 50], "color": "#281a1a"},
                  {"range": [50, 80], "color": "#28241a"},
                  {"range": [80, 100], "color": "#1a281f"},
              ],
              "threshold": {
                  "line": {"color": "#ffffff", "width": 3},
                  "thickness": 0.8,
                  "value": porcentaje,
              },
          },
      )
  )
  fig.update_layout(
      height=210,
      margin=dict(l=25, r=25, t=35, b=15),
      paper_bgcolor="rgba(0,0,0,0)",
      font=dict(color="#ffffff"),
  )
  return fig


# --- 5. PESTAÑAS ---
HOJAS_A_EXCLUIR = [
    "sku",
    "maestra",
    "precio",
    "nivel de servicio sb",
    "venta perdida sb",
    "nivel de servicio pu",
]
nombres_hojas = [
    h for h in hojas.keys() if h.strip().lower() not in HOJAS_A_EXCLUIR
]

tabs = st.tabs([f"📊 {h}" for h in nombres_hojas])

for i, nombre_hoja in enumerate(nombres_hojas):
  with tabs[i]:
    df = hojas[nombre_hoja].copy()
    nombre_clean = nombre_hoja.strip().upper()

    is_sb = nombre_clean == "SB"
    is_pu = nombre_clean == "PU"
    is_stock = nombre_clean == "STOCK"
    is_si = nombre_clean == "SI"

    # =================================================================
    # PESTAÑA VENTA SI
    # =================================================================
    if is_si:
      st.markdown("### 📈 Dashboard Operativo de Venta SI")

      col_cliente = next(
          (c for c in df.columns if "cliente" in c.lower()), "nombre_cliente"
      )
      col_div = next(
          (
              c
              for c in df.columns
              if "division" in c.lower() or "división" in c.lower()
          ),
          "Division",
      )
      col_monto = next(
          (c for c in df.columns if "monto" in c.lower()), "monto"
      )
      col_unid = next(
          (
              c
              for c in df.columns
              if "unidad" in c.lower() or "cantidad" in c.lower()
          ),
          "cantidad_unidades",
      )
      col_pmp = next(
          (c for c in df.columns if "pmp" in c.lower()), "pmp_mes_actual"
      )
      col_inflamable = next(
          (c for c in df.columns if "inflamable" in c.lower()), "es_inflamable"
      )
      col_factura = next(
          (
              c
              for c in df.columns
              if "factura" in c.lower() or "orden" in c.lower()
          ),
          "Factura",
      )

      df[col_monto] = (
          pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
          if col_monto in df.columns
          else 0
      )
      df[col_unid] = (
          pd.to_numeric(df[col_unid], errors="coerce").fillna(0)
          if col_unid in df.columns
          else 0
      )
      df[col_pmp] = (
          pd.to_numeric(df[col_pmp], errors="coerce").fillna(0)
          if col_pmp in df.columns
          else 0
      )

      st.markdown("#### 🎛️ Filtros de Control")
      f_col1, f_col2, f_col3 = st.columns(3)

      with f_col1:
        divs_unicas = (
            ["Todas"] + sorted([str(x) for x in df[col_div].dropna().unique()])
            if col_div in df.columns
            else ["Todas"]
        )
        div_sel = st.selectbox(
            "Filtrar por División:", divs_unicas, key=f"f_div_{i}"
        )

      with f_col2:
        clientes_unicos = (
            ["Todos"]
            + sorted([str(x) for x in df[col_cliente].dropna().unique()])
            if col_cliente in df.columns
            else ["Todos"]
        )
        cliente_sel = st.selectbox(
            "Filtrar por Cliente:", clientes_unicos, key=f"f_cli_{i}"
        )

      with f_col3:
        inflamable_opts = (
            ["Todos"]
            + sorted([str(x) for x in df[col_inflamable].dropna().unique()])
            if col_inflamable in df.columns
            else ["Todos"]
        )
        inflamable_sel = st.selectbox(
            "Producto Inflamable:", inflamable_opts, key=f"f_inf_{i}"
        )

      df_si_filt = df.copy()
      if div_sel != "Todas" and col_div in df_si_filt.columns:
        df_si_filt = df_si_filt[df_si_filt[col_div].astype(str) == div_sel]
      if cliente_sel != "Todos" and col_cliente in df_si_filt.columns:
        df_si_filt = df_si_filt[
            df_si_filt[col_cliente].astype(str) == cliente_sel
        ]
      if inflamable_sel != "Todos" and col_inflamable in df_si_filt.columns:
        df_si_filt = df_si_filt[
            df_si_filt[col_inflamable].astype(str) == inflamable_sel
        ]

      st.divider()

      st.markdown("#### 📊 KPIs Generales")
      monto_total = df_si_filt[col_monto].sum()
      unidades_totales = df_si_filt[col_unid].sum()
      costo_pmp_total = (df_si_filt[col_unid] * df_si_filt[col_pmp]).sum()
      ticket_promedio = (
          (monto_total / unidades_totales) if unidades_totales > 0 else 0
      )
      num_facturas = (
          df_si_filt[col_factura].nunique()
          if col_factura in df_si_filt.columns
          else len(df_si_filt)
      )

      k1, k2, k3, k4, k5 = st.columns(5)
      k1.metric("Monto Total Facturado", formato_moneda(monto_total))
      k2.metric("Unidades Vendidas", formato_unidades(unidades_totales))
      k3.metric("Ticket Promedio / Unid", formato_moneda(ticket_promedio))
      k4.metric("Costo PMP Total", formato_moneda(costo_pmp_total))
      k5.metric("N° Transacciones/Facturas", formato_unidades(num_facturas))

      st.divider()

      c_div_view, c_cli_view = st.columns([1, 1.2], gap="large")

      with c_div_view:
        st.markdown("#### 🏢 Venta por División")
        if col_div in df_si_filt.columns and not df_si_filt.empty:
          grp_div = df_si_filt.groupby(col_div, as_index=False).agg(
              {col_monto: "sum", col_unid: "sum"}
          )
          grp_div["Participación"] = (
              (grp_div[col_monto] / monto_total) if monto_total > 0 else 0
          )
          grp_div = grp_div.sort_values(by=col_monto, ascending=False)

          fig_donut = px.pie(
              grp_div,
              values=col_monto,
              names=col_div,
              hole=0.5,
              color_discrete_sequence=[
                  "#0070f3",
                  "#109618",
                  "#f97316",
                  "#ff9900",
              ],
          )
          fig_donut.update_traces(
              textposition="inside",
              textinfo="percent+label",
              marker=dict(line=dict(color="#0b0b0b", width=2)),
          )
          fig_donut.update_layout(
              template="plotly_dark",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              margin=dict(t=10, b=10, l=10, r=10),
              height=220,
              showlegend=False,
          )
          st.plotly_chart(
              fig_donut, use_container_width=True, key=f"donut_div_{i}"
          )

          grp_div_disp = pd.DataFrame({
              "División": grp_div[col_div],
              "Monto ($)": grp_div[col_monto],
              "Unidades": grp_div[col_unid],
              "Participación": grp_div["Participación"],
          })

          st.dataframe(
              grp_div_disp,
              column_config={
                  "Monto ($)": st.column_config.NumberColumn(
                      "Monto ($)", format="$%,d"
                  ),
                  "Unidades": st.column_config.NumberColumn(
                      "Unidades", format="%,d"
                  ),
                  "Participación": st.column_config.ProgressColumn(
                      "Participación", format="%.1f%%", min_value=0, max_value=1
                  ),
              },
              hide_index=True,
              use_container_width=True,
          )
        else:
          st.info("No hay datos de división disponibles.")

      with c_cli_view:
        st.markdown("#### 🏆 Top Clientes por Facturación")
        if col_cliente in df_si_filt.columns and not df_si_filt.empty:
          grp_cli = (
              df_si_filt.groupby(col_cliente, as_index=False)
              .agg({col_monto: "sum", col_unid: "sum"})
              .sort_values(by=col_monto, ascending=False)
              .head(10)
          )

          grp_cli_sorted = grp_cli.sort_values(by=col_monto, ascending=True)
          fig_bars = px.bar(
              grp_cli_sorted,
              x=col_monto,
              y=col_cliente,
              orientation="h",
              text_auto=".2s",
              color_discrete_sequence=["#00CC96"],
          )
          fig_bars.update_traces(
              textfont_size=11, textposition="outside", cliponaxis=False
          )
          fig_bars.update_layout(
              template="plotly_dark",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              margin=dict(t=10, b=10, l=10, r=10),
              height=220,
              xaxis_title="",
              yaxis_title="",
          )
          st.plotly_chart(
              fig_bars, use_container_width=True, key=f"bars_cli_{i}"
          )

          grp_cli_disp = pd.DataFrame({
              "Cliente": grp_cli[col_cliente],
              "Monto Total ($)": grp_cli[col_monto],
              "Unidades": grp_cli[col_unid],
          })

          st.dataframe(
              grp_cli_disp,
              column_config={
                  "Monto Total ($)": st.column_config.NumberColumn(
                      "Monto Total ($)", format="$%,d"
                  ),
                  "Unidades": st.column_config.NumberColumn(
                      "Unidades", format="%,d"
                  ),
              },
              hide_index=True,
              use_container_width=True,
          )
        else:
          st.info("No hay datos de clientes disponibles.")

      st.divider()

      st.subheader("📋 Registro Completo de Ventas SI")
      busqueda_si = st.text_input(
          "🔍 Buscar en registros SI (Descripción, SKU, Factura, etc.):",
          key=f"search_si_{i}",
      )

      df_si_det = df_si_filt.copy()
      if busqueda_si:
        mask_si = (
            df_si_det.astype(str)
            .apply(lambda x: x.str.contains(busqueda_si, case=False))
            .any(axis=1)
        )
        df_si_det = df_si_det[mask_si]

      st.caption(f"Mostrando {len(df_si_det)} registros.")
      st.dataframe(df_si_det, hide_index=True, use_container_width=True)

    # =================================================================
    # DASHBOARD DE STOCK / CADUCIDAD
    # =================================================================
    elif is_stock:
      st.markdown("### 📦 Dashboard de Fecha de Caducidad")

      col_cod = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["codigo_articulo", "id_producto", "sku", "codigo"]
          ),
          None,
      )
      col_estado_sub = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["estado_subin", "sub_inventario", "estado sub inventario"]
          ),
          None,
      )
      col_estado_lote = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["estado_lote", "estado lote", "estado_lote_prov"]
          ),
          None,
      )
      col_lote = next(
          (
              c
              for c in df.columns
              if c.strip().lower() == "lote_proveedor"
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if c.strip().lower() in ["lote", "lote_prov"]
          ),
          None,
      )
      col_loc = next(
          (
              c
              for c in df.columns
              if c.strip().lower() in ["localizador", "ubicacion"]
          ),
          None,
      )
      col_fecha = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in [
                  "fecha_expiracion_lote",
                  "vencimiento",
                  "fecha expiracion",
                  "fecha_expiracion",
              ]
          ),
          None,
      )
      col_cant = next(
          (
              c
              for c in df.columns
              if c.strip().lower() in ["cantidad", "stock", "unidades"]
          ),
          None,
      )

      if col_cod and col_cod in df.columns:
        df[col_cod] = df[col_cod].apply(fmt_code)

      if col_cant:
        df[col_cant] = pd.to_numeric(df[col_cant], errors="coerce").fillna(0)

      hoy = pd.Timestamp.today()
      limite_6m = hoy + pd.DateOffset(months=6)
      limite_13m = hoy + pd.DateOffset(months=13)

      if col_fecha:
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")

        def calcular_alerta(fecha):
          if pd.isna(fecha):
            return "Sin Fecha"
          if fecha < limite_6m:
            return "Menos de 6 meses"
          elif fecha <= limite_13m:
            return "Pronto vence (6-13m)"
          else:
            return "Vigente (> 13m)"

        df["Alerta_Caducidad"] = df[col_fecha].apply(calcular_alerta)
      else:
        df["Alerta_Caducidad"] = "Sin Fecha"
        df[col_fecha] = "N/A"

      col_dash1, col_dash2, col_dash3 = st.columns([1, 1.5, 1.5])

      with col_dash3:
        if col_cod:
          lista_prods = sorted([str(x) for x in df[col_cod].dropna().unique()])
          prod_sel = st.selectbox(
              "Elija un producto (Código / SKU):",
              ["Seleccione..."] + lista_prods,
              key=f"sel_prod_{i}",
          )
        else:
          prod_sel = "Seleccione..."

      if prod_sel != "Seleccione...":
        df_dash = df[df[col_cod].astype(str) == prod_sel].copy()
      else:
        df_dash = df.copy()

      if col_cant:
        total_unidades = df_dash[col_cant].sum()
        total_menos_6m = df_dash[
            df_dash["Alerta_Caducidad"] == "Menos de 6 meses"
        ][col_cant].sum()
        total_pronto = df_dash[
            df_dash["Alerta_Caducidad"] == "Pronto vence (6-13m)"
        ][col_cant].sum()
        total_vigentes = df_dash[
            df_dash["Alerta_Caducidad"] == "Vigente (> 13m)"
        ][col_cant].sum()
      else:
        total_unidades = len(df_dash)
        total_menos_6m = len(
            df_dash[df_dash["Alerta_Caducidad"] == "Menos de 6 meses"]
        )
        total_pronto = len(
            df_dash[df_dash["Alerta_Caducidad"] == "Pronto vence (6-13m)"]
        )
        total_vigentes = len(
            df_dash[df_dash["Alerta_Caducidad"] == "Vigente (> 13m)"]
        )

      with col_dash1:
        st.markdown(
            """
                <style>
                .stock-card { border-radius: 5px; padding: 15px; margin-bottom: 10px; text-align: center; color: white; font-weight: bold; }
                </style>
                """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="stock-card" style="background-color: #333; color:'
            ' white;">Unidades Registradas<br><span'
            f' style="font-size:24px;">{formato_unidades(total_unidades)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color:'
            ' #e74c3c;">Unidades < 6 meses<br><span'
            f' style="font-size:24px;">{formato_unidades(total_menos_6m)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color: #f1c40f; color:'
            ' black;">Pronto vence (6 a 13 meses)<br><span'
            f' style="font-size:24px;">{formato_unidades(total_pronto)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color:'
            ' #2ecc71;">Vigentes (> 13 meses)<br><span'
            f' style="font-size:24px;">{formato_unidades(total_vigentes)}</span></div>',
            unsafe_allow_html=True,
        )

      with col_dash2:
        st.markdown("#### Estado de caducidad")
        labels = ["< 6 meses", "6 a 13 meses", "Vigente (> 13m)"]
        values = [total_menos_6m, total_pronto, total_vigentes]
        colors = ["#e74c3c", "#f1c40f", "#2ecc71"]

        if sum(values) > 0:
          fig_pie = go.Figure(
              data=[
                  go.Pie(
                      labels=labels,
                      values=values,
                      hole=0.5,
                      marker=dict(colors=colors),
                  )
              ]
          )
          fig_pie.update_layout(
              height=300,
              margin=dict(t=0, b=0, l=0, r=0),
              paper_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#ffffff"),
              showlegend=True,
              legend=dict(orientation="h", y=-0.1),
          )
          st.plotly_chart(
              fig_pie, use_container_width=True, key=f"pie_stock_{i}"
          )
        else:
          st.info("Sin registros para mostrar.")

      with col_dash3:
        if prod_sel != "Seleccione...":
          stock_actual = df_dash[col_cant].sum() if col_cant else 0
          prox_vencer = (
              df_dash[df_dash[col_fecha].notna()][col_fecha].min()
              if col_fecha
              else None
          )
          dias_vencer = (
              (prox_vencer - hoy).days if pd.notna(prox_vencer) else "N/A"
          )

          st.markdown(
              '<div class="stock-card" style="background-color: #7f8c8d;">Stock'
              ' actual<br><span'
              f' style="font-size:24px;">{formato_unidades(stock_actual)}</span></div>',
              unsafe_allow_html=True,
          )

          if isinstance(dias_vencer, int):
            if prox_vencer < limite_6m:
              texto_vence = (
                  f"Vence en {dias_vencer} días"
                  if dias_vencer >= 0
                  else f"Venció hace {abs(dias_vencer)} días"
              )
              color_vence = "#e74c3c"
              color_texto = "color: white;"
            elif prox_vencer <= limite_13m:
              texto_vence = f"Vence en {dias_vencer} días"
              color_vence = "#f1c40f"
              color_texto = "color: black;"
            else:
              texto_vence = f"Vence en {dias_vencer} días"
              color_vence = "#2ecc71"
              color_texto = "color: white;"
          else:
            texto_vence = "Sin fecha registrada"
            color_vence = "#333333"
            color_texto = "color: white;"

          st.markdown(
              f'<div class="stock-card" style="background-color: {color_vence};'
              f' {color_texto} border: 1px solid #555;">Plazo de'
              f' vencimiento<br><span style="font-size:20px;">{texto_vence}</span></div>',
              unsafe_allow_html=True,
          )

      st.divider()

      st.subheader("📋 Registro de Inventario")
      busqueda_stock = st.text_input(
          "🔍 Buscar en inventario (SKU, Lote, Sub-inventario, etc.):",
          key=f"search_stock_{i}",
      )

      df_vista_stock = df.copy()
      if busqueda_stock:
        mask_st = (
            df_vista_stock.astype(str)
            .apply(lambda x: x.str.contains(busqueda_stock, case=False))
            .any(axis=1)
        )
        df_vista_stock = df_vista_stock[mask_st]

      renombrar_stock = {
          col_cod: "SKU",
          col_estado_sub: "Estado Sub-inventario",
          col_estado_lote: "Estado Lote",
          col_lote: "Lote",
          col_loc: "Localizador",
          col_fecha: "Fecha Expiración",
          col_cant: "Unidades Stock",
      }
      cols_validas = {
          k: v for k, v in renombrar_stock.items() if k and k in df_vista_stock
      }
      df_vista_stock = df_vista_stock.rename(columns=cols_validas)

      if "Fecha Expiración" in df_vista_stock.columns:
        df_vista_stock["Fecha Expiración"] = pd.to_datetime(
            df_vista_stock["Fecha Expiración"], errors="coerce"
        ).dt.strftime("%d-%m-%Y")

      st.dataframe(df_vista_stock, hide_index=True, use_container_width=True)

    # =================================================================
    # LÓGICA ORIGINAL PARA SB Y PU
    # =================================================================
    elif is_sb or is_pu:
      col_semana = next(
          (
              c
              for c in df.columns
              if c.strip().lower() in ["semana", "sem", "wk", "week"]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if "semana" in c.lower() or "sem" in c.lower()
          ),
          None,
      )
      col_sku = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in [
                  "id_producto",
                  "id_product",
                  "id_prod",
                  "sku",
                  "cod_sku",
                  "codigo_sku",
                  "codigo",
                  "cod_prod",
                  "material",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(
                  k in c.lower()
                  for k in ["id_prod", "producto_id", "sku", "cod_prod"]
              )
          ),
          None,
      )
      col_oc = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in [
                  "oc",
                  "orden_compra",
                  "orden de compra",
                  "num_oc",
                  "numero_oc",
                  "orden",
                  "numero_orden",
              ]
          ),
          None,
      ) or next(
          (c for c in df.columns if "oc" in c.lower() or "orden" in c.lower()),
          None,
      )
      col_desc = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["descripcion", "desc_producto", "producto", "desc", "nombre"]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if "desc" in c.lower()
              or "nombre" in c.lower()
              or "prod" in c.lower()
          ),
          None,
      )
      col_div = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["division", "categoría", "categoria", "linea", "div", "cat"]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if "divis" in c.lower()
              or "categ" in c.lower()
              or "linea" in c.lower()
          ),
          None,
      )
      col_marca = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["marca", "brand", "laboratorio", "lab", "proveedor"]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if "marca" in c.lower()
              or "lab" in c.lower()
              or "prov" in c.lower()
          ),
          None,
      )

      col_u_compra = next(
          (
              c
              for c in df.columns
              if c.lower().strip()
              in [
                  "unidades_compra",
                  "unidades compra",
                  "unid_compra",
                  "cant_compra",
                  "unidades_pedidas",
                  "unidades pedidas",
                  "cantidad_pedida",
                  "cant_pedida",
                  "unidades",
                  "cantidad",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(
                  k in c.lower()
                  for k in ["compra", "pedid", "solicit", "solic", "unid"]
              )
              and not any(
                  k in c.lower() for k in ["recib", "monto", "val", "cost", "$"]
              )
          ),
          None,
      )
      col_u_recib = next(
          (
              c
              for c in df.columns
              if c.lower().strip()
              in [
                  "unidades_recibidas",
                  "unidades recibidas",
                  "unid_recibidas",
                  "cant_recibida",
                  "unidades_entregadas",
                  "cant_entregada",
                  "recibidas",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(k in c.lower() for k in ["recib", "entreg", "factur"])
              and not any(
                  k in c.lower() for k in ["monto", "val", "cost", "$"]
              )
          ),
          None,
      )

      col_m_compra = next(
          (
              c
              for c in df.columns
              if c.lower().strip()
              in [
                  "monto_compra",
                  "monto compra",
                  "total_compra",
                  "monto_pedido",
                  "monto pedido",
                  "monto_solicitado",
                  "val_compra",
                  "valor_compra",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(
                  k in c.lower() for k in ["monto", "val", "cost", "total", "$"]
              )
              and any(k in c.lower() for k in ["comp", "pedi", "solic"])
          ),
          None,
      )
      col_m_recib = next(
          (
              c
              for c in df.columns
              if c.lower().strip()
              in [
                  "recibidas",
                  "monto_recibido",
                  "monto recibido",
                  "total_recibido",
                  "monto_facturado",
                  "monto_entregado",
                  "val_recibido",
                  "valor_recibido",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(k in c.lower() for k in ["recib", "fact", "entre"])
              and any(
                  k in c.lower() for k in ["monto", "val", "cost", "total", "$"]
              )
          ),
          None,
      )

      col_precio = next(
          (
              c
              for c in df.columns
              if any(
                  k in c.lower()
                  for k in [
                      "precio",
                      "costo_unitario",
                      "p_unitario",
                      "precio_costo",
                      "puc",
                      "precio_final",
                  ]
              )
          ),
          None,
      )
      col_quiebre = next(
          (
              c
              for c in df.columns
              if "quiebre" in c.lower() or "monto_falta" in c.lower()
          ),
          None,
      )
      col_rechazado = next(
          (
              c
              for c in df.columns
              if "rechaz" in c.lower() or "devuel" in c.lower()
          ),
          None,
      )

      if not col_sku or col_sku not in df.columns:
        col_sku = df.columns[0]
      if not col_desc or col_desc not in df.columns:
        col_desc = col_sku

      df[col_sku] = df[col_sku].apply(fmt_code)
      df[col_desc] = df[col_desc].fillna("Sin Descripción").astype(str)

      if col_semana and col_semana in df.columns:
        df[col_semana] = df[col_semana].apply(fmt_sem)

      if not col_u_compra or col_u_compra not in df.columns:
        df["unidades_compra_calc"] = 0
        col_u_compra = "unidades_compra_calc"
      if not col_u_recib or col_u_recib not in df.columns:
        df["unidades_recibidas_calc"] = 0
        col_u_recib = "unidades_recibidas_calc"
      if not col_precio or col_precio not in df.columns:
        df["precio_calc"] = 0
        col_precio = "precio_calc"

      cols_a_num = [
          c
          for c in [
              col_u_compra,
              col_u_recib,
              col_m_compra,
              col_m_recib,
              col_precio,
              col_quiebre,
              col_rechazado,
          ]
          if c and c in df.columns
      ]
      for coln in cols_a_num:
        df[coln] = pd.to_numeric(df[coln], errors="coerce").fillna(0)

      if not col_m_compra or col_m_compra not in df.columns:
        df["monto_compra_calc"] = df[col_u_compra] * df[col_precio]
        col_m_compra = "monto_compra_calc"
      if not col_m_recib or col_m_recib not in df.columns:
        df["monto_recibido_calc"] = df[col_u_recib] * df[col_precio]
        col_m_recib = "monto_recibido_calc"

      df["quiebre_monto_calc"] = (df[col_m_compra] - df[col_m_recib]).apply(
          lambda x: max(0, x)
      )
      df["quiebre_unid_calc"] = (df[col_u_compra] - df[col_u_recib]).apply(
          lambda x: max(0, x)
      )

      semanas_todas = []
      if col_semana and col_semana in df.columns:
        semanas_todas = sorted(
            [s for s in df[col_semana].dropna().unique() if str(s).strip()],
            key=lambda x: (
                float(x) if str(x).replace(".", "", 1).isdigit() else str(x)
            ),
        )

      opciones_semanas = (
          [f"W{fmt_sem(s)}" for s in semanas_todas] + ["Todas"]
          if semanas_todas
          else ["Todas"]
      )
      idx_defecto = len(opciones_semanas) - 2 if semanas_todas else 0

      st.markdown("#### 📅 Selecciona la Semana")
      semana_sel_raw = st.radio(
          "Selecciona la Semana",
          range(len(opciones_semanas)),
          format_func=lambda x: opciones_semanas[x],
          index=idx_defecto,
          horizontal=True,
          key=f"semana_sel_{nombre_hoja}_{i}",
      )
      semana_sel = (
          semanas_todas[semana_sel_raw]
          if semana_sel_raw < len(semanas_todas)
          else "Todas"
      )

      df_filt = df.copy()
      if semana_sel != "Todas" and col_semana:
        df_filt = df_filt[df_filt[col_semana] == semana_sel]

      st.divider()

      if col_semana:
        sem_actual = (
            semana_sel
            if semana_sel != "Todas"
            else (semanas_todas[-1] if semanas_todas else None)
        )
        if sem_actual is not None:
          df_sem_curr = df[df[col_semana] == sem_actual].copy()
          if is_pu:
            tot_c = df_sem_curr[col_m_compra].sum()
            tot_r = df_sem_curr[col_m_recib].sum()
            fr_tot = (tot_r / tot_c * 100) if tot_c > 0 else 0.0
            st.markdown(
                f"### ⏱️ Fill rate W{fmt_sem(sem_actual)} (PU General)"
            )
            col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
            with col_r2:
              fig_g = crear_reloj_gauge("FILL RATE GLOBAL", fr_tot, "#0070f3")
              st.plotly_chart(
                  fig_g,
                  use_container_width=True,
                  key=f"gauge_pu_{nombre_hoja}_{i}",
              )
          elif is_sb and col_div:
            grp_curr = (
                df_sem_curr.groupby(col_div)[[col_m_compra, col_m_recib]]
                .sum()
                .reset_index()
            )
            fr_consumo_monto, fr_farma_monto = 0.0, 0.0
            for _, row in grp_curr.iterrows():
              div_name = str(row[col_div]).upper()
              pct = (
                  (row[col_m_recib] / row[col_m_compra] * 100)
                  if row[col_m_compra] > 0
                  else 0.0
              )
              if "CONSUMO" in div_name:
                fr_consumo_monto = pct
              elif "FARMA" in div_name:
                fr_farma_monto = pct
            st.markdown(f"### ⏱️ Fill rate W{fmt_sem(sem_actual)}")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
              fig_g_cons = crear_reloj_gauge(
                  "CONSUMO MASIVO", fr_consumo_monto, "#f97316"
              )
              st.plotly_chart(
                  fig_g_cons,
                  use_container_width=True,
                  key=f"gauge_cons_{nombre_hoja}_{i}",
              )
            with col_r2:
              fig_g_farma = crear_reloj_gauge(
                  "FARMA", fr_farma_monto, "#00adb5"
              )
              st.plotly_chart(
                  fig_g_farma,
                  use_container_width=True,
                  key=f"gauge_farma_{nombre_hoja}_{i}",
              )

      st.divider()

      # TOP 15
      st.subheader(
          f"🔥 TOP 15 Quiebres {'(Global)' if is_pu else '(Por División)'}"
      )
      crit_orden = st.radio(
          "Ordenar Top 15 por:",
          options=["Monto ($)", "Unidades"],
          horizontal=True,
          key=f"crit_top15_{nombre_hoja}_{i}",
      )
      sem_top = (
          semana_sel
          if semana_sel != "Todas"
          else (semanas_todas[-1] if semanas_todas else None)
      )

      lista_divs = []
      if sem_top is not None:
        sem_sig = None
        try:
          idx_curr = semanas_todas.index(sem_top)
          if idx_curr + 1 < len(semanas_todas):
            sem_sig = semanas_todas[idx_curr + 1]
          elif str(sem_top).isdigit():
            sem_sig = str(int(sem_top) + 1)
        except ValueError:
          if str(sem_top).isdigit():
            sem_sig = str(int(sem_top) + 1)

        oc_abierta_map = {}
        if sem_sig is not None:
          df_sig = df[df[col_semana] == sem_sig]
          oc_abierta_map = (
              df_sig.groupby(col_sku)[col_u_compra].sum().to_dict()
          )

        df_sem_top = df[df[col_semana] == sem_top].copy()

        if df_sem_top.empty:
          st.info(
              f"No se encontraron registros para la semana"
              f" {fmt_sem(sem_top)}."
          )
        else:
          if is_pu:
            # Cálculo adaptable a Unidades o Monto ($)
            if crit_orden == "Unidades":
              tot_compra = df_sem_top[col_u_compra].sum()
              tot_recib = df_sem_top[col_u_recib].sum()
              delta_txt = (
                  f"{formato_unidades(tot_recib - tot_compra)} Unds (Dif)"
              )
            else:
              tot_compra = df_sem_top[col_m_compra].sum()
              tot_recib = df_sem_top[col_m_recib].sum()
              delta_txt = (
                  f"{tot_recib - tot_compra:,.0f} $ (Dif)".replace(",", ".")
              )

            fr_div_pct = (
                (tot_recib / tot_compra * 100) if tot_compra > 0 else 0.0
            )

            st.markdown(f"#### 📌 RESUMEN GENERAL PU (Sem {fmt_sem(sem_top)})")
            st.metric(
                label="Fill Rate General",
                value=f"{fr_div_pct:.1f}%",
                delta=delta_txt,
            )

            grp_top = df_sem_top.groupby(
                [col_sku, col_desc], as_index=False
            ).agg({
                col_u_compra: "sum",
                col_m_compra: "sum",
                "quiebre_monto_calc": "sum",
                "quiebre_unid_calc": "sum",
            })

            if col_rechazado and col_rechazado in df_sem_top.columns:
              grp_rech = df_sem_top.groupby(
                  [col_sku, col_desc], as_index=False
              )[col_rechazado].sum()
              grp_top = pd.merge(
                  grp_top, grp_rech, on=[col_sku, col_desc], how="left"
              )
              grp_top[col_rechazado] = grp_top[col_rechazado].fillna(0)
            else:
              grp_top["Suma de RECHAZADO"] = 0

            grp_top["OC abierta"] = (
                grp_top[col_sku].map(oc_abierta_map).fillna(0)
            )
            col_sort = (
                "quiebre_monto_calc"
                if crit_orden == "Monto ($)"
                else "quiebre_unid_calc"
            )
            grp_top = grp_top.sort_values(by=col_sort, ascending=False).head(15)

            if not grp_top.empty:
              grp_top_disp = pd.DataFrame()
              grp_top_disp["SKU"] = grp_top[col_sku].astype(str)
              grp_top_disp["Descripción"] = grp_top[col_desc]
              grp_top_disp["Unidades Compra"] = grp_top[col_u_compra].apply(
                  formato_unidades
              )
              grp_top_disp["Compra Total ($)"] = grp_top[col_m_compra].apply(
                  formato_moneda
              )
              grp_top_disp["Quiebre ($)"] = grp_top["quiebre_monto_calc"].apply(
                  lambda x: f"-{formato_moneda(abs(x))}" if x > 0 else "$0"
              )
              col_r_name = (
                  col_rechazado
                  if (col_rechazado and col_rechazado in grp_top.columns)
                  else "Suma de RECHAZADO"
              )
              grp_top_disp["Rechazado (Unds)"] = grp_top[col_r_name].apply(
                  formato_unidades
