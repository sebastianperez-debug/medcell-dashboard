import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import streamlit.components.v1 as components

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
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        margin-top: 8px !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label {
        background-color: #141414 !important;
        border: 1px solid #2b2b2b !important;
        padding: 10px 22px !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: all 0.25s ease-in-out !important;
        color: #cccccc !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-sizing: border-box !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label:hover {
        border-color: #0070f3 !important;
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        transform: translateY(-2px);
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label[data-checked="true"] {
        background-color: #0070f3 !important;
        border-color: #0070f3 !important;
        color: #ffffff !important;
        box-shadow: 0px 4px 14px rgba(0, 112, 243, 0.4);
    }

    /* En celular: exactamente 2 semanas por fila, ocupando mejor el ancho. */
    @media (max-width: 768px) {
        div[data-testid="stRadio"] {
            width: 100% !important;
            max-width: none !important;
            margin-top: 0 !important;
            margin-bottom: 8px !important;
        }
        div[data-testid="stRadio"] > div {
            width: 100% !important;
            max-width: none !important;
        }
        div[data-testid="stRadio"] [role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            column-gap: 10px !important;
            row-gap: 10px !important;
            width: 100% !important;
            max-width: none !important;
            margin-top: 0 !important;
        }
        div[data-testid="stRadio"] [role="radiogroup"] > label {
            width: 100% !important;
            min-width: 0 !important;
            height: 58px !important;
            padding: 10px 12px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            margin: 0 !important;
        }
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

    /* En celular: las grillas de indicadores (st.columns con st.metric,
       como "Resumen de Órdenes y Montos") se acomodan de a 2 por fila en
       vez de aplastarse todas en una sola línea horizontal ilegible.
       Se EXCLUYEN explícitamente las filas que contienen una tabla
       (st.dataframe) o un gráfico, para que esas sigan ocupando el ancho
       completo, apiladas una debajo de la otra (de lo contrario las
       columnas de la tabla quedan cortadas / ilegibles). */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stDataFrame"])):not(:has(div[data-testid="stDataFrameResizable"])):not(:has(div[data-testid="stPlotlyChart"])):not(:has(div[data-testid="stTable"])) {
            flex-wrap: wrap !important;
            row-gap: 16px !important;
            column-gap: 12px !important;
        }
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stDataFrame"])):not(:has(div[data-testid="stDataFrameResizable"])):not(:has(div[data-testid="stPlotlyChart"])):not(:has(div[data-testid="stTable"])) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stDataFrame"])):not(:has(div[data-testid="stDataFrameResizable"])):not(:has(div[data-testid="stPlotlyChart"])):not(:has(div[data-testid="stTable"])) > div[data-testid="stColumn"] {
            min-width: 46% !important;
            width: 46% !important;
            flex: 1 1 46% !important;
        }
        /* Filas con tabla/gráfico: apiladas a ancho completo (comportamiento
           estándar de Streamlit en pantallas angostas). */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stDataFrame"]),
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stDataFrameResizable"]),
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]),
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTable"]) {
            flex-wrap: wrap !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stDataFrame"]) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stDataFrameResizable"]) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTable"]) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stDataFrame"]) > div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stDataFrameResizable"]) > div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]) > div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTable"]) > div[data-testid="stColumn"] {
            min-width: 100% !important;
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        div[data-testid="stMetric"] {
            min-width: 0 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 19px !important;
            overflow-wrap: break-word !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 12px !important;
            white-space: normal !important;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- Funciones auxiliares de formato y conversión ---
def limpiar_numero(val):
  """Limpia cadenas numéricas de Excel preservando la escala real de enteros y decimales."""
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
  """Normaliza las cabeceras de fechas a formato corto tipo ene-26."""
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


def aplicar_criticidad(column):
  is_total = column.index == (len(column) - 1)
  styles = []
  for i, val in enumerate(column):
    # Acepta tanto números como strings ya formateados (ej. "18.16%"),
    # así la columna puede exportarse a CSV como texto sin romper el color.
    try:
      val_num = float(str(val).replace("%", "").replace(",", ".").strip())
    except (ValueError, TypeError):
      val_num = 0.0
    if is_total[i]:
      styles.append("font-weight: bold; background-color: #1a1a1a;")
    elif val_num >= 15.0:
      styles.append(
          "background-color: #8b0000; color: #ffffff; font-weight: bold;"
      )
    elif val_num >= 10.0:
      styles.append(
          "background-color: #b91c1c; color: #ffffff; font-weight: bold;"
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
  """Carga una hoja del Excel sin asumir fila de encabezado, preservando
  la posición original de cada celda (para hojas con múltiples tablas
  pegadas, como 'FILL RATE')."""
  return pd.read_excel(ruta, sheet_name=nombre_hoja, header=None, dtype=object)


def _fr_num(valor):
  """Convierte un valor de celda a float; si no es numérico o está vacío
  (None o NaN), retorna None."""
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
  """Detecta y extrae los distintos bloques/tablas pegados verticalmente
  en la hoja 'FILL RATE'. Cada bloque tiene: una fila 'Semana X Total ...',
  una fila 'Top N ...', una fila de encabezados (col A = 'TOP'), y luego
  las filas de detalle hasta la siguiente fila vacía o el próximo bloque."""
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

      # Las filas KPI ('Total' y 'Top N') siempre traen sus valores en las
      # columnas E, F, G y (opcionalmente) H, independiente de dónde
      # empiecen los encabezados de la tabla de detalle de ese bloque.
      def _valores_kpi(fila_kpi):
        e = _fr_num(fila_kpi.iloc[4]) if n_cols > 4 else None
        f = _fr_num(fila_kpi.iloc[5]) if n_cols > 5 else None
        g = _fr_num(fila_kpi.iloc[6]) if n_cols > 6 else None
        h = _fr_num(fila_kpi.iloc[7]) if n_cols > 7 else None
        if h is not None:
          # Layout de 4 valores: cantidad, monto, quiebre, FR
          return {"cantidad": e, "monto": f, "quiebre": g, "fr": h}
        else:
          # Layout de 3 valores: cantidad, monto, FR (sin quiebre propio)
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

      # Buscar el final del bloque: próxima fila vacía o próximo header 'TOP'
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

      # Si el corte fue por toparnos con el header 'TOP' del siguiente
      # bloque, hay que re-evaluar esa misma fila en la próxima vuelta
      # (no saltarla), o de lo contrario ese bloque se pierde.
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
    "hoja1",
]
nombres_hojas = [
    h for h in hojas.keys() if h.strip().lower() not in HOJAS_A_EXCLUIR
]

tabs = st.tabs([f"📊 {h}" for h in nombres_hojas] + ["📷 Escanear"])

for i, nombre_hoja in enumerate(nombres_hojas):
  with tabs[i]:
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
      # Prioridad: 1) columna con "descripcion" en el nombre (ej. "med0_descripcion"),
      # 2) columna con "producto" en el nombre, 3) columna J por posición.
      # Se separan en dos búsquedas para que "id_producto_sb"/"id_producto_pu"
      # (que traen códigos numéricos) no le ganen a la descripción real.
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

          # Nombres cortos solo para el eje del gráfico (la tabla de abajo
          # sigue mostrando el nombre completo del cliente).
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
                  marker_color="#00CC96",
                  text=grp_cli[col_monto].apply(formato_moneda),
                  textposition="outside",
                  textfont=dict(size=10),
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
                  line=dict(color="#ffffff", width=2),
                  marker=dict(size=6, color="#ffffff"),
                  text=grp_cli["Pct_Acumulado"].apply(lambda x: f"{x:.0f}%"),
                  textposition="top center",
                  textfont=dict(color="#ffffff", size=10),
                  customdata=grp_cli[col_cliente],
                  hovertemplate="%{customdata}<br>%{y:.1f}%<extra></extra>",
              ),
              secondary_y=True,
          )
          fig_pareto.update_layout(
              template="plotly_dark",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              margin=dict(t=30, b=110, l=10, r=10),
              height=380,
              showlegend=False,
              xaxis=dict(
                  tickangle=-45,
                  tickfont=dict(size=10),
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
        st.info(
            "No se encontró una columna de producto/SKU en esta hoja para"
            " calcular el Top Productos."
        )

      st.divider()

      st.subheader("📋 Registro Completo de Ventas SI")
      busqueda_si = st.text_input(
          "🔍 Buscar en registros SI (Descripción, SKU, Factura, etc.):",
          key=f"search_si_{i}",
      )

      df_si_det = df_si_filt.copy()

      # CORTE HASTA ES_INFLAMABLE
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

        canales_principales = ["Consumo", "Farma", "Terceros"]

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
                  marker_color="#f97316",
              )
          )
          fig_bar.add_trace(
              go.Bar(
                  y=df_resumen[mes_col],
                  x=df_resumen["Meta"],
                  name="Meta",
                  orientation="h",
                  marker_color="#109618",
              )
          )
          fig_bar.update_layout(
              barmode="group",
              height=280,
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#ffffff"),
              margin=dict(t=10, b=10, l=10, r=10),
              xaxis=dict(gridcolor="#222222"),
              yaxis=dict(gridcolor="#222222"),
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

        # =================================================================
        # SECCIÓN REDISEÑADA: TABLA Y GRÁFICO MEJORADO DE OC Y PROYECCIÓN COMPRA
        # =================================================================
        st.divider()
        st.markdown("#### 📦 Detalle OC Vigente y Proyección Compra")
        
        # ---> NUEVO FILTRO TIPO BOTÓN (RADIO) AÑADIDO AQUÍ <---
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

              # Detiene la lectura al llegar a filas de totales (Cierre, Meta, Resultado, Cumplimiento)
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
          st.warning(f"No se pudo leer la tabla OC directamente del Excel ({e}). Se muestra vacío.")

        df_oc_tab = pd.DataFrame(
            datos_oc_proyeccion,
            columns=["Concepto", "Canal", "Monto OC", "FR", "Proyección salida", "OC extra"],
        )
        
        # Filtramos la tabla dependiendo del valor del radio button
        if vista_oc != "Ambos":
            df_oc_tab = df_oc_tab[df_oc_tab["Concepto"] == vista_oc]

        # KPIs Resumen de la sección OC
        tot_monto_oc = df_oc_tab["Monto OC"].sum()
        tot_proy_salida = df_oc_tab["Proyección salida"].sum()

        col_k1, col_k2 = st.columns(2)
        col_k1.metric("📦 Monto Total OC", formato_moneda(tot_monto_oc))
        col_k2.metric(
            "🚚 Total Proyección Salida", formato_moneda(tot_proy_salida)
        )

        st.markdown("---")

        # Disposición en 2 columnas: Tabla a la izquierda, Gráfico a la derecha
        col_oc_tabla, col_oc_grafico = st.columns([1.1, 1], gap="medium")

        with col_oc_tabla:
          st.markdown("##### 📋 Tabla Detalle")
          st.dataframe(
              df_oc_tab,
              column_config={
                  "Concepto": st.column_config.TextColumn("Categoría / Estado"),
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

          # Modelo limpio: Barras Verticales Agrupadas por Canal y Categoría con valores formateados en Millones ($M)
          df_oc_plot = df_oc_tab.copy()
          df_oc_plot["Etiqueta"] = (
              df_oc_plot["Canal"]
              + "<br><sub>("
              + df_oc_plot["Concepto"]
              + ")</sub>"
          )

          fig_oc = go.Figure()

          # Barra Monto OC
          fig_oc.add_trace(
              go.Bar(
                  x=df_oc_plot["Etiqueta"],
                  y=df_oc_plot["Monto OC"],
                  name="Monto OC",
                  marker_color="#0070f3",
                  text=[
                      f"${v/1e6:.1f}M" if v > 0 else "$0"
                      for v in df_oc_plot["Monto OC"]
                  ],
                  textposition="outside",
                  textfont=dict(size=10, color="#ffffff"),
              )
          )

          # Barra Proyección Salida
          fig_oc.add_trace(
              go.Bar(
                  x=df_oc_plot["Etiqueta"],
                  y=df_oc_plot["Proyección salida"],
                  name="Proyección Salida",
                  marker_color="#109618",
                  text=[
                      f"${v/1e6:.1f}M" if v > 0 else "$0"
                      for v in df_oc_plot["Proyección salida"]
                  ],
                  textposition="outside",
                  textfont=dict(size=10, color="#ffffff"),
              )
          )

          fig_oc.update_layout(
              barmode="group",
              height=360,
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#ffffff"),
              margin=dict(t=30, b=10, l=10, r=10),
              xaxis=dict(gridcolor="#222222", tickangle=0),
              yaxis=dict(
                  gridcolor="#222222",
                  showticklabels=False,
                  range=[0, df_oc_plot["Monto OC"].max() * 1.22] if not df_oc_plot.empty else [0, 100],
              ),
              legend=dict(orientation="h", y=1.15, x=0.2),
          )
          st.plotly_chart(
              fig_oc, use_container_width=True, key=f"bar_oc_comp_{i}"
          )

        # Sección: Tabla Proyecciones Metas por Mes
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
                      "background-color: rgba(0, 112, 243, 0.4); color:"
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
      col_desc_stock = next(
          (c for c in df.columns if "descripcion" in c.lower()), None
      )
      if not col_desc_stock and len(df.columns) > 3:
        col_desc_stock = df.columns[3]  # Columna D
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

      # ---------------------------------------------------------------
      # SKU (columnas B y C de la propia hoja STOCK)
      # La hoja STOCK ya trae: A=codigo_articulo, B=codigo_sb, C=codigo_pu.
      # No hace falta cruzar con ninguna otra hoja: se usan directo.
      # ---------------------------------------------------------------
      col_sku_sb = next(
          (c for c in df.columns if c.strip().lower() == "codigo_sb"), None
      )
      col_sku_pu = next(
          (c for c in df.columns if c.strip().lower() == "codigo_pu"), None
      )
      # Respaldo por posición: si por algún motivo no calzan los nombres,
      # se usan la columna B (índice 1) y C (índice 2) tal cual.
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

      col_dash1, col_dash2 = st.columns([1, 2.3])

      # Filtros de STOCK: Código, SKU SB (columna B) y SKU PU (columna C).
      # Son mutuamente excluyentes: al elegir uno, los otros dos vuelven a "Todos".
      key_codigo = f"sel_codigo_stock_{i}"
      key_sku_sb = f"sel_sku_sb_stock_{i}"
      key_sku_pu = f"sel_sku_pu_stock_{i}"

      def _limpiar_otros_filtros(keys_a_limpiar):
        for k in keys_a_limpiar:
          if k in st.session_state:
            st.session_state[k] = "Todos"

      with col_dash2:
        # Los filtros se centran dejando márgenes livianos a los costados.
        _pad_izq, filtro_codigo_col, filtro_sku_sb_col, filtro_sku_pu_col, _pad_der = (
            st.columns([0.3, 1, 1, 1, 0.3])
        )

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

      if codigo_sel != "Todos":
        prod_sel = codigo_sel
      elif sku_sb_sel != "Todos":
        prod_sel = sku_sb_sel
      elif sku_pu_sel != "Todos":
        prod_sel = sku_pu_sel
      else:
        prod_sel = "Seleccione..."


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

      # % de Stock Crítico: unidades ya vencidas + que vencen en menos de 6 meses,
      # sobre el total de unidades registradas (con la selección de filtros activa).
      total_critico = total_vencido + total_menos_6m
      pct_critico = (
          (total_critico / total_unidades * 100) if total_unidades > 0 else 0.0
      )

      st.markdown(
          """
              <style>
              .critico-card { border-radius: 8px; padding: 14px 18px; margin-bottom: 15px;
                border: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
              </style>
              """,
          unsafe_allow_html=True,
      )
      color_pct_critico = (
          "#e74c3c" if pct_critico >= 15
          else "#f1c40f" if pct_critico >= 5
          else "#2ecc71"
      )
      st.markdown(
          '<div class="critico-card" style="background-color: #141414;">'
          '<span style="color:#aaaaaa; font-weight:600; text-transform:uppercase; font-size:13px;">'
          '⚠️ % de Stock Crítico (vencido + vence en &lt; 6 meses)</span>'
          f'<span style="color:{color_pct_critico}; font-size:26px; font-weight:bold;">{pct_critico:.2f}%</span>'
          "</div>",
          unsafe_allow_html=True,
      )

      # Filtro por categoría de caducidad: un selector simple y confiable
      # (los botones coloreados con CSS no se pintaban bien en todos los casos).
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

      # df_dash filtrado por la categoría de caducidad seleccionada arriba.
      # Se usa en las secciones de abajo (localizadores, estado de lote, detalle).
      if filtro_actual != "Todos":
        df_dash_alerta = df_dash[df_dash["Alerta_Caducidad"] == filtro_actual].copy()
      else:
        df_dash_alerta = df_dash.copy()

      with col_dash1:
        st.markdown(
            """
                <style>
                .stock-card { border-radius: 5px; padding: 15px; margin-bottom: 10px; text-align: center; color: white; font-weight: bold; }
                </style>
                """,
            unsafe_allow_html=True,
        )

        def _borde(valor):
          return "border: 2px solid #ffffff;" if filtro_actual == valor else ""

        st.markdown(
            '<div class="stock-card" style="background-color: #333; color:'
            f' white; {_borde("Todos")}">Unidades Registradas<br><span'
            f' style="font-size:24px;">{formato_unidades(total_unidades)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color:'
            f' #8b0000; {_borde("Vencido")}">Vencido<br><span'
            f' style="font-size:24px;">{formato_unidades(total_vencido)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color:'
            f' #e74c3c; {_borde("Menos de 6 meses")}">Vence en &lt; 6 meses<br><span'
            f' style="font-size:24px;">{formato_unidades(total_menos_6m)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color: #f1c40f; color:'
            f' black; {_borde("Pronto vence (6-13m)")}">Pronto vence (6 a 13'
            ' meses)<br><span'
            f' style="font-size:24px;">{formato_unidades(total_pronto)}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stock-card" style="background-color:'
            f' #2ecc71; {_borde("Vigente (> 13m)")}">Vigentes (> 13 meses)<br><span'
            f' style="font-size:24px;">{formato_unidades(total_vigentes)}</span></div>',
            unsafe_allow_html=True,
        )

      with col_dash2:
        st.markdown("#### Estado de caducidad")
        labels = ["Vencido", "< 6 meses", "6 a 13 meses", "Vigente (> 13m)"]
        values = [total_vencido, total_menos_6m, total_pronto, total_vigentes]
        colors = ["#8b0000", "#e74c3c", "#f1c40f", "#2ecc71"]

        total_donut = sum(values)
        if total_donut > 0:
          # Texto propio con 2 decimales para que los segmentos muy chicos
          # (ej. 0.00%) también se alcancen a leer bien, afuera de la dona.
          textos_pct = [
              f"{lbl}<br>{(v / total_donut * 100):.2f}%"
              for lbl, v in zip(labels, values)
          ]
          fig_pie = go.Figure(
              data=[
                  go.Pie(
                      labels=labels,
                      values=values,
                      hole=0.55,
                      marker=dict(colors=colors, line=dict(color="#0e1117", width=2)),
                      text=textos_pct,
                      texttemplate="%{text}",
                      textposition="outside",
                      textfont=dict(size=12, color="#ffffff"),
                  )
              ]
          )
          fig_pie.update_layout(
              height=380,
              margin=dict(t=20, b=60, l=60, r=60),
              paper_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#ffffff"),
              showlegend=True,
              legend=dict(
                  orientation="h",
                  y=-0.15,
                  x=0.5,
                  xanchor="center",
                  yanchor="top",
              ),
          )
          # Se centra el gráfico dentro de la columna para que no quede
          # estirado a lo ancho ni deje espacio vacío desbalanceado.
          _pad_chart_izq, col_chart, _pad_chart_der = st.columns([0.3, 2, 0.3])
          with col_chart:
            st.plotly_chart(
                fig_pie, use_container_width=True, key=f"pie_stock_{i}"
            )
        else:
          st.info("Sin registros para mostrar.")

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
              '<div class="stock-card" style="background-color:'
              f" {color_vence}; {color_texto} border: 1px solid #555;\">Plazo de"
              f' vencimiento<br><span style="font-size:20px;">{texto_vence}</span></div>',
              unsafe_allow_html=True,
          )

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
                  f"""<div style="background-color: #141414; border: 1px solid #0070f3; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 15px;">
                                    <div style="font-size: 12px; color: #aaaaaa; font-weight: 600; text-transform: uppercase;">{nombre_est}</div>
                                    <div style="font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 3px;">{formato_unidades(cant_est)}</div>
                                </div>""",
                  unsafe_allow_html=True,
              )

        st.divider()

      detalle_filtro = "(General)"
      partes_filtro = []
      if codigo_sel != "Todos":
        partes_filtro.append(f"Código: {codigo_sel}")
      if sku_sb_sel != "Todos":
        partes_filtro.append(f"SKU SB: {sku_sb_sel}")
      if sku_pu_sel != "Todos":
        partes_filtro.append(f"SKU PU: {sku_pu_sel}")
      if filtro_actual != "Todos":
        partes_filtro.append(f"Caducidad: {filtro_actual}")
      if partes_filtro:
        detalle_filtro = f"({' | '.join(partes_filtro)})"

      st.subheader(f"📋 Detalle de Stock y Lotes {detalle_filtro}")

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

      st.divider()

      # TOP LOCALIZADORES CON MÁS STOCK POR VENCER (Vencido + < 6 meses,
      # o la categoría seleccionada en las tarjetas de arriba).
      if col_loc and col_loc in df_dash.columns:
        if filtro_actual != "Todos":
          titulo_loc = f"##### 📍 Top Localizadores — {filtro_actual}"
          df_critico = df_dash_alerta.copy()
        else:
          titulo_loc = "##### 📍 Top Localizadores con más Stock por Vencer"
          df_critico = df_dash[
              df_dash["Alerta_Caducidad"].isin(["Vencido", "Menos de 6 meses"])
          ].copy()

        st.markdown(titulo_loc)

        # Se excluyen las filas sin localizador registrado.
        df_critico = df_critico[
            df_critico[col_loc].notna()
            & (df_critico[col_loc].astype(str).str.strip() != "")
        ].copy()

        if not df_critico.empty:
          cols_group = [col_loc]
          if col_desc_stock and col_desc_stock in df_critico.columns:
            cols_group.append(col_desc_stock)

          if col_cant:
            grp_loc = (
                df_critico.groupby(cols_group, dropna=False)[col_cant]
                .sum()
                .reset_index()
                .rename(columns={col_cant: "Cantidad"})
            )
          else:
            grp_loc = (
                df_critico.groupby(cols_group, dropna=False)
                .size()
                .reset_index(name="Cantidad")
            )

          grp_loc = grp_loc.sort_values(by="Cantidad", ascending=False).head(10)

          etiqueta_barra = (
              grp_loc[col_loc].astype(str)
              + (
                  " — " + grp_loc[col_desc_stock].astype(str)
                  if col_desc_stock and col_desc_stock in grp_loc.columns
                  else ""
              )
          )
          grp_loc_sorted = grp_loc.assign(_etiqueta=etiqueta_barra).sort_values(
              by="Cantidad", ascending=True
          )
          fig_loc = px.bar(
              grp_loc_sorted,
              x="Cantidad",
              y="_etiqueta",
              orientation="h",
              text_auto=",.0f",
              color_discrete_sequence=["#e74c3c"],
          )
          fig_loc.update_traces(
              textfont_size=11, textposition="outside", cliponaxis=False
          )
          fig_loc.update_layout(
              template="plotly_dark",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
              margin=dict(t=10, b=10, l=10, r=10),
              height=320,
              xaxis_title="",
              yaxis_title="",
          )
          st.plotly_chart(
              fig_loc, use_container_width=True, key=f"top_loc_stock_{i}"
          )

          rename_cols = {col_loc: "Localizador"}
          if col_desc_stock and col_desc_stock in grp_loc.columns:
            rename_cols[col_desc_stock] = "Descripción Producto"
          grp_loc_disp = grp_loc.rename(columns=rename_cols)
          st.dataframe(
              grp_loc_disp,
              column_config={
                  "Cantidad": st.column_config.NumberColumn(
                      "Cantidad", format="%,d"
                  ),
              },
              hide_index=True,
              use_container_width=True,
          )
        else:
          st.info(
              "No hay stock (con localizador registrado) para la categoría"
              " seleccionada."
          )



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
              in ["marca", "brand", "lab", "laboratorio", "proveedor"]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(
                  k in c.lower()
                  for k in ["marca", "brand", "lab", "proveedor"]
              )
          ),
          None,
      )
      col_glosa = next(
          (c for c in df.columns if c.strip().lower() == "glosa"),
          None,
      ) or next(
          (c for c in df.columns if "glosa" in c.lower()),
          None,
      )
      col_u_compra = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in [
                  "unidades_compra",
                  "unidades_pedidas",
                  "unid_pedidas",
                  "cant_pedida",
                  "cantidad_pedida",
                  "unidades_solicitadas",
                  "cant_solic",
                  "cantidad",
                  "unidades",
                  "solicitado",
                  "cant",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(
                  k in c.lower() for k in ["comp", "pedi", "solic", "cant", "unid"]
              )
          ),
          None,
      )
      col_u_recib = next(
          (
              c
              for c in df.columns
              if c.strip().lower()
              in [
                  "unidades_recibidas",
                  "unid_recibidas",
                  "cant_recibida",
                  "cantidad_recibida",
                  "unidades_entregadas",
                  "unid_entregadas",
                  "cant_entregada",
                  "recibido",
                  "entregado",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(k in c.lower() for k in ["recib", "entre", "despa"])
          ),
          None,
      )
      col_m_compra = next(
          (
              c
              for c in df.columns
              if c.lower().strip()
              in [
                  "compra total",
                  "monto_compra",
                  "monto compra",
                  "total_compra",
                  "costo_total",
                  "monto_pedido",
                  "val_compra",
                  "valor_compra",
                  "monto_solicitado",
                  "precio_total",
              ]
          ),
          None,
      ) or next(
          (
              c
              for c in df.columns
              if any(k in c.lower() for k in ["monto", "val", "cost", "total", "$"])
              and any(
                  k in c.lower() for k in ["comp", "pedi", "solic", "total"]
              )
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
      for c_num in cols_a_num:
        df[c_num] = df[c_num].apply(limpiar_numero)

      if not col_m_compra or col_m_compra not in df.columns:
        df["monto_compra_calc"] = df[col_u_compra] * df[col_precio]
        col_m_compra = "monto_compra_calc"

      if not col_m_recib or col_m_recib not in df.columns:
        if col_precio in df.columns and (df[col_precio] > 0).any():
          df["monto_recibido_calc"] = df[col_u_recib] * df[col_precio]
        else:
          precio_linea = (
              df[col_m_compra] / df[col_u_compra].replace(0, 1)
          ).fillna(0)
          df["monto_recibido_calc"] = df[col_u_recib] * precio_linea
        col_m_recib = "monto_recibido_calc"

      if col_quiebre and col_quiebre in df.columns:
        df["quiebre_monto_calc"] = df[col_quiebre].abs()
      else:
        df["quiebre_monto_calc"] = (df[col_m_compra] - df[col_m_recib]).clip(
            lower=0
        )

      df["quiebre_unid_calc"] = (df[col_u_compra] - df[col_u_recib]).clip(
          lower=0
      )

      def orden_semana_key(s):
        try:
          return (0, int(float(s)))
        except (ValueError, TypeError):
          return (1, str(s))

      semanas_todas = (
          sorted(
              [s for s in df[col_semana].unique() if str(s).strip() != ""],
              key=orden_semana_key,
          )
          if col_semana
          else []
      )
      # Se excluye del "Últimas 4 Semanas" la semana en curso / incompleta:
      # aquella que todavía no registra recepciones (Monto y Unidades Recibidas = 0),
      # ya que mostrarla en 0% distorsiona la visualización de Fill Rate.
      semanas_con_datos = list(semanas_todas)
      if semanas_con_datos and col_m_recib and col_u_recib:
        ultima_sem = semanas_con_datos[-1]
        df_ultima_sem = df[df[col_semana] == ultima_sem]
        recib_monto = df_ultima_sem[col_m_recib].sum() if col_m_recib in df.columns else 0
        recib_unds = df_ultima_sem[col_u_recib].sum() if col_u_recib in df.columns else 0
        if recib_monto == 0 and recib_unds == 0:
          semanas_con_datos = semanas_con_datos[:-1]
      ultimas_4_semanas = semanas_con_datos[-4:] if semanas_con_datos else []

      st.markdown("### 📅 Seleccionar Semana")
      opciones_semanas = {"Todas": "Todas"}
      for s in semanas_todas:
        val_str = fmt_sem(s)
        opciones_semanas[f"Semana {val_str}"] = s

      semanas_disp = list(opciones_semanas.keys())
      idx_defecto = len(semanas_disp) - 1 if semanas_todas else 0

      semana_sel_raw = st.radio(
          "Selección de Semana",
          options=semanas_disp,
          index=idx_defecto,
          horizontal=True,
          label_visibility="collapsed",
          width="stretch",
          key=f"semana_sel_{nombre_hoja}_{i}",
      )
      semana_sel = opciones_semanas[semana_sel_raw]

      df_filt = df.copy()
      if semana_sel != "Todas" and col_semana:
        df_filt = df_filt[df_filt[col_semana] == semana_sel]
      st.divider()

      # =================================================================
      # MÉTRICAS DE OC Y MONTOS EN LA ZONA SUPERIOR
      # =================================================================
      if is_sb and col_div and col_oc:
        st.markdown("#### 📊 Resumen de Órdenes y Montos")

        # Filtros de División
        mask_farma = df_filt[col_div].astype(str).str.upper().str.contains("FARMA", na=False)
        mask_consumo = df_filt[col_div].astype(str).str.upper().str.contains("CONSUMO", na=False)

        # Cálculos de Solares (filtrando por la columna "glosa" que contenga "SOLARES")
        # Se calcula ANTES que Consumo porque Solares es un subconjunto de la división
        # Consumo y debe excluirse de ese grupo para no sumarse dos veces.
        if col_glosa and col_glosa in df_filt.columns:
          mask_solares = (
              df_filt[col_glosa].astype(str).str.upper().str.contains("SOLARES", na=False)
          )
          oc_solares = df_filt[mask_solares][col_oc].nunique()
          monto_solares = df_filt[mask_solares][col_m_compra].sum()
        else:
          mask_solares = pd.Series(False, index=df_filt.index)
          oc_solares = 0
          monto_solares = 0

        # Consumo excluye lo que ya está contabilizado como Solares, para que
        # OC Consumo / Monto Consumo no dupliquen los registros de Solares
        # (Solares pertenece a la división Consumo pero se reporta aparte).
        mask_consumo = mask_consumo & ~mask_solares

        # Cálculos de OC
        oc_farma = df_filt[mask_farma][col_oc].nunique()
        oc_consumo = df_filt[mask_consumo][col_oc].nunique()

        # Cálculos de Monto
        monto_farma = df_filt[mask_farma][col_m_compra].sum()
        monto_consumo = df_filt[mask_consumo][col_m_compra].sum()
        monto_total = df_filt[col_m_compra].sum()

        # UI - Grid equilibrado de 4 columnas x 2 filas, agrupado por categoría
        kf1, kf2, kf3, kf4 = st.columns(4)
        kf1.metric("📦 OC Farma", str(oc_farma))
        kf2.metric("💊 Monto Farma", formato_moneda(monto_farma))
        kf3.metric("🛒 OC Consumo", str(oc_consumo))
        kf4.metric("🛍️ Monto Consumo", formato_moneda(monto_consumo))

        ks1, ks2, ks3, ks4 = st.columns(4)
        ks1.metric("☀️ OC Solares", str(oc_solares))
        ks2.metric("💵 Monto Solares", formato_moneda(monto_solares))
        ks3.metric("💰 Monto Total", formato_moneda(monto_total))

        st.divider()

      # =================================================================
      # NUEVO BLOQUE: MÉTRICAS DE OC Y MONTO TOTAL PARA PU (SIN DIVISIÓN)
      # =================================================================
      if is_pu and col_oc and col_m_compra:
        st.markdown("#### 📊 Resumen General de Órdenes y Compras PU")

        # En PU se consideran todas las divisiones juntas.
        cantidad_oc_pu = df_filt[col_oc].nunique()
        monto_total_pu = df_filt[col_m_compra].sum()

        # UI (2 KPIs, sin separar por división)
        kpu1, kpu2 = st.columns(2)
        kpu1.metric("📦 Cantidad de OC", str(cantidad_oc_pu))
        kpu2.metric("💰 Monto Total de Compra", formato_moneda(monto_total_pu))

        st.divider()
      # =================================================================

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

            st.markdown(f"### ⏱️ Fill rate W{fmt_sem(sem_actual)} (PU General)")
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
          oc_abierta_map = df_sig.groupby(col_sku)[
              col_u_compra
          ].sum().to_dict()

        df_sem_top = df[df[col_semana] == sem_top].copy()

        if df_sem_top.empty:
          st.info(
              f"No se encontraron registros para la semana {fmt_sem(sem_top)}."
          )
        else:
          if is_pu:
            if crit_orden == "Monto ($)":
              tot_compra_val = df_sem_top[col_m_compra].sum()
              tot_recib_val = df_sem_top[col_m_recib].sum()
              fr_div_pct = (
                  (tot_recib_val / tot_compra_val * 100)
                  if tot_compra_val > 0
                  else 0.0
              )
              delta_str = (
                  f"{tot_recib_val - tot_compra_val:,.0f} $ (Dif)".replace(
                      ",", "."
                  )
              )
              lbl_metric = "Fill Rate General (Monto)"
            else:
              tot_compra_val = df_sem_top[col_u_compra].sum()
              tot_recib_val = df_sem_top[col_u_recib].sum()
              fr_div_pct = (
                  (tot_recib_val / tot_compra_val * 100)
                  if tot_compra_val > 0
                  else 0.0
              )
              delta_str = (
                  f"{tot_recib_val - tot_compra_val:,.0f} Unds (Dif)".replace(
                      ",", "."
                  )
              )
              lbl_metric = "Fill Rate General (Unidades)"

            st.markdown(f"#### 📌 RESUMEN GENERAL PU (Sem {fmt_sem(sem_top)})")
            col_metric_fr, col_metric_oc = st.columns(2)
            with col_metric_fr:
              st.metric(
                  label=lbl_metric,
                  value=f"{fr_div_pct:.1f}%",
                  delta=delta_str,
              )

            # % de OC cumplidas al 100% (sin quiebre en ninguna de sus líneas)
            # vs OC que tuvieron algún quiebre, para la semana seleccionada.
            if col_oc and col_oc in df_sem_top.columns:
              grp_oc_cumpl = df_sem_top.groupby(col_oc)[
                  "quiebre_unid_calc"
              ].sum()
              total_oc_sem = grp_oc_cumpl.shape[0]
              oc_cumplidas = int((grp_oc_cumpl <= 0).sum())
              oc_con_quiebre = total_oc_sem - oc_cumplidas
              pct_oc_cumplidas = (
                  (oc_cumplidas / total_oc_sem * 100) if total_oc_sem > 0 else 0.0
              )

              with col_metric_oc:
                st.metric(
                    label="OC Cumplidas al 100%",
                    value=f"{pct_oc_cumplidas:.1f}%",
                    delta=(
                        f"{oc_cumplidas} de {total_oc_sem} OC"
                        f" ({oc_con_quiebre} con quiebre)"
                    ),
                    delta_color="off",
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
              )
              lbl_oc = (
                  f"OC Abierta Sem {fmt_sem(sem_sig)}"
                  if sem_sig
                  else "OC Abierta"
              )
              grp_top_disp[lbl_oc] = grp_top["OC abierta"].apply(
                  formato_unidades
              )

              st.dataframe(
                  grp_top_disp, hide_index=True, use_container_width=True
              )

          elif is_sb and col_div:
            divisiones_unicas = [d for d in df_sem_top[col_div].dropna().unique()]
            div_cons = next(
                (d for d in divisiones_unicas if "CONSUMO" in str(d).upper()),
                None,
            )
            div_farm = next(
                (d for d in divisiones_unicas if "FARMA" in str(d).upper()),
                None,
            )

            lista_divs = [d for d in [div_cons, div_farm] if d is not None]
            if not lista_divs and len(divisiones_unicas) > 0:
              lista_divs = divisiones_unicas[:2]

            col_t1, col_t2 = st.columns(2)
            columnas_ui = [col_t1, col_t2]

            for idx, div_nombre in enumerate(lista_divs):
              if idx >= 2:
                break
              with columnas_ui[idx]:
                df_div = df_sem_top[
                    df_sem_top[col_div] == div_nombre
                ].copy()

                if crit_orden == "Monto ($)":
                  tot_compra_val = df_div[col_m_compra].sum()
                  tot_recib_val = df_div[col_m_recib].sum()
                  fr_div_pct = (
                      (tot_recib_val / tot_compra_val * 100)
                      if tot_compra_val > 0
                      else 0.0
                  )
                  delta_str = (
                      f"{tot_recib_val - tot_compra_val:,.0f} $ (Dif)".replace(
                          ",", "."
                      )
                  )
                  lbl_metric = f"Fill Rate Monto (Sem {fmt_sem(sem_top)})"
                else:
                  tot_compra_val = df_div[col_u_compra].sum()
                  tot_recib_val = df_div[col_u_recib].sum()
                  fr_div_pct = (
                      (tot_recib_val / tot_compra_val * 100)
                      if tot_compra_val > 0
                      else 0.0
                  )
                  delta_str = (
                      f"{tot_recib_val - tot_compra_val:,.0f} Unds"
                      " (Dif)".replace(",", ".")
                  )
                  lbl_metric = f"Fill Rate Unidades (Sem {fmt_sem(sem_top)})"

                st.markdown(f"#### 📌 {str(div_nombre).upper()}")
                st.metric(
                    label=lbl_metric,
                    value=f"{fr_div_pct:.1f}%",
                    delta=delta_str,
                )

                grp_top = df_div.groupby(
                    [col_sku, col_desc], as_index=False
                ).agg({
                    col_u_compra: "sum",
                    col_m_compra: "sum",
                    "quiebre_monto_calc": "sum",
                    "quiebre_unid_calc": "sum",
                })

                if col_rechazado and col_rechazado in df_div.columns:
                  grp_rech = df_div.groupby(
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
                grp_top = grp_top.sort_values(
                    by=col_sort, ascending=False
                ).head(15)

                grp_top_disp = pd.DataFrame()
                grp_top_disp["SKU"] = grp_top[col_sku].astype(str)
                grp_top_disp["Descripción"] = grp_top[col_desc]
                grp_top_disp["Unidades Compra"] = grp_top[col_u_compra].apply(
                    formato_unidades
                )
                grp_top_disp["Compra Total ($)"] = grp_top[col_m_compra].apply(
                    formato_moneda
                )
                grp_top_disp["Quiebre ($)"] = grp_top[
                    "quiebre_monto_calc"
                ].apply(
                    lambda x: f"-{formato_moneda(abs(x))}" if x > 0 else "$0"
                )
                col_r_name = (
                    col_rechazado
                    if (col_rechazado and col_rechazado in grp_top.columns)
                    else "Suma de RECHAZADO"
                )
                grp_top_disp["Rechazado (Unds)"] = grp_top[col_r_name].apply(
                    formato_unidades
                )
                lbl_oc = (
                    f"OC Abierta Sem {fmt_sem(sem_sig)}"
                    if sem_sig
                    else "OC Abierta"
                )
                grp_top_disp[lbl_oc] = grp_top["OC abierta"].apply(
                    formato_unidades
                )

                st.dataframe(
                    grp_top_disp, hide_index=True, use_container_width=True
                )

      # =================================================================
      # DETALLE DE PRODUCTOS SOLARES (justo debajo de "TOP 15 Quiebres
      # (Por División)")
      # =================================================================
      if is_sb and col_div and col_oc and col_glosa and col_glosa in df_filt.columns:
        st.divider()
        st.markdown("#### ☀️ Detalle de Productos Solares")

        # Indicadores de Fill Rate para Solares, en el mismo estilo que
        # los indicadores de "TOP 15 Quiebres (Por División)" (Fill Rate
        # + variación en $ / Unds respecto de lo comprado).
        mask_solares_ind = (
            df_filt[col_glosa].astype(str).str.upper().str.contains("SOLARES", na=False)
        )
        df_solares_ind = df_filt[mask_solares_ind].copy()

        etiqueta_sem_ind = (
            f"Sem {fmt_sem(semana_sel)}" if semana_sel != "Todas" else "Todas"
        )

        st.markdown("#### 📌 SOLARES")
        ind_s1, ind_s2 = st.columns(2)
        with ind_s1:
          tot_compra_sol = df_solares_ind[col_m_compra].sum() if col_m_compra else 0
          tot_recib_sol = df_solares_ind[col_m_recib].sum() if col_m_recib else 0
          fr_sol_monto = (
              (tot_recib_sol / tot_compra_sol * 100) if tot_compra_sol > 0 else 0.0
          )
          delta_sol_monto = f"{tot_recib_sol - tot_compra_sol:,.0f} $ (Dif)".replace(
              ",", "."
          )
          st.metric(
              label=f"Fill Rate Monto ({etiqueta_sem_ind})",
              value=f"{fr_sol_monto:.1f}%",
              delta=delta_sol_monto,
          )
        with ind_s2:
          tot_compra_sol_u = (
              df_solares_ind[col_u_compra].sum() if col_u_compra else 0
          )
          tot_recib_sol_u = df_solares_ind[col_u_recib].sum() if col_u_recib else 0
          fr_sol_unds = (
              (tot_recib_sol_u / tot_compra_sol_u * 100)
              if tot_compra_sol_u > 0
              else 0.0
          )
          delta_sol_unds = (
              f"{tot_recib_sol_u - tot_compra_sol_u:,.0f} Unds (Dif)".replace(
                  ",", "."
              )
          )
          st.metric(
              label=f"Fill Rate Unidades ({etiqueta_sem_ind})",
              value=f"{fr_sol_unds:.1f}%",
              delta=delta_sol_unds,
          )

        st.divider()

        df_solares = df_solares_ind.copy()

        if not df_solares.empty:
          col_det_s1, col_det_s2 = st.columns(2)
          with col_det_s1:
            ocs_solares_disp = ["Todas"] + sorted(
                [str(x) for x in df_solares[col_oc].dropna().unique()]
            )
            oc_solar_sel = st.selectbox(
                "Filtrar Solares por OC:",
                ocs_solares_disp,
                key=f"det_oc_solares_{nombre_hoja}_{i}",
            )
          with col_det_s2:
            skus_solares_disp = ["Todos"] + sorted(
                [str(x) for x in df_solares[col_sku].dropna().unique()]
            )
            sku_solar_sel = st.selectbox(
                "Filtrar Solares por SKU:",
                skus_solares_disp,
                key=f"det_sku_solares_{nombre_hoja}_{i}",
            )

          if oc_solar_sel != "Todas":
            df_solares = df_solares[
                df_solares[col_oc].astype(str) == oc_solar_sel
            ]
          if sku_solar_sel != "Todos":
            df_solares = df_solares[
                df_solares[col_sku].astype(str) == sku_solar_sel
            ]

          if col_rechazado and col_rechazado in df_solares.columns:
            idx_corte_s = list(df_solares.columns).index(col_rechazado) + 1
            df_solares_final = df_solares.iloc[:, :idx_corte_s].copy()
          else:
            df_solares_final = df_solares.copy()

          renombrar_columnas_solares = {
              "id_producto": "SKU",
              "id_prod": "SKU",
              "numero_orden": "OC",
              "num_oc": "OC",
              "orden_compra": "OC",
              "descripcion": "Descripción",
              "unidades_compra": "Unidades Compra",
              "unidades_recibidas": "Unidades Recibidas",
              "unidades_rechazadas": "Unidades Rechazadas",
              "cantidad": "Unidades Compra",
              "cantidad_recibida": "Unidades Recibidas",
              "fecha_hora_despacho_default": "Fecha Despacho",
              "precio_final": "Precio Final",
              "precio_total": "Precio Total",
          }
          nuevas_columnas_s = {}
          for col in df_solares_final.columns:
            col_lower = str(col).strip().lower()
            if col_lower in renombrar_columnas_solares:
              nuevas_columnas_s[col] = renombrar_columnas_solares[col_lower]
            else:
              nuevas_columnas_s[col] = str(col).replace("_", " ").strip().title()
          df_solares_final = df_solares_final.rename(columns=nuevas_columnas_s)

          st.dataframe(
              df_solares_final, hide_index=True, use_container_width=True
          )
        else:
          st.info("No hay productos Solares registrados para la semana seleccionada.")

      st.divider()

      # RESUMEN 4 SEMANAS
      if col_semana:
        df_base_fr = df.copy()
        df_4sem = df_base_fr[
            df_base_fr[col_semana].isin(ultimas_4_semanas)
        ].copy()

        st.subheader("📊 Resumen Fill Rate (Últimas 4 Semanas)")

        if is_pu:
          grp = df_4sem.groupby(col_semana, as_index=False)[
              [col_u_compra, col_u_recib, col_m_compra, col_m_recib]
          ].sum()
          grp["FR_Unds_pct"] = (grp[col_u_recib] / grp[col_u_compra] * 100).fillna(
              0
          )
          grp["FR_Monto_pct"] = (
              grp[col_m_recib] / grp[col_m_compra] * 100
          ).fillna(0)

          df_disp = grp.copy()
          df_disp[col_semana] = df_disp[col_semana].apply(fmt_sem)
          df_disp[col_u_compra] = df_disp[col_u_compra].apply(formato_unidades)
          df_disp[col_u_recib] = df_disp[col_u_recib].apply(formato_unidades)
          df_disp[col_m_compra] = df_disp[col_m_compra].apply(formato_moneda)
          df_disp[col_m_recib] = df_disp[col_m_recib].apply(formato_moneda)
          df_disp["FR_Unds_pct"] = df_disp["FR_Unds_pct"].apply(
              lambda x: f"{x:.2f}%"
          )
          df_disp["FR_Monto_pct"] = df_disp["FR_Monto_pct"].apply(
              lambda x: f"{x:.2f}%"
          )

          df_disp.columns = [
              "Semana",
              "Unidades Compra",
              "Unidades Recibidas",
              "Monto Compra ($)",
              "Monto Recibido ($)",
              "Fill Rate Unidades",
              "Fill Rate Monto",
          ]
          st.dataframe(df_disp, hide_index=True, use_container_width=True)
          st.divider()

          col_g1, col_g2 = st.columns(2)
          with col_g1:
            st.markdown("##### Fill Rate por Unidades (Evolutivo)")
            fig_unds = go.Figure(
                go.Bar(
                    x=[f"Sem {fmt_sem(s)}" for s in grp[col_semana]],
                    y=grp["FR_Unds_pct"],
                    text=[f"{v:.1f}%" for v in grp["FR_Unds_pct"]],
                    textposition="auto",
                    marker_color="#0070f3",
                )
            )
            fig_unds.update_layout(
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                yaxis=dict(
                    range=[0, 115], gridcolor="#222222", ticksuffix="%"
                ),
                xaxis=dict(gridcolor="#222222"),
            )
            st.plotly_chart(
                fig_unds,
                use_container_width=True,
                key=f"plot_unds_{nombre_hoja}_{i}",
            )

          with col_g2:
            st.markdown("##### Fill Rate por Monto (Evolutivo)")
            fig_monto = go.Figure(
                go.Bar(
                    x=[f"Sem {fmt_sem(s)}" for s in grp[col_semana]],
                    y=grp["FR_Monto_pct"],
                    text=[f"{v:.1f}%" for v in grp["FR_Monto_pct"]],
                    textposition="auto",
                    marker_color="#00adb5",
                )
            )
            fig_monto.update_layout(
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                yaxis=dict(
                    range=[0, 115], gridcolor="#222222", ticksuffix="%"
                ),
                xaxis=dict(gridcolor="#222222"),
            )
            st.plotly_chart(
                fig_monto,
                use_container_width=True,
                key=f"plot_monto_{nombre_hoja}_{i}",
            )

        elif is_sb and col_div:
          grp = df_4sem.groupby([col_semana, col_div], as_index=False)[
              [col_u_compra, col_u_recib, col_m_compra, col_m_recib]
          ].sum()
          grp["FR_Unds_pct"] = (grp[col_u_recib] / grp[col_u_compra] * 100).fillna(
              0
          )
          grp["FR_Monto_pct"] = (
              grp[col_m_recib] / grp[col_m_compra] * 100
          ).fillna(0)

          df_disp = grp.copy()
          df_disp[col_semana] = df_disp[col_semana].apply(fmt_sem)
          df_disp[col_u_compra] = df_disp[col_u_compra].apply(formato_unidades)
          df_disp[col_u_recib] = df_disp[col_u_recib].apply(formato_unidades)
          df_disp[col_m_compra] = df_disp[col_m_compra].apply(formato_moneda)
          df_disp[col_m_recib] = df_disp[col_m_recib].apply(formato_moneda)
          df_disp["FR_Unds_pct"] = df_disp["FR_Unds_pct"].apply(
              lambda x: f"{x:.2f}%"
          )
          df_disp["FR_Monto_pct"] = df_disp["FR_Monto_pct"].apply(
              lambda x: f"{x:.2f}%"
          )

          df_disp.columns = [
              "Semana",
              "División",
              "Unidades Compra",
              "Unidades Recibidas",
              "Monto Compra ($)",
              "Monto Recibido ($)",
              "Fill Rate Unidades",
              "Fill Rate Monto",
          ]
          st.dataframe(df_disp, hide_index=True, use_container_width=True)
          st.divider()

          col_g1, col_g2 = st.columns(2)
          p_unds = grp.pivot(
              index=col_semana, columns=col_div, values="FR_Unds_pct"
          ).reset_index()
          p_monto = grp.pivot(
              index=col_semana, columns=col_div, values="FR_Monto_pct"
          ).reset_index()

          tot_sem = df_4sem.groupby(col_semana, as_index=False)[
              [col_u_compra, col_u_recib, col_m_compra, col_m_recib]
          ].sum()
          tot_sem["Total_FR_Unds"] = (
              tot_sem[col_u_recib] / tot_sem[col_u_compra] * 100
          ).fillna(0)
          tot_sem["Total_FR_Monto"] = (
              tot_sem[col_m_recib] / tot_sem[col_m_compra] * 100
          ).fillna(0)

          with col_g1:
            st.markdown("##### Fill Rate por Unidades")
            fig_unds = go.Figure()
            for col_d in [c for c in p_unds.columns if c != col_semana]:
              color_bar = (
                  "#f97316" if "CONSUMO" in str(col_d).upper() else "#00adb5"
              )
              fig_unds.add_trace(
                  go.Bar(
                      x=[f"Sem {fmt_sem(s)}" for s in p_unds[col_semana]],
                      y=p_unds[col_d],
                      name=str(col_d).title(),
                      marker_color=color_bar,
                  )
              )
            fig_unds.add_trace(
                go.Scatter(
                    x=[f"Sem {fmt_sem(s)}" for s in tot_sem[col_semana]],
                    y=tot_sem["Total_FR_Unds"],
                    name="Total Semana",
                    mode="lines+markers+text",
                    text=[f"{v:.1f}%" for v in tot_sem["Total_FR_Unds"]],
                    textposition="top center",
                    line=dict(color="#e2e8f0", width=3),
                )
            )
            fig_unds.update_layout(
                barmode="group",
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                yaxis=dict(
                    range=[0, 115], gridcolor="#222222", ticksuffix="%"
                ),
                xaxis=dict(gridcolor="#222222"),
                legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(
                fig_unds, use_container_width=True, key=f"plot_unds_sb_{i}"
            )

          with col_g2:
            st.markdown("##### Fill Rate por Monto")
            fig_monto = go.Figure()
            for col_d in [c for c in p_monto.columns if c != col_semana]:
              color_bar = (
                  "#f97316" if "CONSUMO" in str(col_d).upper() else "#00adb5"
              )
              fig_monto.add_trace(
                  go.Bar(
                      x=[f"Sem {fmt_sem(s)}" for s in p_monto[col_semana]],
                      y=p_monto[col_d],
                      name=str(col_d).title(),
                      marker_color=color_bar,
                  )
              )
            fig_monto.add_trace(
                go.Scatter(
                    x=[f"Sem {fmt_sem(s)}" for s in tot_sem[col_semana]],
                    y=tot_sem["Total_FR_Monto"],
                    name="Total Semana",
                    mode="lines+markers+text",
                    text=[f"{v:.1f}%" for v in tot_sem["Total_FR_Monto"]],
                    textposition="top center",
                    line=dict(color="#e2e8f0", width=3),
                )
            )
            fig_monto.update_layout(
                barmode="group",
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                yaxis=dict(
                    range=[0, 115], gridcolor="#222222", ticksuffix="%"
                ),
                xaxis=dict(gridcolor="#222222"),
                legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(
                fig_monto, use_container_width=True, key=f"plot_monto_sb_{i}"
            )

        st.divider()

      # TABLAS DINÁMICAS: QUIEBRE POR MARCA
      if sem_top is not None and col_marca:
        st.subheader("🏷️ Resumen Quiebres por Marca")
        df_sem_marca = df[df[col_semana] == sem_top].copy()

        if is_pu:
          grp_m = df_sem_marca.groupby(col_marca, as_index=False).agg(
              {col_m_compra: "sum", "quiebre_monto_calc": "sum"}
          )
          grp_m = grp_m[grp_m["quiebre_monto_calc"] > 0]

          if not grp_m.empty:
            total_quiebre_div = grp_m["quiebre_monto_calc"].sum()
            grp_m["pct_quiebre"] = (
                (grp_m["quiebre_monto_calc"] / total_quiebre_div * 100)
                if total_quiebre_div > 0
                else 0.0
            )
            grp_m = grp_m.sort_values(
                by="quiebre_monto_calc", ascending=False
            )

            grp_m_disp = pd.DataFrame()
            grp_m_disp["Etiquetas de fila"] = grp_m[col_marca].astype(str)
            grp_m_disp["TOTAL COMPRA"] = grp_m[col_m_compra].apply(
                formato_moneda
            )
            grp_m_disp["MONTO QUIEBRE"] = grp_m["quiebre_monto_calc"].apply(
                lambda x: f"-{formato_moneda(abs(x))}"
            )
            grp_m_disp["QUIEBRE %"] = grp_m["pct_quiebre"].apply(
                lambda x: f"{x:.2f}%"
            )

            total_compra_div = grp_m[col_m_compra].sum()
            fila_total = pd.DataFrame([{
                "Etiquetas de fila": "Total general",
                "TOTAL COMPRA": formato_moneda(total_compra_div),
                "MONTO QUIEBRE": (
                    f"-{formato_moneda(abs(total_quiebre_div))}"
                ),
                "QUIEBRE %": "100.00%",
            }])
            grp_m_final = pd.concat(
                [grp_m_disp, fila_total], ignore_index=True
            )

            styled_df = grp_m_final.style.apply(
                aplicar_criticidad, subset=["QUIEBRE %"]
            )
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
          else:
            st.info(
                f"No hay quiebres registrados para la semana {fmt_sem(sem_top)} en"
                " PU."
            )

        elif is_sb and col_div:
          col_m1, col_m2 = st.columns(2)
          cols_marca_ui = [col_m1, col_m2]

          for idx, div_nombre in enumerate(lista_divs):
            if idx >= 2:
              break
            with cols_marca_ui[idx]:
              st.markdown(f"#### {str(div_nombre).upper()}")
              df_div_m = df_sem_marca[
                  df_sem_marca[col_div] == div_nombre
              ].copy()
              grp_m = df_div_m.groupby(col_marca, as_index=False).agg(
                  {col_m_compra: "sum", "quiebre_monto_calc": "sum"}
              )
              grp_m = grp_m[grp_m["quiebre_monto_calc"] > 0]

              if not grp_m.empty:
                total_quiebre_div = grp_m["quiebre_monto_calc"].sum()
                grp_m["pct_quiebre"] = (
                    (grp_m["quiebre_monto_calc"] / total_quiebre_div * 100)
                    if total_quiebre_div > 0
                    else 0.0
                )
                grp_m = grp_m.sort_values(
                    by="quiebre_monto_calc", ascending=False
                )

                grp_m_disp = pd.DataFrame()
                grp_m_disp["Etiquetas de fila"] = grp_m[col_marca].astype(str)
                grp_m_disp["TOTAL COMPRA"] = grp_m[col_m_compra].apply(
                    formato_moneda
                )
                grp_m_disp["MONTO QUIEBRE"] = grp_m["quiebre_monto_calc"].apply(
                    lambda x: f"-{formato_moneda(abs(x))}"
                )
                grp_m_disp["QUIEBRE %"] = grp_m["pct_quiebre"].apply(
                    lambda x: f"{x:.2f}%"
                )

                total_compra_div = grp_m[col_m_compra].sum()
                fila_total = pd.DataFrame([{
                    "Etiquetas de fila": "Total general",
                    "TOTAL COMPRA": formato_moneda(total_compra_div),
                    "MONTO QUIEBRE": (
                        f"-{formato_moneda(abs(total_quiebre_div))}"
                    ),
                    "QUIEBRE %": "100.00%",
                }])
                grp_m_final = pd.concat(
                    [grp_m_disp, fila_total], ignore_index=True
                )

                styled_df = grp_m_final.style.apply(
                    aplicar_criticidad, subset=["QUIEBRE %"]
                )
                st.dataframe(
                    styled_df, hide_index=True, use_container_width=True
                )
              else:
                st.info(
                    f"No hay quiebres registrados para {div_nombre} en la semana"
                    f" {fmt_sem(sem_top)}."
                )

        st.divider()

      # DETALLE DE REGISTRO CON FILTROS
      st.subheader("📋 Detalle de Registro de Compras")
      col_det_f1, col_det_f2 = st.columns(2)
      with col_det_f1:
        ocs_disponibles = (
            ["Todas"] + sorted([str(x) for x in df_filt[col_oc].dropna().unique()])
            if col_oc and col_oc in df_filt.columns
            else ["Todas"]
        )
        oc_seleccionada = st.selectbox(
            "Filtrar Detalle por OC:",
            ocs_disponibles,
            key=f"det_oc_{nombre_hoja}_{i}",
        )
      with col_det_f2:
        skus_det_disponibles = (
            ["Todos"]
            + sorted([str(x) for x in df_filt[col_sku].dropna().unique()])
            if col_sku and col_sku in df_filt.columns
            else ["Todos"]
        )
        sku_det_seleccionado = st.selectbox(
            "Filtrar Detalle por SKU:",
            skus_det_disponibles,
            key=f"det_sku_{nombre_hoja}_{i}",
        )

      df_detalle = df_filt.copy()
      if col_oc and oc_seleccionada != "Todas":
        df_detalle = df_detalle[
            df_detalle[col_oc].astype(str) == oc_seleccionada
        ]
      if col_sku and sku_det_seleccionado != "Todos":
        df_detalle = df_detalle[
            df_detalle[col_sku].astype(str) == sku_det_seleccionado
        ]

      if col_rechazado and col_rechazado in df_detalle.columns:
        idx_corte = list(df_detalle.columns).index(col_rechazado) + 1
        df_corte_final = df_detalle.iloc[:, :idx_corte].copy()
      else:
        df_corte_final = df_detalle.copy()

      renombrar_columnas = {
          "id_producto": "SKU",
          "id_prod": "SKU",
          "numero_orden": "OC",
          "num_oc": "OC",
          "orden_compra": "OC",
          "descripcion": "Descripción",
          "unidades_compra": "Unidades Compra",
          "unidades_recibidas": "Unidades Recibidas",
          "unidades_rechazadas": "Unidades Rechazadas",
          "cantidad": "Unidades Compra",
          "cantidad_recibida": "Unidades Recibidas",
          "fecha_hora_despacho_default": "Fecha Despacho",
          "precio_final": "Precio Final",
          "precio_total": "Precio Total",
      }

      nuevas_columnas = {}
      for col in df_corte_final.columns:
        col_lower = str(col).strip().lower()
        if col_lower in renombrar_columnas:
          nuevas_columnas[col] = renombrar_columnas[col_lower]
        else:
          nuevas_columnas[col] = str(col).replace("_", " ").strip().title()

      df_corte_final = df_corte_final.rename(columns=nuevas_columnas)

      st.dataframe(df_corte_final, hide_index=True, use_container_width=True)

    # =================================================================
    # PESTAÑA FILL RATE (múltiples tablas pegadas: Salcobrand Consumo,
    # Salcobrand Farma, Preunic, Terceros/Otros Canales)
    # =================================================================
    elif is_fill_rate:
      st.subheader("🔥 Fill Rate por Cadena (Top Quiebres)")

      try:
        df_raw_fr = cargar_hoja_raw(ruta_final, nombre_hoja)
      except Exception as e:
        st.error(f"No se pudo leer la hoja en formato bruto: {e}")
        df_raw_fr = None

      if df_raw_fr is not None:
        bloques_fr = parse_bloques_fill_rate(df_raw_fr)

        titulos_fallback = [
            "🏬 SALCOBRAND — CONSUMO MASIVO",
            "💊 SALCOBRAND — FARMA",
            "🏪 PREUNIC",
            "🌐 TERCEROS / OTROS CANALES",
        ]

        if not bloques_fr:
          st.info(
              "No se encontraron bloques de datos reconocibles en esta hoja."
          )

        def _fr_tabla_display(tabla):
          """Arma la tabla de detalle con el mismo estilo visual (columnas
          formateadas como texto) que 'TOP 15 Quiebres' en SB/PU."""
          col_sku_fr = next(
              (c for c in tabla.columns if "sku" in c.lower()), None
          )
          col_desc_fr = next(
              (c for c in tabla.columns if "descrip" in c.lower()), None
          )
          col_marca_fr = next(
              (c for c in tabla.columns if c.strip().lower() == "marca"), None
          )
          col_cliente_fr = next(
              (c for c in tabla.columns if c.strip().lower() == "cliente"),
              None,
          )
          col_cant_fr = next(
              (
                  c
                  for c in tabla.columns
                  if "suma de solicitado" in c.strip().lower()
              ),
              None,
          )
          col_monto_fr = next(
              (
                  c
                  for c in tabla.columns
                  if c.strip().lower().startswith("solicitado $")
              ),
              None,
          )
          col_quiebre_fr = next(
              (
                  c
                  for c in tabla.columns
                  if c.strip().lower().startswith("quiebre $")
              ),
              None,
          )
          col_fr_fr = next(
              (c for c in tabla.columns if c.strip().lower() == "fr"), None
          )
          col_estado_fr = next(
              (
                  c
                  for c in tabla.columns
                  if c.strip().lower() == "observacion"
              ),
              None,
          )

          disp = pd.DataFrame()
          if col_sku_fr:
            disp["SKU"] = tabla[col_sku_fr].astype(str)
          if col_desc_fr:
            disp["Descripción"] = tabla[col_desc_fr]
          if col_marca_fr:
            disp["Marca"] = tabla[col_marca_fr]
          if col_cliente_fr:
            disp["Cliente"] = tabla[col_cliente_fr]
          if col_cant_fr:
            disp["Unidades Solicitadas"] = tabla[col_cant_fr].apply(
                lambda x: formato_unidades(_fr_num(x) or 0)
            )
          if col_monto_fr:
            disp["Solicitado ($)"] = tabla[col_monto_fr].apply(
                lambda x: formato_moneda(_fr_num(x) or 0)
            )
          if col_quiebre_fr:
            disp["Quiebre ($)"] = tabla[col_quiebre_fr].apply(
                lambda x: (
                    f"-{formato_moneda(abs(_fr_num(x)))}"
                    if (_fr_num(x) or 0) > 0
                    else "$0"
                )
            )
          if col_fr_fr:
            disp["FR"] = tabla[col_fr_fr].apply(
                lambda x: f"{(_fr_num(x) or 0) * 100:.1f}%"
            )
          if col_estado_fr:
            disp["Comentario"] = tabla[col_estado_fr]

          return disp, tabla.columns.tolist()

        for idx_b, bloque in enumerate(bloques_fr):
          titulo_mostrar = (
              titulos_fallback[idx_b]
              if idx_b < len(titulos_fallback)
              else (bloque["titulo"] or f"BLOQUE {idx_b + 1}")
          )
          n_filas_tabla = len(bloque["tabla"])
          kt = bloque["kpi_total"]
          kp = bloque["kpi_top"]

          try:
            sem_txt = (
                f"Sem {int(float(bloque['semana']))}"
                if bloque["semana"] not in (None, "")
                else ""
            )
          except (TypeError, ValueError):
            sem_txt = ""

          st.markdown(f"#### 📌 {titulo_mostrar}")

          if kt["monto"] is not None:
            st.caption(
                f"Solicitado: {formato_moneda(kt['monto'])} · "
                f"{formato_unidades(kt['cantidad'] or 0)} unidades"
            )

          m_ind1, m_ind2 = st.columns(2)
          with m_ind1:
            fr_total_pct = (kt["fr"] * 100) if kt["fr"] is not None else 0.0
            delta_total = (
                f"{kt['quiebre']:,.0f} $ (Quiebre)".replace(",", ".")
                if kt["quiebre"] is not None
                else None
            )
            st.metric(
                label=(
                    f"Fill Rate Total ({sem_txt})"
                    if sem_txt
                    else "Fill Rate Total"
                ),
                value=f"{fr_total_pct:.1f}%",
                delta=delta_total,
            )
          with m_ind2:
            fr_top_pct = (kp["fr"] * 100) if kp["fr"] is not None else 0.0
            delta_top = (
                f"{kp['quiebre']:,.0f} $ (Quiebre Top {n_filas_tabla})".replace(
                    ",", "."
                )
                if kp["quiebre"] is not None
                else (
                    f"{kp['monto']:,.0f} $ (Quiebre Top {n_filas_tabla})".replace(
                        ",", "."
                    )
                    if kp["monto"] is not None
                    else None
                )
            )
            st.metric(
                label=f"% Incidencia s/Monto Total (Top {n_filas_tabla})",
                value=f"{fr_top_pct:.1f}%",
                delta=delta_top,
            )

          # Tabla de detalle, con el mismo look & feel que "TOP 15 Quiebres"
          # de SB/PU: columnas clave, ya formateadas, siempre visibles.
          tabla_disp, columnas_originales = _fr_tabla_display(bloque["tabla"])
          if not tabla_disp.empty:
            st.dataframe(
                tabla_disp, hide_index=True, use_container_width=True
            )
            with st.expander(
                "Ver todas las columnas (detalle completo de la hoja)",
                expanded=False,
            ):
              st.dataframe(
                  bloque["tabla"], hide_index=True, use_container_width=True
              )
          else:
            st.info("No hay productos en este bloque para la semana actual.")

          st.divider()

    else:
      busqueda = st.text_input(
          f"🔍 Buscar en {nombre_hoja}:", key=f"search_{nombre_hoja}_{i}"
      )
      if busqueda:
        mask = (
            df.astype(str)
            .apply(lambda x: x.str.contains(busqueda, case=False))
            .any(axis=1)
        )
        df = df[mask]
      st.caption(f"Mostrando {len(df)} registros en {nombre_hoja}.")
      st.dataframe(df, hide_index=True, use_container_width=True)


# =================================================================
# PESTAÑA: ESCANEAR POSICIÓN (LOCALIZADOR) - código de barras 1D
# =================================================================
with tabs[-1]:
  st.markdown("### 📷 Escanear Localizador")
  st.caption("Apunta la cámara al código de barras de la posición (Localizador).")

  components.html(
      """
      <div style="position:relative; width:100%; max-height:280px; overflow:hidden;
                  border-radius:8px; background:#000;">
        <video id="video" style="width:100%; max-height:280px; object-fit:cover;
               display:block;" muted playsinline autoplay></video>
        <!-- Recuadro guía puramente visual: ZXing analiza todo el
             fotograma, este marco solo ayuda a encuadrar el código. -->
        <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                    width:82%; height:90px; border:3px solid #00e676; border-radius:6px;
                    box-shadow:0 0 0 2000px rgba(0,0,0,0.35); pointer-events:none;"></div>
      </div>
      <div style="text-align:center; margin-top:10px;">
        <button id="btn-torch" style="background:#0070f3; color:#fff; border:none;
                border-radius:8px; padding:8px 16px; font-weight:600; cursor:pointer;">
          💡 Linterna
        </button>
      </div>
      <p id="estado-scan" style="color:#888; font-size:13px; text-align:center; margin-top:6px;">
        Cargando lector...
      </p>
      <script src="https://unpkg.com/@zxing/library@0.21.3/umd/index.min.js"></script>
      <script>
        const estado = document.getElementById("estado-scan");

        // Si la librería no llegó a cargar (CDN caído, red lenta, etc.),
        // avisamos en pantalla en vez de quedar pegados en silencio.
        setTimeout(function () {
          if (typeof ZXing === "undefined") {
            estado.textContent = "❌ No se pudo cargar el lector de códigos (revisa tu conexión y recarga).";
          }
        }, 6000);

        if (typeof ZXing !== "undefined") {
          const { BrowserMultiFormatReader, DecodeHintType, BarcodeFormat } = ZXing;

          const hints = new Map();
          // Solo CODE_128: es el formato real de la etiqueta de Localizador.
          // Tener EAN_13/UPC_A/ITF activos al mismo tiempo hacía que ZXing
          // a veces malinterpretara las barras de un Code128 como si fueran
          // un EAN-13 (falso positivo numérico tipo "9631187073887").
          hints.set(DecodeHintType.POSSIBLE_FORMATS, [
            BarcodeFormat.CODE_128,
            BarcodeFormat.CODE_39,
            BarcodeFormat.CODABAR,
          ]);
          hints.set(DecodeHintType.TRY_HARDER, true);

          const codeReader = new BrowserMultiFormatReader(hints);
          let yaEnvio = false;

          // Un Localizador siempre tiene letras y puntos (ej: MCD.0.3.G.2.120).
          // Si lo leído no calza con ese patrón, es casi seguro una lectura
          // errónea (p.ej. un EAN-13 solo numérico) y seguimos escaneando
          // en vez de aceptarlo.
          function esLocalizadorValido(texto) {
            return /^[A-Za-z0-9]+(\\.[A-Za-z0-9]+){2,}$/.test(texto.trim());
          }

          const constraints = {
            video: {
              facingMode: "environment",
              width: { ideal: 1280 },
              height: { ideal: 720 },
            },
          };

          estado.textContent = "🎥 Solicitando acceso a la cámara...";

          codeReader
            .decodeFromConstraints(constraints, "video", (result, err) => {
              if (result && !yaEnvio) {
                const texto = result.getText();
                if (!esLocalizadorValido(texto)) {
                  // Lectura sospechosa (no tiene forma de Localizador):
                  // la ignoramos y seguimos escaneando en vez de aceptarla.
                  estado.textContent = "⚠️ Código no válido, sigue escaneando: " + texto;
                  return;
                }
                yaEnvio = true;
                estado.textContent = "✅ Código detectado: " + texto;
                const url = new URL(window.parent.location);
                url.searchParams.set("loc", texto);
                window.parent.location.href = url.toString();
              }
            })
            .then((controls) => {
              estado.textContent = "📷 Buscando código...";
              document.getElementById("btn-torch").onclick = function () {
                try {
                  const track = document
                    .getElementById("video")
                    .srcObject.getVideoTracks()[0];
                  const settings = track.getSettings();
                  track
                    .applyConstraints({ advanced: [{ torch: !settings.torch }] })
                    .catch(() => alert("Este dispositivo no permite linterna desde el navegador."));
                } catch (e) {
                  alert("No se pudo acceder a la linterna.");
                }
              };
            })
            .catch((err) => {
              estado.textContent = "❌ No se pudo acceder a la cámara: " + err;
            });
        }
      </script>
      """,
      height=400,
  )


  st.caption(
      "💡 Tip: si tiene 2 códigos en la misma etiqueta, tapa el de arriba con"
      " el dedo y deja solo visible el de abajo (el del Localizador). Mantén"
      " el celular firme y a unos 10-15 cm del código."
  )

  with st.expander("⌨️ ¿No lee el código? Ingresa el Localizador manualmente", expanded=True):
    loc_manual = st.text_input(
        "Localizador (ej: MCD.0.3.C.2.013):", key="loc_manual_input"
    )
    buscar_click = st.button("Buscar", key="btn_buscar_manual")

  # Resuelve el Localizador a usar en esta misma ejecución: prioriza el
  # ingreso manual recién enviado; si no, usa el que venga de la cámara
  # (parámetro de URL). Evita depender de un segundo round-trip de rerun.
  loc_query = st.query_params.get("loc", None)
  loc_escaneado = None
  if buscar_click and loc_manual.strip():
    loc_escaneado = loc_manual.strip()
    st.query_params["loc"] = loc_escaneado
  elif loc_query:
    loc_escaneado = loc_query

  if st.button("🔄 Limpiar escaneo", key="btn_limpiar_scan"):
    st.query_params.clear()
    st.rerun()

  if loc_escaneado:
    df_stock_scan = hojas.get("STOCK")
    if df_stock_scan is None:
      st.error("No se encontró la hoja 'STOCK' en el Excel.")
    else:
      df_stock_scan = df_stock_scan.copy()

      col_loc_scan = next(
          (c for c in df_stock_scan.columns
           if c.strip().lower() in ["localizador", "ubicacion"]),
          None,
      )
      col_cod_scan = next(
          (c for c in df_stock_scan.columns
           if c.strip().lower() in ["codigo_articulo", "id_producto", "sku", "codigo"]),
          None,
      )
      col_desc_scan = next(
          (c for c in df_stock_scan.columns if "descripcion" in c.lower()), None
      )
      if not col_desc_scan and len(df_stock_scan.columns) > 3:
        col_desc_scan = df_stock_scan.columns[3]
      col_lote_scan = next(
          (c for c in df_stock_scan.columns if c.strip().lower() == "lote_proveedor"),
          None,
      )
      col_cant_scan = next(
          (c for c in df_stock_scan.columns
           if c.strip().lower() in ["cantidad", "stock", "unidades"]),
          None,
      )
      col_fecha_scan = next(
          (c for c in df_stock_scan.columns
           if c.strip().lower() in ["fecha_expiracion_lote", "vencimiento", "fecha_expiracion"]),
          None,
      )

      if not col_loc_scan:
        st.error("La hoja STOCK no tiene columna de Localizador reconocible.")
      else:
        resultado = df_stock_scan[
            df_stock_scan[col_loc_scan].astype(str).str.strip().str.upper()
            == str(loc_escaneado).strip().upper()
        ].copy()

        st.success(f"📍 Localizador escaneado: **{loc_escaneado}**")

        if resultado.empty:
          st.warning("No se encontró ningún producto registrado en esa posición.")
        else:
          if col_cant_scan:
            resultado[col_cant_scan] = resultado[col_cant_scan].apply(limpiar_numero)
          if col_cod_scan:
            resultado[col_cod_scan] = resultado[col_cod_scan].apply(fmt_code)
          if col_fecha_scan:
            resultado[col_fecha_scan] = pd.to_datetime(
                resultado[col_fecha_scan], errors="coerce"
            ).dt.strftime("%d-%m-%Y")

          for _, fila in resultado.iterrows():
            desc_txt = fila[col_desc_scan] if col_desc_scan else "Sin descripción"
            cod_txt = fila[col_cod_scan] if col_cod_scan else "S/N"
            cant_txt = (
                formato_unidades(fila[col_cant_scan]) if col_cant_scan else "N/A"
            )
            lote_txt = fila[col_lote_scan] if col_lote_scan else "N/A"
            fecha_txt = fila[col_fecha_scan] if col_fecha_scan else "N/A"

            st.markdown(
                f"""
                <div style="background-color:#141414; border:1px solid #0070f3;
                            border-radius:10px; padding:16px; margin-bottom:12px;">
                    <div style="color:#aaaaaa; font-size:12px; text-transform:uppercase;">Producto</div>
                    <div style="color:#ffffff; font-size:20px; font-weight:bold;">{desc_txt}</div>
                    <div style="margin-top:8px; color:#cccccc; font-size:14px;">
                        Código: <b>{cod_txt}</b> · Lote: <b>{lote_txt}</b> · Vence: <b>{fecha_txt}</b>
                    </div>
                    <div style="margin-top:8px; color:#2ecc71; font-size:22px; font-weight:bold;">
                        Stock: {cant_txt} unidades
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
  else:
    st.info("Aún no se ha escaneado ningún código.")
