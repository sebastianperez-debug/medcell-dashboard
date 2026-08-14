# --- REEMPLAZAR ESTE BLOQUE EN TU CÓDIGO ---

# PROCESAR HOJAS CON ESTRUCTURA OPERACIONAL (SB Y PU)
if nombre_hoja.strip().upper() in ["SB", "PU"]:
    # Detección flexible de columnas adaptada tanto a SB como a PU
    col_semana = next((c for c in df.columns if c.strip().lower() in ['semana', 'sem', 'wk', 'week']), None) or \
                 next((c for c in df.columns if 'semana' in c.lower() or 'sem' in c.lower()), None)
    
    col_sku = next((c for c in df.columns if c.strip().lower() in ['sku', 'cod_sku', 'codigo_sku', 'codigo', 'cod_prod', 'material']), None) or \
              next((c for c in df.columns if 'sku' in c.lower() or 'cod' in c.lower()), None)
    
    col_oc = next((c for c in df.columns if c.strip().lower() in ['oc', 'orden_compra', 'orden de compra', 'num_oc', 'numero_oc', 'orden']), None) or \
             next((c for c in df.columns if 'oc' in c.lower() or 'orden' in c.lower()), None)
    
    col_desc = next((c for c in df.columns if c.strip().lower() in ['descripcion', 'desc_producto', 'producto', 'desc', 'nombre']), None) or \
               next((c for c in df.columns if 'desc' in c.lower() or 'nombre' in c.lower() or 'prod' in c.lower()), col_sku)
    
    col_div = next((c for c in df.columns if c.strip().lower() in ['division', 'categoría', 'categoria', 'linea', 'div', 'cat']), None) or \
              next((c for c in df.columns if 'divis' in c.lower() or 'categ' in c.lower() or 'linea' in c.lower()), None)
    
    # Columna Marca / Proveedor
    col_marca = next((c for c in df.columns if c.strip().lower() in ['marca', 'brand', 'lab', 'laboratorio', 'proveedor']), None) or \
                next((c for c in df.columns if any(k in c.lower() for k in ['marca', 'brand', 'lab', 'proveedor'])), None)

    # Columna Unidades Compra / Solicitadas
    col_u_compra = next((c for c in df.columns if c.strip().lower() in ['unidades_compra', 'unidades_pedidas', 'unid_pedidas', 'cant_pedida', 'cantidad_pedida', 'unidades_solicitadas', 'cant_solic', 'cantidad', 'unidades', 'solicitado', 'cant']), None) or \
                   next((c for c in df.columns if any(k in c.lower() for k in ['comp', 'pedi', 'solic', 'cant', 'unid'])), None)
    
    # Columna Unidades Recibidas / Entregadas
    col_u_recib = next((c for c in df.columns if c.strip().lower() in ['unidades_recibidas', 'unid_recibidas', 'cant_recibida', 'cantidad_recibida', 'unidades_entregadas', 'unid_entregadas', 'cant_entregada', 'recibido', 'entregado']), None) or \
                  next((c for c in df.columns if any(k in c.lower() for k in ['recib', 'entre', 'despa'])), None)

    # Columna Monto Compra
    col_m_compra = next((c for c in df.columns if c.lower().strip() in ['compra total', 'monto_compra', 'monto compra', 'total_compra', 'costo_total', 'monto_pedido', 'val_compra', 'valor_compra', 'monto_solicitado']), None) or \
                   next((c for c in df.columns if any(k in c.lower() for k in ['monto', 'val', 'cost', 'total', '$']) and any(k in c.lower() for k in ['comp', 'pedi', 'solic'])), None)

    # Columna Monto Recibido
    col_m_recib = next((c for c in df.columns if c.lower().strip() in ['recibidas', 'monto_recibido', 'monto recibido', 'total_recibido', 'monto_facturado', 'monto_entregado', 'val_recibido', 'valor_recibido']), None) or \
                  next((c for c in df.columns if any(k in c.lower() for k in ['recib', 'fact', 'entre']) and any(k in c.lower() for k in ['monto', 'val', 'cost', 'total', '$'])), None)

    col_precio = next((c for c in df.columns if any(k in c.lower() for k in ['precio', 'costo_unitario', 'p_unitario', 'precio_costo', 'puc'])), None)
    col_quiebre = next((c for c in df.columns if 'quiebre' in c.lower() or 'monto_falta' in c.lower()), None)
    col_rechazado = next((c for c in df.columns if 'rechaz' in c.lower() or 'devuel' in c.lower()), None)

    # --- GARANTIZAR COLUMNAS PARA EVITAR KEYERROR ---
    if not col_u_compra or col_u_compra not in df.columns:
        df["unidades_compra_calc"] = 0
        col_u_compra = "unidades_compra_calc"
        
    if not col_u_recib or col_u_recib not in df.columns:
        df["unidades_recibidas_calc"] = 0
        col_u_recib = "unidades_recibidas_calc"

    if not col_precio or col_precio not in df.columns:
        df["precio_calc"] = 0
        col_precio = "precio_calc"

    # Conversión numérica segura
    cols_a_num = [c for c in [col_u_compra, col_u_recib, col_m_compra, col_m_recib, col_precio, col_quiebre, col_rechazado] if c and c in df.columns]
    for c_num in cols_a_num:
        df[c_num] = pd.to_numeric(df[c_num], errors='coerce').fillna(0)

    # Reconstrucción de montos calculados
    if not col_m_compra or col_m_compra not in df.columns:
        df["monto_compra_calc"] = df[col_u_compra] * df[col_precio]
        col_m_compra = "monto_compra_calc"

    if not col_m_recib or col_m_recib not in df.columns:
        if col_precio in df.columns and (df[col_precio] > 0).any():
            df["monto_recibido_calc"] = df[col_u_recib] * df[col_precio]
        else:
            precio_linea = (df[col_m_compra] / df[col_u_compra].replace(0, 1)).fillna(0)
            df["monto_recibido_calc"] = df[col_u_recib] * precio_linea
        col_m_recib = "monto_recibido_calc"

    if col_quiebre and col_quiebre in df.columns:
        df["quiebre_monto_calc"] = df[col_quiebre].abs()
    else:
        df["quiebre_monto_calc"] = (df[col_m_compra] - df[col_m_recib]).clip(lower=0)
        
    df["quiebre_unid_calc"] = (df[col_u_compra] - df[col_u_recib]).clip(lower=0)
