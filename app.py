import os
import re
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. Configuración de la página
# ==========================================
st.set_page_config(
    page_title="Medcell Operaciones",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. Estilos personalizados (Diseño Moderno Modo Oscuro)
# ==========================================
st.markdown(
    """
    <style>
    /* Estilos generales */
    .stApp { background-color: #08090a; color: #f3f4f6; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* Header principal */
    .medcell-header { 
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
        border: 1px solid #21262d;
        border-bottom: 3px solid #0070f3;
        border-radius: 12px;
        padding: 20px 24px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .medcell-brand { 
        font-size: 28px; 
        font-weight: 800; 
        letter-spacing: 1.5px; 
        color: #ffffff; 
        text-transform: uppercase; 
    }
    .medcell-brand span { color: #0070f3; }
    .medcell-subtitle { color: #8b949e; font-size: 13px; font-weight: 600; letter-spacing: 1px; margin-top: 4px; }
    .medcell-author { color: #6e7681; font-size: 11px; margin-top: 4px; font-style: italic; }

    /* Tarjetas KPI Personales */
    .kpi-card {
        background-color: #0d1117;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #30363d;
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #8b949e;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #f0f6fc;
        font-size: 24px;
        font-weight: 700;
        margin-top: 6px;
    }

    /* Estilo de Tarjetas de Filtro por Semana (Radio buttons) */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        margin-top: 8px !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label {
        background-color: #0d1117 !important;
        border: 1px solid #21262d !important;
        padding: 8px 18px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        color: #8b949e !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label:hover {
        border-color: #0070f3 !important;
        background-color: #161b22 !important;
        color: #ffffff !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label[data-checked="true"] {
        background-color: #0070f3 !important;
        border-color: #0070f3 !important;
        color: #ffffff !important;
        box-shadow: 0px 4px 12px rgba(0, 112, 243, 0.3);
    }

    /* Pestañas generales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; 
        background-color: #0d1117; 
        padding: 6px; 
        border-radius: 12px; 
        border: 1px solid #21262d; 
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px; 
        background-color: transparent; 
        border-radius: 8px; 
        color: #8b949e; 
        font-weight: 600; 
        font-size: 13px; 
        border: none; 
        padding: 0px 18px; 
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #f0f6fc; background-color: #161b22; }
    .stTabs [aria-selected="true"] { 
        background-color: #0070f3 !important; 
        color: #ffffff !important; 
        box-shadow: 0px 4px 12px rgba(0, 112, 243, 0.25); 
    }
    
    div[data-testid="stMetricValue"] { color: #f0f6fc !important; font-size: 24px !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 13px !important; }
    div[data-testid="stDataFrame"] { background-color: #0d1117; border-radius: 10px; border: 1px solid #21262d; }

    /* Responsivo móvil */
    @media (max-width: 768px) {
        div[data-testid="stRadio"] [role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            column-gap: 8px !important;
            row-gap: 8px !important;
        }
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stDataFrame"])):not(:has(div[data-testid="stPlotlyChart"])) {
            flex-wrap: wrap !important;
            row-gap: 12px !important;
        }
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stDataFrame"])):not(:has(div[data-testid="stPlotlyChart"])) > div[data-testid="stColumn"] {
            min-width: 47% !important;
            flex: 1 1 47% !important;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- Funciones auxiliares de formato y conversión ---
def limpiar_numero(val):
  if pd.isna(val) or val == "" or val is None or str(val).lower() == "nan":
    return 0.0
  if isinstance(val, (int, float)):
    return float(val)
  val_str = str(val).strip().replace("$", "").replace(" ", "")
  if not val_str:
    return 0.0

  if "." in val_str and "," in val_str:
    if val_str.rfind(",") > val_str.rfind("."):
      val_str = val_str.replace(".", "").replace(",", ".")
    else:
      val_str = val_str.replace(",", "")
  elif "," in val_str:
    if val_str.count(",") == 1:
      val_str = val_str.replace(",", ".")
    else:
      val_str = val_str.replace(",", "")
  elif "." in val_str:
    partes = val_str.split(".")
    if len(partes) > 2:
      val_str = val_str.replace(".", "")
    elif len(partes) == 2:
      if len(partes[1]) == 3 and len(partes[0]) <= 3:
        val_str = val_str.replace(".", "")

  try:
    return float(val_str)
  except (ValueError, TypeError):
    return 0.0


def limpiar_nombre_mes(col):
  if (
      pd.isna(col)
      or col is None
      or str(col).strip() == ""
      or str(col).lower() == "nan"
  ):
    return ""
  s = str(col).strip()

  if "-" in s and len(s) <= 8 and not s[0:4].isdigit():
    return s

  if "00:00:00" in s or (len(s) >= 10 and s[0:4].isdigit()):
    try:
      dt = pd.to_datetime(s)
      meses_es = [
          "ene",
          "feb",
          "mar",
          "abr",
          "may",
          "jun",
          "jul",
          "ago",
          "sept",
          "oct",
          "nov",
          "dic",
      ]
      return f"{meses_es[dt.month - 1]}-{str(dt.year)[-2:]}"
    except:
      pass

  try:
    dt = pd.to_datetime(s)
    meses_es = [
        "ene",
        "feb",
        "mar",
        "abr",
        "may",
        "jun",
        "jul",
        "ago",
        "sept",
        "oct",
        "nov",
        "dic",
      ]
    return f"{meses_es[dt.month - 1]}-{str(dt.year)[-2:]}"
  except:
    return s


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
  if pd.isna(val) or val == "" or val is None or str(val).lower() == "nan":
    return "S/N"
  val_str = str(val).strip()
  if val_str.endswith(".0"):
    val_str = val_str[:-2]
  return val_str


def formato_moneda(valor):
  try:
    val_int = int(round(valor))
    if val_int < 0:
      return f"-${abs(val_int):,}".replace(",", ".")
    return f"${val_int:,}".replace(",", ".")
  except (ValueError, TypeError):
    return "$0"


def formato_unidades(valor):
  try:
    val_int = int(round(valor))
    return f"{val_int:,}".replace(",", ".")
  except (ValueError, TypeError):
    return "0"


def parse_semana_int(val):
  try:
    return int(float(str(val).replace(",", ".")))
  except (ValueError, TypeError):
    return None


def semanas_del_mes_actual():
  hoy = datetime.now()
  primer_dia = hoy.replace(day=1)
  if hoy.month == 12:
    primer_dia_sig = hoy.replace(year=hoy.year + 1, month=1, day=1)
  else:
    primer_dia_sig = hoy.replace(month=hoy.month + 1, day=1)
  dias_mes = pd.date_range(primer_dia, primer_dia_sig - timedelta(days=1))
  return set(int(d.isocalendar()[1]) for d in dias_mes)


def aplicar_criticidad(column):
  is_total = column.index == (len(column) - 1)
  styles = []
  for i, val in enumerate(column):
    try:
      val_num = float(str(val).replace("%", "").replace(",", ".").strip())
    except (ValueError, TypeError):
      val_num = 0.0
    if is_total[i]:
      styles.append("font-weight: bold; background-color: #161b22;")
    elif val_num >= 15.0:
      styles.append(
          "background-color: #7f1d1d; color: #ffffff; font-weight: bold;"
      )
    elif val_num >= 10.0:
      styles.append(
          "background-color: #991b1b; color: #ffffff; font-weight: bold;"
      )
    elif val_num >= 5.0:
      styles.append("background-color: #c2410c; color: #ffffff;")
    elif val_num > 0:
      styles.append("background-color: #27272a; color: #d4d4d8;")
    else:
      styles.append("")
  return styles


@st.cache_data(ttl=60)
def cargar_hoja_raw(ruta, nombre_hoja):
  return pd.read_excel(ruta, sheet_name=nombre_hoja, header=None, dtype=object)


def _fr_num(valor):
  if valor is None:
    return None
  try:
    if isinstance(valor, str) and valor.strip() == "":
      return None
    numero = float(valor)
    if pd.isna(numero):
      return None
    return numero
  except (TypeError, ValueError):
    return None


def _fr_dedupe_columnas(cols):
  vistos = {}
  resultado = []
  for c in cols:
    if c not in vistos:
      vistos[c] = 0
      resultado.append(c)
    else:
      vistos[c] += 1
      resultado.append(f"{c} ({vistos[c]})")
  return resultado


def parse_bloques_fill_rate(df_raw):
  n_filas, n_cols = df_raw.shape
  bloques = []
  r = 0
  while r < n_filas:
    fila = df_raw.iloc[r]
    primer_val = (
        str(fila.iloc[0]).strip().lower()
        if n_cols > 0 and fila.iloc[0] is not None and not pd.isna(fila.iloc[0])
        else ""
    )
    if primer_val == "top" and r >= 2:
      header_row_idx = r
      idx_top = r - 1
      idx_total = r - 2

      header_vals = df_raw.iloc[header_row_idx]
      fila_total = df_raw.iloc[idx_total]
      fila_top = df_raw.iloc[idx_top]

      def _valores_kpi(fila_kpi):
        e = _fr_num(fila_kpi.iloc[4]) if n_cols > 4 else None
        f = _fr_num(fila_kpi.iloc[5]) if n_cols > 5 else None
        g = _fr_num(fila_kpi.iloc[6]) if n_cols > 6 else None
        h = _fr_num(fila_kpi.iloc[7]) if n_cols > 7 else None
        if h is not None:
          return {"cantidad": e, "monto": f, "quiebre": g, "fr": h}
        else:
          return {"cantidad": e, "monto": f, "quiebre": None, "fr": g}

      kpi_total = _valores_kpi(fila_total)
      kpi_top = _valores_kpi(fila_top)

      semana_val = fila_total.iloc[2] if n_cols > 2 else None

      etiqueta_b = (
          str(fila_top.iloc[1]).strip()
          if n_cols > 1
          and fila_top.iloc[1] is not None
          and not pd.isna(fila_top.iloc[1])
          else ""
      )
      etiqueta_c = (
          str(fila_top.iloc[2]).strip()
          if n_cols > 2
          and fila_top.iloc[2] is not None
          and not pd.isna(fila_top.iloc[2])
          else ""
      )
      titulo = " ".join(
          p for p in [etiqueta_b, etiqueta_c] if p and p.lower() != "nan"
      ).strip()

      fin = header_row_idx + 1
      while fin < n_filas:
        fila_chk = df_raw.iloc[fin]
        vacio = all(
            (v is None or pd.isna(v) or (isinstance(v, str) and v.strip() == ""))
            for v in fila_chk
        )
        primer_val_chk = (
            str(fila_chk.iloc[0]).strip().lower()
            if n_cols > 0
            and fila_chk.iloc[0] is not None
            and not pd.isna(fila_chk.iloc[0])
            else ""
        )
        if vacio or primer_val_chk == "top":
          break
        fin += 1

      tabla_datos = df_raw.iloc[header_row_idx + 1 : fin].copy()

      columnas_finales = []
      cols_validos = []
      for c in range(n_cols):
        nombre_c = header_vals.iloc[c]
        if nombre_c is not None and not pd.isna(nombre_c) and str(nombre_c).strip() != "":
          columnas_finales.append(str(nombre_c).strip())
          cols_validos.append(c)

      tabla_datos = tabla_datos.iloc[:, cols_validos]
      tabla_datos.columns = _fr_dedupe_columnas(columnas_finales)
      tabla_datos = tabla_datos.dropna(how="all").reset_index(drop=True)

      bloques.append(
          {
              "titulo": titulo,
              "semana": semana_val,
              "kpi_total": kpi_total,
              "kpi_top": kpi_top,
              "tabla": tabla_datos,
          }
      )
      r = fin
      continue
    r += 1
  return bloques


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

# --- 4. HEADER PRINCIPAL ---
st.markdown(
    """
    <div class="medcell-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="medcell-brand">MEDCELL <span>OPERACIONES</span></div>
                <div class="medcell-subtitle">MONITOR DE GESTIÓN OPERATIVA Y CONTROL DE INVENTARIO</div>
            </div>
            <div style="text-align: right;">
                <div class="medcell-author">Desarrollado por: <b>Sebastián Alexis Pérez López</b></div>
                <div style="font-size: 11px; color: #0070f3; font-weight: 600;">Chile | Sistema Activo</div>
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
          number={"suffix": "%", "font": {"size": 26, "color": "#ffffff"}},
          title={
              "text": f"<b>{titulo}</b>",
              "font": {"size": 14, "color": "#8b949e"},
          },
          gauge={
              "axis": {"range": [0, 100], "ticksuffix": "%"},
              "bar": {"color": color_barra, "thickness": 0.4},
              "bgcolor": "#161b22",
              "borderwidth": 1,
              "bordercolor": "#21262d",
              "steps": [
                  {"range": [0, 50], "color": "#2d1215"},
                  {"range": [50, 80], "color": "#2d2412"},
                  {"range": [80, 100], "color": "#122d1b"},
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
      height=200,
      margin=dict(l=20, r=20, t=30, b=10),
      paper_bgcolor="rgba(0,0,0,0)",
      font=dict(color="#ffffff"),
  )
  return fig


# --- 5. PESTAÑAS Y NAVEGACIÓN ---
HOJAS_A_EXCLUIR = [
    "sku",
    "maestra",
    "precio",
    "nivel de servicio sb",
    "venta perdida sb",
    "nivel de servicio pu",
    "hoja1",
]
nombres_hojas = [
    h for h in hojas.keys() if h.strip().lower() not in HOJAS_A_EXCLUIR
]

nombres_hojas = [
    h for h in nombres_hojas if h.strip().upper() != "STOCK"
] + [h for h in nombres_hojas if h.strip().upper() == "STOCK"]

nombres_fr = [h for h in nombres_hojas if h.strip().upper() == "FILL RATE"]
nombres_resto = [h for h in nombres_hojas if h.strip().upper() != "FILL RATE"]
nombres_hojas = nombres_resto[:2] + nombres_fr + nombres_resto[2:]

tabs = st.tabs(
    ["📊 RESUMEN"] + [f"📊 {h}" for h in nombres_hojas] + ["📷 Escanear"]
)

resumen_data = {}

for i, nombre_hoja in enumerate(nombres_hojas):
  with tabs[i + 1]:
    df = hojas[nombre_hoja].copy()
    nombre_clean = nombre_hoja.strip().upper()

    is_sb = nombre_clean == "SB"
    is_pu = nombre_clean == "PU"
    is_stock = nombre_clean == "STOCK"
    is_si = nombre_clean == "SI"
    is_si_proy = nombre_clean == "SI PROYECCION"
    is_fill_rate = nombre_clean == "FILL RATE"

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
      col_producto = next(
          (c for c in df.columns if "descripcion" in c.lower()), None
      )
      if not col_producto:
        col_producto = next(
            (c for c in df.columns if "producto" in c.lower()), None
        )
      if not col_producto and len(df.columns) > 9:
        col_producto = df.columns[9]
      col_sku_si = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in ["sku", "codigo_articulo", "codigo", "cod_articulo"]
          ),
          None,
      )
      col_prod_label = col_producto or col_sku_si

      df[col_monto] = (
          df[col_monto].apply(limpiar_numero) if col_monto in df.columns else 0
      )
      df[col_unid] = (
          df[col_unid].apply(limpiar_numero) if col_unid in df.columns else 0
      )
      df[col_pmp] = (
          df[col_pmp].apply(limpiar_numero) if col_pmp in df.columns else 0
      )

      # PANEL DE FILTROS EN CONTENEDOR AGRUPADO
      with st.container(border=True):
        st.markdown("<div style='font-size:14px; font-weight:700; margin-bottom:8px;'>🎛️ Panel de Filtros</div>", unsafe_allow_html=True)
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
      k5.metric("N° Transacciones", formato_unidades(num_facturas))

      st.divider()

      c_cli_view, c_div_view = st.columns([1.6, 1], gap="large")

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

          resumen_data["venta_div"] = {
              "filas": [
                  {
                      "division": str(r[col_div]),
                      "monto": float(r[col_monto]),
                      "participacion": float(r["Participación"]) * 100,
                  }
                  for _, r in grp_div.iterrows()
              ],
              "monto_total": float(monto_total),
          }

          fig_donut = px.pie(
              grp_div,
              values=col_monto,
              names=col_div,
              hole=0.55,
              color_discrete_sequence=[
                  "#0070f3",
                  "#10b981",
                  "#f59e0b",
                  "#8b5cf6",
              ],
          )
          fig_donut.update_traces(
              textposition="inside",
              textinfo="percent+label",
              marker=dict(line=dict(color="#08090a", width=2)),
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
        st.markdown("#### 🏆 Top Clientes por Facturación (Pareto)")
        if col_cliente in df_si_filt.columns and not df_si_filt.empty:
          grp_cli = (
              df_si_filt.groupby(col_cliente, as_index=False)
              .agg({col_monto: "sum", col_unid: "sum"})
              .sort_values(by=col_monto, ascending=False)
              .head(10)
              .reset_index(drop=True)
          )

          total_monto_cli = df_si_filt[col_monto].sum()
          grp_cli["Pct_Acumulado"] = (
              (grp_cli[col_monto].cumsum() / total_monto_cli * 100)
              if total_monto_cli > 0
              else 0
          )

          def _truncar_nombre(nombre, largo=16):
            nombre = str(nombre)
            return nombre if len(nombre) <= largo else nombre[: largo - 1] + "…"

          etiquetas_cli_cortas = grp_cli[col_cliente].apply(_truncar_nombre)

          fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
          fig_pareto.add_trace(
              go.Bar(
                  x=etiquetas_cli_cortas,
                  y=grp_cli[col_monto],
                  name="Monto ($)",
                  marker_color="#0070f3",
                  text=grp_cli[col_monto].apply(formato_moneda),
                  textposition="outside",
                  textfont=dict(size=10, color="#ffffff"),
                  customdata=grp_cli[col_cliente],
                  hovertemplate="%{customdata}<br>%{text}<extra></extra>",
              ),
              secondary_y=False,
          )
          fig_pareto.add_trace(
              go.Scatter(
                  x=etiquetas_cli_cortas,
                  y=grp_cli["Pct_Acumulado"],
                  name="% Acumulado",
                  mode="lines+markers+text",
                  line=dict(color="#10b981", width=2),
                  marker=dict(size=6, color="#10b981"),
                  text=grp_cli["Pct_Acumulado"].apply(lambda x: f"{x:.0f}%"),
                  textposition="top center",
                  textfont=dict(color="#10b981", size=10),
                  customdata=grp_cli[col_cliente],
                  hovertemplate="%{customdata}<br>%{y:.1f}%<extra></extra>",
              ),
              secondary_y=True,
          )
          fig_pareto.update_layout(
              template="plotly_dark",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              margin=dict(t=30, b=100, l=10, r=10),
              height=380,
              showlegend=False,
              xaxis=dict(
                  tickangle=-45,
                  tickfont=dict(size=10, color="#8b949e"),
                  automargin=True,
              ),
              uniformtext_minsize=8,
          )
          fig_pareto.update_yaxes(
              secondary_y=False, showgrid=False, title_text=""
          )
          fig_pareto.update_yaxes(
              secondary_y=True,
              range=[0, 115],
              ticksuffix="%",
              showgrid=False,
              title_text="",
          )
          st.plotly_chart(
              fig_pareto, use_container_width=True, key=f"pareto_cli_{i}"
          )

          grp_cli_disp = pd.DataFrame({
              "Cliente": grp_cli[col_cliente],
              "Monto Total ($)": grp_cli[col_monto],
              "Unidades": grp_cli[col_unid],
              "% Acumulado": grp_cli["Pct_Acumulado"],
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
                  "% Acumulado": st.column_config.ProgressColumn(
                      "% Acumulado", format="%.1f%%", min_value=0, max_value=100
                  ),
              },
              hide_index=True,
              use_container_width=True,
          )
        else:
          st.info("No hay datos de clientes disponibles.")

      st.divider()

      st.markdown("#### 📦 Top Productos por Venta")
      if col_prod_label and col_prod_label in df_si_filt.columns and not df_si_filt.empty:
        grp_prod = (
            df_si_filt.groupby(col_prod_label, as_index=False)
            .agg({col_monto: "sum", col_unid: "sum"})
            .sort_values(by=col_monto, ascending=False)
            .head(10)
        )

        grp_prod_sorted = grp_prod.sort_values(by=col_monto, ascending=True)
        fig_prod = px.bar(
            grp_prod_sorted,
            x=col_monto,
            y=col_prod_label,
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=["#0070f3"],
        )
        fig_prod.update_traces(
            textfont_size=11, textposition="outside", cliponaxis=False
        )
        fig_prod.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            xaxis_title="",
            yaxis_title="",
        )
        st.plotly_chart(
            fig_prod, use_container_width=True, key=f"bars_prod_{i}"
        )

        grp_prod_disp = pd.DataFrame({
            "Producto": grp_prod[col_prod_label],
            "Monto Total ($)": grp_prod[col_monto],
            "Unidades": grp_prod[col_unid],
        })

        st.dataframe(
            grp_prod_disp,
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
        st.info("No se encontró una columna de producto/SKU en esta hoja.")

      st.divider()

      st.subheader("📋 Registro Completo de Ventas SI")
      busqueda_si = st.text_input(
          "🔍 Buscar en registros SI (Descripción, SKU, Factura, etc.):",
          key=f"search_si_{i}",
      )

      df_si_det = df_si_filt.copy()

      if col_inflamable in df_si_det.columns:
        idx_corte = list(df_si_det.columns).index(col_inflamable) + 1
        df_si_det = df_si_det.iloc[:, :idx_corte]

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
    # DASHBOARD DE SI PROYECCION
    # =================================================================
    elif is_si_proy:
      st.markdown("### 📊 Dashboard de Proyección SI")

      if df.empty:
        st.info("No hay datos disponibles en SI PROYECCION.")
      else:
        mes_col = df.columns[0]
        mes_actual = (
            mes_col
            if str(mes_col).lower() not in ["unnamed: 0", "canal", "index"]
            else "Mes Actual"
        )

        df_proy = df.copy()
        df_proy[mes_col] = df_proy[mes_col].astype(str).str.strip()

        cols_moneda = ["Facturado x canal", "Proyección x canal", "Meta"]
        cols_pct = ["%", "Facturado actual"]

        for c in cols_moneda + cols_pct:
          if c in df_proy.columns:
            df_proy[c] = df_proy[c].apply(limpiar_numero)

        canales_principales = [
            "Consumo", "Consumo SB", "Consumo PU", "Farma", "Terceros"
        ]

        df_resumen = df_proy[df_proy[mes_col].isin(canales_principales)].copy()
        df_resumen = df_resumen.drop_duplicates(subset=[mes_col], keep="first")

        meta_total = (
            df_resumen["Meta"].sum() if "Meta" in df_resumen.columns else 0
        )
        proyeccion_total = (
            df_resumen["Proyección x canal"].sum()
            if "Proyección x canal" in df_resumen.columns
            else 0
        )
        facturado_total = (
            df_resumen["Facturado x canal"].sum()
            if "Facturado x canal" in df_resumen.columns
            else 0
        )

        cumplimiento_proy = (
            (proyeccion_total / meta_total * 100) if meta_total > 0 else 0
        )
        cumplimiento_actual = (
            (facturado_total / meta_total * 100) if meta_total > 0 else 0
        )
        diferencia_proy = proyeccion_total - meta_total

        resumen_data["si_proy"] = {
            "mes_actual": str(mes_actual),
            "meta_total": float(meta_total),
            "facturado_total": float(facturado_total),
            "proyeccion_total": float(proyeccion_total),
            "cumplimiento_actual": float(cumplimiento_actual),
            "cumplimiento_proy": float(cumplimiento_proy),
            "diferencia_proy": float(diferencia_proy),
        }

        st.markdown("#### 🎯 Resumen de Cumplimiento Meta")
        k1, k2, k3, k4, k5 = st.columns(5)

        k1.metric("🗓️ Mes en Curso", str(mes_actual).upper())
        k2.metric("🎯 Meta Total", formato_moneda(meta_total))
        k3.metric(
            "💰 Facturado Actual",
            formato_moneda(facturado_total),
            delta=f"{cumplimiento_actual:.1f}% Meta",
        )
        k4.metric("🚀 Cierre Proyectado", formato_moneda(proyeccion_total))
        k5.metric(
            "📈 Cumplimiento Proyectado",
            f"{cumplimiento_proy:.0f}%",
            delta=formato_moneda(diferencia_proy),
        )

        pct_barra = min(max(float(cumplimiento_proy) / 100.0, 0.0), 1.0)
        st.progress(
            pct_barra,
            text=(
                f"Avance de Proyección sobre la Meta: {cumplimiento_proy:.1f}%"
                f" (Resultado: {formato_moneda(diferencia_proy)})"
            ),
        )

        st.divider()

        col_t, col_g = st.columns([1.1, 1], gap="medium")

        with col_t:
          st.markdown("#### 📈 Detalle por Canal de Ventas")
          df_mostrar = df_resumen.copy()

          for c in cols_pct:
            if c in df_mostrar.columns:
              df_mostrar[c + "_pct"] = df_mostrar[c].apply(
                  lambda x: x * 100.0 if 0 <= x <= 3.0 else x
              )

          config_columnas = {mes_col: st.column_config.TextColumn("Canal / Concepto")}

          for c in cols_moneda:
            if c in df_mostrar.columns:
              config_columnas[c] = st.column_config.NumberColumn(
                  c, format="$%,.0f"
              )

          if "%" in df_mostrar.columns:
            config_columnas["%_pct"] = st.column_config.ProgressColumn(
                "Proyección vs Meta",
                format="%.0f%%",
                min_value=0,
                max_value=150,
            )
          if "Facturado actual" in df_mostrar.columns:
            config_columnas["Facturado actual_pct"] = (
                st.column_config.ProgressColumn(
                    "Facturado Actual",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100,
                )
            )

          cols_disp = [mes_col] + [
              c for c in cols_moneda if c in df_mostrar.columns
          ]
          if "%_pct" in df_mostrar.columns:
            cols_disp.append("%_pct")
          if "Facturado actual_pct" in df_mostrar.columns:
            cols_disp.append("Facturado actual_pct")

          st.dataframe(
              df_mostrar[cols_disp],
              column_config=config_columnas,
              hide_index=True,
              use_container_width=True,
          )

        with col_g:
          st.markdown("#### 📊 Comparativo Facturado vs Proyección vs Meta")
          fig_bar = go.Figure()
          fig_bar.add_trace(
              go.Bar(
                  y=df_resumen[mes_col],
                  x=df_resumen["Facturado x canal"],
                  name="Facturado Actual",
                  orientation="h",
                  marker_color="#0070f3",
              )
          )
          fig_bar.add_trace(
              go.Bar(
                  y=df_resumen[mes_col],
                  x=df_resumen["Proyección x canal"],
                  name="Proyección",
                  orientation="h",
                  marker_color="#f59e0b",
              )
          )
          fig_bar.add_trace(
              go.Bar(
                  y=df_resumen[mes_col],
                  x=df_resumen["Meta"],
                  name="Meta",
                  orientation="h",
                  marker_color="#10b981",
              )
          )
          fig_bar.update_layout(
              barmode="group",
              height=280,
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#ffffff"),
              margin=dict(t=10, b=10, l=10, r=10),
              xaxis=dict(gridcolor="#21262d"),
              yaxis=dict(
                  gridcolor="#21262d",
                  categoryorder="array",
                  categoryarray=list(df_resumen[mes_col])[::-1],
              ),
              legend=dict(orientation="h", y=1.15),
          )
          st.plotly_chart(
              fig_bar, use_container_width=True, key=f"bar_proy_{i}"
          )

        st.markdown("#### 💡 Insights de la Proyección")
        st.markdown("""
                * **Consumo y Farma**: Representan los motores principales del negocio, alcanzando un **55%** y **57%** de avance sobre sus metas y proyectando cerrar al **91%** ($2.100M y $2.013M respectivamente).
                * **Terceros**: Presenta un desempeño rezagado con un **28%** facturado y una proyección total del **35%** respecto a su meta ($14.4M proyectados de $41.0M).
                """)

        st.divider()
        st.markdown("#### 📦 Detalle OC Vigente y Proyección Compra")
        
        vista_oc = st.radio(
            "Seleccionar Vista:",
            options=["Ambos", "OC vigente", "Proyección Compra"],
            horizontal=True,
            key=f"radio_vista_oc_{i}"
        )

        def _norm_txt(s):
          s = str(s).strip().lower()
          for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
            s = s.replace(a, b)
          return s

        def _parse_pct(val):
          v = limpiar_numero(val)
          if 0 <= v <= 1.0:
            v = v * 100.0
          return round(v)

        datos_oc_proyeccion = []

        try:
          df_grid_oc = pd.read_excel(
              ruta_final, sheet_name=nombre_hoja, header=None, dtype=str
          )

          header_r, header_c = None, None
          for r in range(len(df_grid_oc)):
            for c in range(len(df_grid_oc.columns) - 1):
              if _norm_txt(df_grid_oc.iloc[r, c]) == "canal" and "monto" in _norm_txt(
                  df_grid_oc.iloc[r, c + 1]
              ):
                header_r, header_c = r, c
                break
            if header_r is not None:
              break

          if header_r is not None:
            col_concepto = header_c - 1
            col_canal = header_c
            col_monto = header_c + 1
            col_fr = header_c + 2
            col_proy = header_c + 3
            col_extra = header_c + 4

            concepto_actual = None
            r = header_r + 1
            while r < len(df_grid_oc):
              canal_val = df_grid_oc.iloc[r, col_canal] if col_canal < len(df_grid_oc.columns) else None
              canal_txt = str(canal_val).strip() if pd.notna(canal_val) else ""

              if col_concepto >= 0:
                concepto_val = df_grid_oc.iloc[r, col_concepto]
                if pd.notna(concepto_val) and str(concepto_val).strip() != "":
                  txt_concepto = _norm_txt(concepto_val)
                  if "vigente" in txt_concepto:
                    concepto_actual = "OC vigente"
                  elif "proyec" in txt_concepto:
                    concepto_actual = "Proyección Compra"
                  else:
                    concepto_actual = str(concepto_val).strip()

              if canal_txt == "" or canal_txt.lower() == "nan":
                break

              canal_norm = _norm_txt(canal_txt)
              if any(
                  kw in canal_norm
                  for kw in ["cierre", "meta", "resultado", "cumplimiento"]
              ):
                break

              datos_oc_proyeccion.append({
                  "Concepto": concepto_actual or "",
                  "Canal": canal_txt,
                  "Monto OC": limpiar_numero(df_grid_oc.iloc[r, col_monto]) if col_monto < len(df_grid_oc.columns) else 0.0,
                  "FR": _parse_pct(df_grid_oc.iloc[r, col_fr]) if col_fr < len(df_grid_oc.columns) else 0,
                  "Proyección salida": limpiar_numero(df_grid_oc.iloc[r, col_proy]) if col_proy < len(df_grid_oc.columns) else 0.0,
                  "OC extra": limpiar_numero(df_grid_oc.iloc[r, col_extra]) if col_extra < len(df_grid_oc.columns) else 0.0,
              })
              r += 1
        except Exception as e:
          st.warning(f"No se pudo leer la tabla OC del Excel ({e}).")

        df_oc_tab = pd.DataFrame(
            datos_oc_proyeccion,
            columns=["Concepto", "Canal", "Monto OC", "FR", "Proyección salida", "OC extra"],
        )
        
        if vista_oc != "Ambos":
            df_oc_tab = df_oc_tab[df_oc_tab["Concepto"] == vista_oc]

        tot_monto_oc = df_oc_tab["Monto OC"].sum()
        tot_proy_salida = df_oc_tab["Proyección salida"].sum()

        col_k1, col_k2 = st.columns(2)
        col_k1.metric("📦 Monto Total OC", formato_moneda(tot_monto_oc))
        col_k2.metric(
            "🚚 Total Proyección Salida", formato_moneda(tot_proy_salida)
        )

        st.markdown("---")

        col_oc_tabla, col_oc_grafico = st.columns([1.1, 1], gap="medium")

        with col_oc_tabla:
          st.markdown("##### 📋 Tabla Detalle")
          st.dataframe(
              df_oc_tab,
              column_config={
                  "Concepto": st.column_config.TextColumn("Categoría"),
                  "Canal": st.column_config.TextColumn("Canal"),
                  "Monto OC": st.column_config.NumberColumn(
                      "Monto OC", format="$%,.0f"
                  ),
                  "FR": st.column_config.NumberColumn("FR", format="%d%%"),
                  "Proyección salida": st.column_config.NumberColumn(
                      "Proyección salida", format="$%,.0f"
                  ),
                  "OC extra": st.column_config.NumberColumn(
                      "OC extra", format="$%,.0f"
                  ),
              },
              hide_index=True,
              use_container_width=True,
          )

        with col_oc_grafico:
          st.markdown("##### 📊 Comparativo Monto OC vs Proyección Salida")

          def _agregar_barras_oc(fig, df_sub, row=None, col=None, mostrar_leyenda=True):
              kwargs_pos = {"row": row, "col": col} if row is not None else {}
              fig.add_trace(
                  go.Bar(
                      x=df_sub["Canal"],
                      y=df_sub["Monto OC"],
                      name="Monto OC",
                      marker_color="#0070f3",
                      text=[
                          f"${round(v/1e6):,.0f}M" if v > 0 else "$0"
                          for v in df_sub["Monto OC"]
                      ],
                      textposition="inside",
                      insidetextanchor="end",
                      textangle=0,
                      textfont=dict(size=12, color="#ffffff"),
                      cliponaxis=False,
                      showlegend=mostrar_leyenda,
                      legendgroup="Monto OC",
                  ),
                  **kwargs_pos,
              )
              fig.add_trace(
                  go.Bar(
                      x=df_sub["Canal"],
                      y=df_sub["Proyección salida"],
                      name="Proyección Salida",
                      marker_color="#10b981",
                      text=[
                          f"${round(v/1e6):,.0f}M" if v > 0 else "$0"
                          for v in df_sub["Proyección salida"]
                      ],
                      textposition="inside",
                      insidetextanchor="end",
                      textangle=0,
                      textfont=dict(size=12, color="#ffffff"),
                      cliponaxis=False,
                      showlegend=mostrar_leyenda,
                      legendgroup="Proyección Salida",
                  ),
                  **kwargs_pos,
              )

          if vista_oc == "Ambos":
              df_vig = df_oc_tab[df_oc_tab["Concepto"] == "OC vigente"]
              df_proy = df_oc_tab[df_oc_tab["Concepto"] == "Proyección Compra"]

              fig_oc = make_subplots(
                  rows=1, cols=2,
                  subplot_titles=("OC vigente", "Proyección Compra"),
                  horizontal_spacing=0.1,
              )

              _agregar_barras_oc(fig_oc, df_vig, row=1, col=1, mostrar_leyenda=True)
              _agregar_barras_oc(fig_oc, df_proy, row=1, col=2, mostrar_leyenda=False)

              max_vig = df_vig["Monto OC"].max() if not df_vig.empty else 100
              max_proy = df_proy["Monto OC"].max() if not df_proy.empty else 100

              fig_oc.update_yaxes(
                  gridcolor="#21262d", showticklabels=False,
                  range=[0, max_vig * 1.15], row=1, col=1,
              )
              fig_oc.update_yaxes(
                  gridcolor="#21262d", showticklabels=False,
                  range=[0, max_proy * 1.15], row=1, col=2,
              )
              fig_oc.update_xaxes(gridcolor="#21262d", tickangle=0, tickfont=dict(size=12), row=1, col=1)
              fig_oc.update_xaxes(gridcolor="#21262d", tickangle=0, tickfont=dict(size=12), row=1, col=2)

              fig_oc.update_layout(
                  barmode="group",
                  bargap=0.35,
                  bargroupgap=0.15,
                  height=420,
                  paper_bgcolor="rgba(0,0,0,0)",
                  plot_bgcolor="rgba(0,0,0,0)",
                  font=dict(color="#ffffff"),
                  margin=dict(t=50, b=10, l=10, r=10),
                  legend=dict(orientation="h", y=1.2, x=0.2, font=dict(size=12)),
                  uniformtext_minsize=10,
                  uniformtext_mode="show",
              )
              fig_oc.update_annotations(font=dict(color="#ffffff", size=13))
          else:
              df_oc_plot = df_oc_tab.copy()

              fig_oc = go.Figure()
              _agregar_barras_oc(fig_oc, df_oc_plot, mostrar_leyenda=True)

              fig_oc.update_layout(
                  barmode="group",
                  bargap=0.35,
                  bargroupgap=0.15,
                  height=420,
                  paper_bgcolor="rgba(0,0,0,0)",
                  plot_bgcolor="rgba(0,0,0,0)",
                  font=dict(color="#ffffff"),
                  margin=dict(t=40, b=10, l=10, r=10),
                  xaxis=dict(gridcolor="#21262d", tickangle=0, tickfont=dict(size=12)),
                  yaxis=dict(
                      gridcolor="#21262d",
                      showticklabels=False,
                      range=[0, df_oc_plot["Monto OC"].max() * 1.15] if not df_oc_plot.empty else [0, 100],
                  ),
                  legend=dict(orientation="h", y=1.15, x=0.2, font=dict(size=12)),
                  uniformtext_minsize=10,
                  uniformtext_mode="show",
              )

          st.plotly_chart(
              fig_oc, use_container_width=True, key=f"bar_oc_comp_{i}"
          )

        # Matriz Proyecciones Metas por Mes
        st.divider()
        st.markdown("#### 🗓️ Proyecciones Metas por Mes (2026)")

        try:
          df_grid = pd.read_excel(
              ruta_final, sheet_name=nombre_hoja, header=None, dtype=str
          )

          target_r, target_c = None, None

          for r in range(len(df_grid)):
            for c in range(len(df_grid.columns)):
              val = str(df_grid.iloc[r, c]).strip().upper()
              if val in ["DIV.", "DIV"]:
                sub_vals = [
                    str(df_grid.iloc[r_sub, c]).strip().upper()
                    for r_sub in range(r + 1, min(r + 8, len(df_grid)))
                ]
                if any("FARMA" in v for v in sub_vals) and any(
                    "CONSUMO" in v for v in sub_vals
                ):
                  target_r, target_c = r, c

          if target_r is not None and target_c is not None:
            c_start = target_c
            c_end = min(c_start + 13, len(df_grid.columns))

            r_end = min(target_r + 7, len(df_grid))
            df_block = df_grid.iloc[target_r:r_end, c_start:c_end].copy()

            raw_headers = df_block.iloc[0].values
            headers = []

            meses_map = {
                "ene": "Enero",
                "feb": "Febrero",
                "mar": "Marzo",
                "abr": "Abril",
                "may": "Mayo",
                "jun": "Junio",
                "jul": "Julio",
                "ago": "Agosto",
                "sept": "Septiembre",
                "sep": "Septiembre",
                "oct": "Octubre",
                "nov": "Noviembre",
                "dic": "Diciembre",
            }

            for idx_h, h in enumerate(raw_headers):
              if idx_h == 0:
                headers.append("División")
              else:
                cleaned_h = limpiar_nombre_mes(h)
                mes_prefix = (
                    cleaned_h.split("-")[0].lower()
                    if "-" in cleaned_h
                    else str(cleaned_h).lower()
                )
                mes_nombre = meses_map.get(
                    mes_prefix, cleaned_h.capitalize()
                )
                headers.append(mes_nombre)

            df_rows = df_block.iloc[1:].copy()
            df_rows.columns = headers

            filas_procesadas = []
            for _, row_data in df_rows.iterrows():
              div_val = str(row_data["División"]).strip()

              tiene_datos = any(
                  pd.notna(v) and str(v).strip() not in ["", "nan"]
                  for v in row_data[1:]
              )

              if not tiene_datos:
                continue

              div_upper = div_val.upper()
              if (
                  div_val == ""
                  or div_val.lower() == "nan"
                  or "TOTAL" in div_upper
              ):
                div_val = "Total General"
              elif "FARMA" in div_upper:
                div_val = "FARMA"
              elif "CONSUMO" in div_upper:
                div_val = "CONSUMO"
              elif (
                  "CAN" in div_upper
                  or "TERCEROS" in div_upper
                  or "3" in div_upper
              ):
                div_val = "3 Canales"

              row_dict = {"División": div_val}
              for col_m in headers[1:]:
                row_dict[col_m] = limpiar_numero(row_data[col_m])

              filas_procesadas.append(row_dict)

            df_res_meses = pd.DataFrame(filas_procesadas)

            if not df_res_meses.empty:
              df_res_meses = df_res_meses.drop_duplicates(
                  subset=["División"], keep="first"
              )

              cols_num_meses = [
                  c for c in df_res_meses.columns if c != "División"
              ]
              cfg_meses = {"División": st.column_config.TextColumn("División")}
              for cm in cols_num_meses:
                cfg_meses[cm] = st.column_config.NumberColumn(
                    cm, format="$%,.0f"
                )

              nombres_meses_lista = [
                  "Enero",
                  "Febrero",
                  "Marzo",
                  "Abril",
                  "Mayo",
                  "Junio",
                  "Julio",
                  "Agosto",
                  "Septiembre",
                  "Octubre",
                  "Noviembre",
                  "Diciembre",
              ]
              mes_actual_nombre = nombres_meses_lista[datetime.now().month - 1]

              def resaltar_mes_actual(df_to_style):
                df_styles = pd.DataFrame(
                    "", index=df_to_style.index, columns=df_to_style.columns
                )
                if mes_actual_nombre in df_to_style.columns:
                  df_styles[mes_actual_nombre] = (
                      "background-color: rgba(0, 112, 243, 0.35); color:"
                      " #ffffff; font-weight: bold;"
                  )
                return df_styles

              st.dataframe(
                  df_res_meses.style.apply(resaltar_mes_actual, axis=None),
                  column_config=cfg_meses,
                  hide_index=True,
                  use_container_width=True,
              )
            else:
              st.info("No se pudieron procesar los registros de la tabla.")
          else:
            st.info("No se encontró la matriz de proyecciones mensuales.")
        except Exception as e_proy:
          st.warning(f"Error al procesar la tabla de proyecciones: {e_proy}")

    # =================================================================
    # DASHBOARD DE STOCK / CADUCIDAD
    # =================================================================
    elif is_stock:
      st.markdown("### 📦 Dashboard de Fecha de Caducidad e Inventarios")

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
      col_desc_stock = next(
          (c for c in df.columns if "descripcion" in c.lower()), None
      )
      if not col_desc_stock and len(df.columns) > 3:
        col_desc_stock = df.columns[3]
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

      col_sku_sb = next(
          (c for c in df.columns if c.strip().lower() == "codigo_sb"), None
      )
      col_sku_pu = next(
          (c for c in df.columns if c.strip().lower() == "codigo_pu"), None
      )
      if not col_sku_sb and len(df.columns) > 1:
        col_sku_sb = df.columns[1]
      if not col_sku_pu and len(df.columns) > 2:
        col_sku_pu = df.columns[2]

      if col_sku_sb and col_sku_sb in df.columns:
        df[col_sku_sb] = df[col_sku_sb].apply(fmt_code)
      if col_sku_pu and col_sku_pu in df.columns:
        df[col_sku_pu] = df[col_sku_pu].apply(fmt_code)

      if col_cant:
        df[col_cant] = df[col_cant].apply(limpiar_numero)

      hoy = pd.Timestamp.today()
      limite_6m = hoy + pd.DateOffset(months=6)
      limite_13m = hoy + pd.DateOffset(months=13)

      if col_fecha:
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")

        def calcular_alerta(fecha):
          if pd.isna(fecha):
            return "Sin Fecha"
          if fecha < hoy:
            return "Vencido"
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

      # CONTENEDOR DE FILTROS BÚSQUEDA STOCK
      with st.container(border=True):
        st.markdown("<div style='font-size:14px; font-weight:700; margin-bottom:8px;'>🔍 Filtros de Búsqueda de Inventario</div>", unsafe_allow_html=True)
        key_codigo = f"sel_codigo_stock_{i}"
        key_sku_sb = f"sel_sku_sb_stock_{i}"
        key_sku_pu = f"sel_sku_pu_stock_{i}"

        def _limpiar_otros_filtros(keys_a_limpiar):
          for k in keys_a_limpiar:
            if k in st.session_state:
              st.session_state[k] = "Todos"

        filtro_codigo_col, filtro_sku_sb_col, filtro_sku_pu_col = st.columns(3)

        with filtro_codigo_col:
          if col_cod:
            lista_codigos = sorted(
                [str(x) for x in df[col_cod].dropna().unique() if str(x).strip() != ""]
            )
            codigo_sel = st.selectbox(
                "Código:",
                ["Todos"] + lista_codigos,
                key=key_codigo,
                on_change=_limpiar_otros_filtros,
                args=([key_sku_sb, key_sku_pu],),
            )
          else:
            codigo_sel = "Todos"

        with filtro_sku_sb_col:
          if col_sku_sb and col_sku_sb in df.columns:
            lista_sku_sb = sorted(
                [str(x) for x in df[col_sku_sb].dropna().unique() if str(x).strip() != "" and str(x) != "S/N"]
            )
            sku_sb_sel = st.selectbox(
                "SKU SB:",
                ["Todos"] + lista_sku_sb,
                key=key_sku_sb,
                on_change=_limpiar_otros_filtros,
                args=([key_codigo, key_sku_pu],),
            )
          else:
            sku_sb_sel = "Todos"

        with filtro_sku_pu_col:
          if col_sku_pu and col_sku_pu in df.columns:
            lista_sku_pu = sorted(
                [str(x) for x in df[col_sku_pu].dropna().unique() if str(x).strip() != "" and str(x) != "S/N"]
            )
            sku_pu_sel = st.selectbox(
                "SKU PU:",
                ["Todos"] + lista_sku_pu,
                key=key_sku_pu,
                on_change=_limpiar_otros_filtros,
                args=([key_codigo, key_sku_sb],),
            )
          else:
            sku_pu_sel = "Todos"

      df_dash = df.copy()
      if codigo_sel != "Todos" and col_cod:
        df_dash = df_dash[df_dash[col_cod].astype(str) == codigo_sel].copy()

      if sku_sb_sel != "Todos" and col_sku_sb and col_sku_sb in df_dash.columns:
        df_dash = df_dash[df_dash[col_sku_sb].astype(str) == sku_sb_sel].copy()

      if sku_pu_sel != "Todos" and col_sku_pu and col_sku_pu in df_dash.columns:
        df_dash = df_dash[df_dash[col_sku_pu].astype(str) == sku_pu_sel].copy()

      if col_cant:
        total_unidades = df_dash[col_cant].sum()
        total_vencido = df_dash[
            df_dash["Alerta_Caducidad"] == "Vencido"
        ][col_cant].sum()
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
        total_vencido = len(df_dash[df_dash["Alerta_Caducidad"] == "Vencido"])
        total_menos_6m = len(
            df_dash[df_dash["Alerta_Caducidad"] == "Menos de 6 meses"]
        )
        total_pronto = len(
            df_dash[df_dash["Alerta_Caducidad"] == "Pronto vence (6-13m)"]
        )
        total_vigentes = len(
            df_dash[df_dash["Alerta_Caducidad"] == "Vigente (> 13m)"]
        )

      resumen_data["stock_caducidad"] = {
          "total_unidades": float(total_unidades),
          "vencido": float(total_vencido),
          "menos_6m": float(total_menos_6m),
          "pronto_6_13m": float(total_pronto),
          "vigente_13m": float(total_vigentes),
      }

      total_critico = total_vencido + total_menos_6m
      pct_critico = (
          (total_critico / total_unidades * 100) if total_unidades > 0 else 0.0
      )

      color_pct_critico = (
          "#ef4444" if pct_critico >= 15
          else "#f59e0b" if pct_critico >= 5
          else "#10b981"
      )
      
      st.markdown(
          f"""
          <div class="kpi-card" style="margin-top:15px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                  <div class="kpi-title">⚠️ Porcentaje de Stock Crítico (Vencido + Vence en &lt; 6 Meses)</div>
                  <div style="font-size:12px; color:#8b949e;">Requiere acción de liquidación o retiro preventivo</div>
              </div>
              <div style="color:{color_pct_critico}; font-size:28px; font-weight:800;">{pct_critico:.2f}%</div>
          </div>
          """,
          unsafe_allow_html=True,
      )

      label_map_alerta = {
          "Todos": "Todos",
          "Vencido": "Vencido",
          "Vence en < 6 meses": "Menos de 6 meses",
          "Pronto vence (6-13m)": "Pronto vence (6-13m)",
          "Vigente (> 13m)": "Vigente (> 13m)",
      }
      key_alerta = f"radio_alerta_stock_{i}"
      etiqueta_sel = st.radio(
          "🔍 Filtrar por categoría de caducidad:",
          list(label_map_alerta.keys()),
          horizontal=True,
          key=key_alerta,
      )
      filtro_actual = label_map_alerta[etiqueta_sel]

      if filtro_actual != "Todos":
        df_dash_alerta = df_dash[df_dash["Alerta_Caducidad"] == filtro_actual].copy()
      else:
        df_dash_alerta = df_dash.copy()

      col_dash1, col_dash2 = st.columns([1, 2])

      with col_dash1:
        st.markdown("<div class='kpi-title' style='margin-bottom:10px;'>📊 Resumen por Estados</div>", unsafe_allow_html=True)
        
        cards_data = [
            ("Unidades Registradas", formato_unidades(total_unidades), "#0070f3"),
            ("Vencido", formato_unidades(total_vencido), "#7f1d1d"),
            ("Vence en < 6 meses", formato_unidades(total_menos_6m), "#ef4444"),
            ("Pronto vence (6-13m)", formato_unidades(total_pronto), "#f59e0b"),
            ("Vigentes (> 13m)", formato_unidades(total_vigentes), "#10b981")
        ]
        
        for titulo_card, valor_card, color_card in cards_data:
            st.markdown(
                f"""
                <div class="kpi-card" style="margin-bottom:8px; border-left: 4px solid {color_card};">
                    <div class="kpi-title">{titulo_card}</div>
                    <div class="kpi-value" style="font-size:20px;">{valor_card}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

      with col_dash2:
        st.markdown("<div class='kpi-title' style='margin-bottom:10px;'>🍩 Distribución Proporcional de Caducidad</div>", unsafe_allow_html=True)
        labels = ["Vencido", "< 6 meses", "6 a 13 meses", "Vigente (> 13m)"]
        values = [total_vencido, total_menos_6m, total_pronto, total_vigentes]
        colors = ["#7f1d1d", "#ef4444", "#f59e0b", "#10b981"]

        total_donut = sum(values)
        if total_donut > 0:
          textos_pct = [
              f"{lbl}<br>{(v / total_donut * 100):.2f}%"
              for lbl, v in zip(labels, values)
          ]
          fig_pie = go.Figure(
              data=[
                  go.Pie(
                      labels=labels,
                      values=values,
                      hole=0.6,
                      marker=dict(colors=colors, line=dict(color="#08090a", width=2)),
                      text=textos_pct,
                      texttemplate="%{text}",
                      textposition="outside",
                      textfont=dict(size=12, color="#ffffff"),
                  )
              ]
          )
          fig_pie.update_layout(
              height=320,
              margin=dict(t=20, b=40, l=40, r=40),
              paper_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#ffffff"),
              showlegend=False
          )
          st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_stock_{i}")
        else:
          st.info("Sin registros para mostrar.")

      st.divider()

      if col_estado_lote and col_estado_lote in df_dash_alerta.columns:
        st.markdown("##### 🏷️ Cantidad de Unidades por Estado de Lote")
        df_est_grp = (
            df_dash_alerta.groupby(col_estado_lote, dropna=False)[col_cant]
            .sum()
            .reset_index()
            if col_cant
            else df_dash_alerta[col_estado_lote].value_counts().reset_index()
        )

        if not df_est_grp.empty:
          c_e, c_q = df_est_grp.columns[0], df_est_grp.columns[1]
          num_items = len(df_est_grp)
          cols_est = st.columns(min(num_items, 6))
          for idx_e, row_e in df_est_grp.iterrows():
            nombre_est = (
                str(row_e[c_e]) if pd.notna(row_e[c_e]) else "Sin Estado"
            )
            cant_est = row_e[c_q]

            with cols_est[idx_e % min(num_items, 6)]:
              st.markdown(
                  f"""
                  <div class="kpi-card" style="text-align:center;">
                      <div class="kpi-title">{nombre_est}</div>
                      <div class="kpi-value" style="font-size:18px; color:#0070f3;">{formato_unidades(cant_est)}</div>
                  </div>
                  """,
                  unsafe_allow_html=True,
              )

        st.divider()

      st.subheader("📋 Detalle de Stock y Lotes")

      cols_mostrar = []
      nombres_amigables = {}
      if col_cod:
        cols_mostrar.append(col_cod)
        nombres_amigables[col_cod] = "Código Artículo"
      if col_sku_sb and col_sku_sb in df_dash_alerta.columns:
        cols_mostrar.append(col_sku_sb)
        nombres_amigables[col_sku_sb] = "SKU SB"
      if col_sku_pu and col_sku_pu in df_dash_alerta.columns:
        cols_mostrar.append(col_sku_pu)
        nombres_amigables[col_sku_pu] = "SKU PU"
      if col_estado_sub:
        cols_mostrar.append(col_estado_sub)
        nombres_amigables[col_estado_sub] = "Estado Sub-Inv"
      if col_estado_lote:
        cols_mostrar.append(col_estado_lote)
        nombres_amigables[col_estado_lote] = "Estado Lote"
      if col_lote:
        cols_mostrar.append(col_lote)
        nombres_amigables[col_lote] = "Lote Proveedor"
      if col_loc:
        cols_mostrar.append(col_loc)
        nombres_amigables[col_loc] = "Localizador"
      if col_cant:
        cols_mostrar.append(col_cant)
        nombres_amigables[col_cant] = "Cantidad"
      if col_fecha:
        cols_mostrar.append(col_fecha)
        nombres_amigables[col_fecha] = "Fecha Expiración"
      cols_mostrar.append("Alerta_Caducidad")
      nombres_amigables["Alerta_Caducidad"] = "Rango Caducidad"

      df_vista_stock = df_dash_alerta[cols_mostrar].copy()
      df_vista_stock = df_vista_stock.rename(columns=nombres_amigables)

      if "Fecha Expiración" in df_vista_stock.columns:
        df_vista_stock["Fecha Expiración"] = pd.to_datetime(
            df_vista_stock["Fecha Expiración"], errors="coerce"
        ).dt.strftime("%d-%m-%Y")

      st.dataframe(df_vista_stock, hide_index=True, use_container_width=True)

    # =================================================================
    # PESTAÑAS SB Y PU ORIGINALES (CON ESTILO MEJORADO)
    # =================================================================
    elif is_sb or is_pu:
      col_semana = next((c for c in df.columns if c.strip().lower() in ["semana", "sem", "wk", "week"]), None)
      col_sku = next((c for c in df.columns if any(k in c.lower() for k in ["id_prod", "sku", "cod_prod"])), None)
      col_oc = next((c for c in df.columns if "oc" in c.lower() or "orden" in c.lower()), None)
      col_desc = next((c for c in df.columns if "desc" in c.lower() or "nombre" in c.lower()), None)
      col_div = next((c for c in df.columns if "divis" in c.lower() or "categ" in c.lower()), None)
      col_u_compra = next((c for c in df.columns if any(k in c.lower() for k in ["comp", "pedi", "solic", "cant", "unid"])), None)
      col_u_recib = next((c for c in df.columns if any(k in c.lower() for k in ["recib", "entre", "despa"])), None)

      st.markdown(f"### 📋 Operaciones Canal {nombre_clean}")
      st.dataframe(df, hide_index=True, use_container_width=True)

    # =================================================================
    # FILL RATE
    # =================================================================
    elif is_fill_rate:
      st.markdown("### 📊 Reporte de Fill Rate por Semanas")
      try:
        raw_fr = cargar_hoja_raw(ruta_final, nombre_hoja)
        bloques_fr = parse_bloques_fill_rate(raw_fr)
        if bloques_fr:
          for blk in bloques_fr:
            with st.expander(f"📍 {blk['titulo']} (Semana {blk['semana']})", expanded=True):
              k1, k2, k3 = st.columns(3)
              k1.metric("Cantidad Pedida", formato_unidades(blk['kpi_total']['cantidad']))
              k2.metric("Monto Total ($)", formato_moneda(blk['kpi_total']['monto']))
              k3.metric("Fill Rate Global", f"{(blk['kpi_total']['fr'] or 0)*100:.1f}%")
              
              st.dataframe(blk['tabla'], hide_index=True, use_container_width=True)
        else:
          st.info("No se detectaron bloques de datos con formato 'TOP' en la hoja Fill Rate.")
      except Exception as e_fr:
        st.error(f"Error procesando Fill Rate: {e_fr}")


# =================================================================
# CONSTRUCCIÓN DE LA PESTAÑA PRINCIPAL: 📊 RESUMEN (TORRE DE CONTROL)
# =================================================================
with tabs[0]:
  st.markdown("### 🚀 Torre de Control Operativa")
  st.caption("Visión consolidada de proyecciones, salud de inventario y ejecución de ventas.")

  r_col1, r_col2 = st.columns([1.2, 1], gap="large")

  with r_col1:
    st.markdown("#### 🎯 Avance de Metas y Proyección SI")
    if "si_proy" in resumen_data:
      d_proy = resumen_data["si_proy"]
      st.markdown(
          f"""
          <div class="kpi-card" style="margin-bottom:15px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                  <div>
                      <div class="kpi-title">Mes Evaluado: {d_proy['mes_actual'].upper()}</div>
                      <div class="kpi-value">{formato_moneda(d_proy['facturado_total'])} <span style="font-size:14px; font-weight:normal; color:#8b949e;">Facturado</span></div>
                  </div>
                  <div style="text-align:right;">
                      <div class="kpi-title">Meta Mes</div>
                      <div style="font-size:18px; font-weight:700; color:#f0f6fc;">{formato_moneda(d_proy['meta_total'])}</div>
                  </div>
              </div>
          </div>
          """,
          unsafe_allow_html=True
      )
      
      gauge_fig = crear_reloj_gauge("Cierre Proyectado vs Meta", d_proy['cumplimiento_proy'], "#0070f3")
      st.plotly_chart(gauge_fig, use_container_width=True)
    else:
      st.info("Datos de proyección SI no disponibles.")

  with r_col2:
    st.markdown("#### ⚠️ Estado Crítico de Inventario (Caducidad)")
    if "stock_caducidad" in resumen_data:
      d_stock = resumen_data["stock_caducidad"]
      tot_stock = d_stock["total_unidades"]
      venc = d_stock["vencido"]
      m6 = d_stock["menos_6m"]
      
      pct_venc = (venc / tot_stock * 100) if tot_stock > 0 else 0
      pct_m6 = (m6 / tot_stock * 100) if tot_stock > 0 else 0

      c_sk1, c_sk2 = st.columns(2)
      c_sk1.metric("Stock Total Registrado", formato_unidades(tot_stock))
      c_sk2.metric("Stock Vencido", formato_unidades(venc), delta=f"{pct_venc:.1f}% del total", delta_color="inverse")

      st.markdown(
          f"""
          <div class="kpi-card" style="margin-top:10px; border-left:4px solid #ef4444;">
              <div class="kpi-title">Unidades Vencen en &lt; 6 Meses</div>
              <div class="kpi-value" style="color:#ef4444;">{formato_unidades(m6)} <span style="font-size:13px; font-weight:normal; color:#8b949e;">({pct_m6:.1f}%)</span></div>
          </div>
          """,
          unsafe_allow_html=True
      )
    else:
      st.info("Datos de Stock no cargados en el Resumen.")

  st.divider()
  st.markdown("#### 🏢 Participación por División (Ventas SI)")
  if "venta_div" in resumen_data:
    df_div_res = pd.DataFrame(resumen_data["venta_div"]["filas"])
    if not df_div_res.empty:
      fig_div_res = px.bar(
          df_div_res,
          x="division",
          y="monto",
          text="monto",
          color_discrete_sequence=["#0070f3"],
          labels={"division": "División", "monto": "Monto ($)"}
      )
      fig_div_res.update_traces(texttemplate='%{y:$.2s}', textposition='outside')
      fig_div_res.update_layout(
          template="plotly_dark",
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          height=300,
          margin=dict(t=20, b=20, l=10, r=10)
      )
      st.plotly_chart(fig_div_res, use_container_width=True)

# =================================================================
# PESTAÑA ESCANEAR / HERRAMIENTAS ADICIONALES
# =================================================================
with tabs[-1]:
  st.markdown("### 📷 Módulo de Escaneo / Código de Barras")
  st.info("Función lista para integración con cámara móvil o lector USB.")
