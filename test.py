import hashlib
import pandas as pd

# ── [1.1] Carga directa desde GitHub (sin credenciales) ─────────────────────
# URLs públicas — funcionan en Colab y localmente sin login
BASE = "https://raw.githubusercontent.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist/master/files"

print("Cargando tablas desde GitHub...")
df_orders      = pd.read_csv(f"{BASE}/olist_orders_dataset.csv")
df_order_items = pd.read_csv(f"{BASE}/olist_order_items_dataset.csv")
df_payments    = pd.read_csv(f"{BASE}/olist_order_payments_dataset.csv")
df_reviews     = pd.read_csv(f"{BASE}/olist_order_reviews_dataset.csv")
df_customers   = pd.read_csv(f"{BASE}/olist_customers_dataset.csv")
df_products    = pd.read_csv(f"{BASE}/olist_products_dataset.csv")
df_sellers     = pd.read_csv(f"{BASE}/olist_sellers_dataset.csv")
df_translation = pd.read_csv(f"{BASE}/product_category_name_translation.csv")

# ── Agregaciones previas al merge ─────────────────────────────────────────────
# Un pedido puede tener múltiples ítems: se agrupa a nivel de order_id
items_agg = df_order_items.groupby("order_id").agg(
    price_total   = ("price",         "sum"),
    freight_total = ("freight_value", "sum"),
    num_items     = ("order_item_id", "count"),
    product_id    = ("product_id",    "first"),
).reset_index()

# Un pedido puede tener múltiples pagos (cuotas): se toma el tipo principal
payments_agg = df_payments.groupby("order_id").agg(
    payment_type         = ("payment_type",         "first"),
    payment_value        = ("payment_value",         "sum"),
    payment_installments = ("payment_installments",  "max"),
).reset_index()

# Se conserva solo la primera reseña por pedido
reviews_agg = df_reviews.groupby("order_id").agg(
    review_score = ("review_score", "first"),
).reset_index()

# Traducción de categorías al inglés
products_tr = df_products.merge(df_translation, on="product_category_name", how="left")

# ── Merge principal ───────────────────────────────────────────────────────────
df = (
    df_orders
    .merge(df_customers[["customer_id", "customer_state", "customer_city"]],
           on="customer_id", how="left")
    .merge(items_agg,
           on="order_id", how="left")
    .merge(products_tr[["product_id", "product_category_name",
                         "product_category_name_english", "product_weight_g"]],
           on="product_id", how="left")
    .merge(payments_agg, on="order_id", how="left")
    .merge(reviews_agg,  on="order_id", how="left")
)

# ── [1.2] Inspección del DataFrame ───────────────────────────────────────────
print("\n── head() ──────────────────────────────────────────────────────────────")
print(df.head())
print("\n── shape ───────────────────────────────────────────────────────────────")
print(df.shape)
print("\n── info() ──────────────────────────────────────────────────────────────")
df.info()

# ── [1.3] Huella reproducible del DataFrame ───────────────────────────────────
def calcular_fingerprint_dataframe(dataframe: pd.DataFrame) -> str:
    """
    Retorna una huella SHA-256 reproducible del contenido de un DataFrame.

    Usa pd.util.hash_pandas_object() para generar un hash por fila y
    hashlib.sha256() para combinarlos en un único string hexadecimal.

    Args:
        dataframe: DataFrame de Pandas a hashear.
    Returns:
        String hexadecimal de 64 caracteres (SHA-256).
    """
    row_hashes = pd.util.hash_pandas_object(dataframe, index=True)
    return hashlib.sha256(row_hashes.values.tobytes()).hexdigest()

fingerprint = calcular_fingerprint_dataframe(df)
print(f"\n── fingerprint ─────────────────────────────────────────────────────────")
print(fingerprint)


## Usamos assert para validar que el fingerprint es reproducible y sensible a cambios
assert calcular_fingerprint_dataframe(df) == calcular_fingerprint_dataframe(df), \
    "El fingerprint no es determinista"
assert calcular_fingerprint_dataframe(df) != calcular_fingerprint_dataframe(df.iloc[:100]), \
    "DataFrames distintos no deben producir el mismo hash"

# ── [1.4] Metadata del dataset ────────────────────────────────────────────────
dataset_info = {
    "nombre_dataset":             "Brazilian E-Commerce Public Dataset by Olist",
    "fuente_url":                 "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
    "institucion_fuente":         "Olist — marketplace de e-commerce brasileño",
    "fecha_descarga":             "2026-06-08",
    "descripcion_breve":          (
        "Dataset real de ~100.000 pedidos realizados en el marketplace Olist "
        "entre 2016 y 2018. Incluye información de pedidos, productos, clientes, "
        "vendedores, pagos y reseñas distribuidos en 8 tablas relacionadas."
    ),
    "licencia_o_condiciones_uso": "CC BY-NC-SA 4.0",
}

print("\n── dataset_info ────────────────────────────────────────────────────────")
for k, v in dataset_info.items():
    print(f"  {k}: {v}")

# ── Validaciones finales ──────────────────────────────────────────────────────
assert df.shape[0] >= 99_000, f"Se esperaban ≥99.000 filas, se obtuvieron {df.shape[0]}"
assert df.shape[1] >= 10,     f"Se esperaban ≥10 columnas, se obtuvieron {df.shape[1]}"
assert all(v for v in dataset_info.values()), "dataset_info tiene campos vacíos"
print("\n✓ Todas las validaciones pasaron")

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 2 — Diccionario de datos y estructuras básicas de Python
# ═══════════════════════════════════════════════════════════════════════════════

# ── [2.1] Lista de columnas seleccionadas para el análisis ────────────────────
columnas_analisis = [
    "order_purchase_timestamp",       # temporal
    "order_delivered_customer_date",  # temporal
    "order_estimated_delivery_date",  # temporal
    "customer_state",                 # geográfica
    "price_total",                    # numérica
    "freight_total",                  # numérica
    "payment_value",                  # numérica
    "payment_installments",           # numérica
    "review_score",                   # numérica
    "product_weight_g",               # numérica
    "order_status",                   # categórica
    "product_category_name_english",  # categórica
    "payment_type",                   # categórica
]

assert isinstance(columnas_analisis, list), "columnas_analisis debe ser una lista"
assert len(columnas_analisis) >= 10, "Se necesitan al menos 10 columnas"
assert all(c in df.columns for c in columnas_analisis), "Hay columnas que no existen en el DataFrame"

# ── [2.2] Diccionario de datos ────────────────────────────────────────────────
diccionario_datos = {
    "order_purchase_timestamp": {
        "tipo_conceptual": "temporal",
        "rol_analitico":   "variable de segmentación temporal — permite analizar estacionalidad y tendencias de compra",
        "descripcion":     "Fecha y hora en que el cliente realizó el pedido en el marketplace Olist",
        "posibles_problemas": ["formato string, requiere conversión a datetime", "posibles registros fuera del rango 2016-2018"],
    },
    "order_delivered_customer_date": {
        "tipo_conceptual": "temporal",
        "rol_analitico":   "variable para calcular tiempo real de entrega",
        "descripcion":     "Fecha en que el pedido fue efectivamente entregado al cliente",
        "posibles_problemas": ["2.965 nulos — pedidos cancelados o aún no entregados al momento del corte", "no puede usarse sin imputación o filtrado previo"],
    },
    "order_estimated_delivery_date": {
        "tipo_conceptual": "temporal",
        "rol_analitico":   "benchmark para medir cumplimiento de plazos de entrega",
        "descripcion":     "Fecha estimada de entrega prometida al cliente al momento de la compra",
        "posibles_problemas": ["sin nulos, pero puede diferir significativamente de la entrega real"],
    },
    "customer_state": {
        "tipo_conceptual": "geografica",
        "rol_analitico":   "variable de segmentación geográfica — permite comparar comportamiento por región de Brasil",
        "descripcion":     "Estado brasileño (UF) donde reside el cliente que realizó el pedido",
        "posibles_problemas": ["27 estados con distribución muy desigual — SP concentra ~40% de los pedidos"],
    },
    "price_total": {
        "tipo_conceptual": "numerica",
        "rol_analitico":   "variable de respuesta principal — monto pagado por el pedido (sin flete)",
        "descripcion":     "Suma del precio de todos los ítems del pedido en BRL",
        "posibles_problemas": ["775 nulos — pedidos sin ítems asociados", "distribución con cola larga derecha, presencia de outliers"],
    },
    "freight_total": {
        "tipo_conceptual": "numerica",
        "rol_analitico":   "variable para analizar costo logístico relativo al precio",
        "descripcion":     "Suma del costo de flete de todos los ítems del pedido en BRL",
        "posibles_problemas": ["775 nulos — misma causa que price_total", "valores muy altos en regiones remotas de Brasil"],
    },
    "payment_value": {
        "tipo_conceptual": "numerica",
        "rol_analitico":   "monto total cobrado al cliente incluyendo cuotas",
        "descripcion":     "Valor total pagado por el cliente, sumando todos los pagos del pedido",
        "posibles_problemas": ["1 nulo", "puede diferir de price_total + freight_total por redondeos en cuotas"],
    },
    "payment_installments": {
        "tipo_conceptual": "numerica",
        "rol_analitico":   "indicador de comportamiento financiero del comprador",
        "descripcion":     "Número máximo de cuotas elegido por el cliente para el pago",
        "posibles_problemas": ["1 nulo", "valor 0 en pagos con boleto (pago único sin cuotas)"],
    },
    "review_score": {
        "tipo_conceptual": "numerica",
        "rol_analitico":   "variable de satisfacción del cliente — variable dependiente central del análisis",
        "descripcion":     "Calificación otorgada por el cliente al pedido, de 1 (muy malo) a 5 (excelente)",
        "posibles_problemas": ["768 nulos en versión original, sin nulos en este merge", "escala ordinal tratada como numérica"],
    },
    "product_weight_g": {
        "tipo_conceptual": "numerica",
        "rol_analitico":   "proxy del tamaño/tipo de producto, relacionado con el costo de flete",
        "descripcion":     "Peso en gramos del primer producto del pedido",
        "posibles_problemas": ["791 nulos — productos sin peso registrado en el catálogo", "solo representa el primer ítem en pedidos con múltiples productos"],
    },
    "order_status": {
        "tipo_conceptual": "categorica",
        "rol_analitico":   "filtro de calidad — permite aislar pedidos entregados de cancelados o en tránsito",
        "descripcion":     "Estado del pedido: delivered, shipped, canceled, invoiced, processing, approved, unavailable, created",
        "posibles_problemas": ["distribución muy desigual — >95% son 'delivered'", "estados intermedios representan <5% del dataset"],
    },
    "product_category_name_english": {
        "tipo_conceptual": "categorica",
        "rol_analitico":   "variable de segmentación por tipo de producto",
        "descripcion":     "Nombre de la categoría del producto en inglés (traducido desde el portugués)",
        "posibles_problemas": ["2.212 nulos — productos sin categoría registrada o sin traducción disponible", "73 categorías distintas con frecuencias muy heterogéneas"],
    },
    "payment_type": {
        "tipo_conceptual": "categorica",
        "rol_analitico":   "variable de comportamiento de pago del cliente",
        "descripcion":     "Método de pago utilizado: credit_card, boleto, voucher, debit_card",
        "posibles_problemas": ["1 nulo", "credit_card representa ~75% de los pagos"],
    },
}

assert len(diccionario_datos) >= 10, "El diccionario debe tener al menos 10 columnas"
assert all(c in diccionario_datos for c in columnas_analisis), "Hay columnas sin documentar"
assert all(
    all(k in v for k in ["tipo_conceptual", "rol_analitico", "descripcion", "posibles_problemas"])
    for v in diccionario_datos.values()
), "Alguna columna tiene campos incompletos"
assert all(
    isinstance(v["posibles_problemas"], list)
    for v in diccionario_datos.values()
), "posibles_problemas debe ser una lista en todas las columnas"

cols_con_problemas = [c for c, v in diccionario_datos.items() if len(v["posibles_problemas"]) > 0]
assert len(cols_con_problemas) >= 3, "Al menos 3 columnas deben tener posibles_problemas no vacíos"

# ── [2.3] Resumen textual con f-strings ───────────────────────────────────────
tipos = {}
for v in diccionario_datos.values():
    t = v["tipo_conceptual"]
    tipos[t] = tipos.get(t, 0) + 1

resumen = (
    f"El dataset Olist contiene {df.shape[0]:,} pedidos y {df.shape[1]} columnas en total.\n"
    f"Para este análisis se seleccionaron {len(columnas_analisis)} columnas: "
    f"{tipos.get('numerica', 0)} numéricas, {tipos.get('categorica', 0)} categóricas, "
    f"{tipos.get('temporal', 0)} temporales y {tipos.get('geografica', 0)} geográficas.\n"
    f"El periodo cubierto va de 2016 a 2018, con un review_score promedio de "
    f"{df['review_score'].mean():.2f} sobre 5 puntos.\n"
    f"Se detectaron columnas con posibles problemas de calidad: "
    f"{', '.join(cols_con_problemas[:3])} (entre otras)."
)

print("\n── resumen ─────────────────────────────────────────────────────────────")
print(resumen)

# ── [2.4] Variables centrales para la pregunta analítica ──────────────────────
# Pregunta: ¿Cómo varían el precio, el tiempo de entrega y la satisfacción del
# cliente según la categoría de producto y el estado geográfico, y qué patrones
# temporales permiten recomendar mejoras operacionales al marketplace?

variables_centrales = {
    "review_score": (
        "Tipo: numérica. Es la variable dependiente principal del análisis: mide "
        "directamente la satisfacción del cliente. Permite comparar si distintas "
        "categorías de producto o regiones geográficas generan mejores o peores experiencias."
    ),
    "price_total": (
        "Tipo: numérica. Representa el valor económico del pedido. Es clave para "
        "segmentar el análisis por rango de precio y detectar si el monto comprado "
        "se asocia con mayor o menor satisfacción."
    ),
    "order_purchase_timestamp": (
        "Tipo: temporal. Permite identificar patrones estacionales (días de la semana, "
        "meses, festividades) en el volumen de compras y la satisfacción. Es esencial "
        "para la dimensión temporal de la pregunta analítica."
    ),
    "customer_state": (
        "Tipo: geográfica. Permite segmentar todos los indicadores por región de Brasil. "
        "Las diferencias logísticas entre estados (distancia, infraestructura) afectan "
        "directamente el tiempo de entrega y la satisfacción del cliente."
    ),
}

assert 2 <= len(variables_centrales) <= 4, "Deben identificarse entre 2 y 4 variables centrales"
assert any(
    diccionario_datos[v]["tipo_conceptual"] in ("temporal", "geografica")
    for v in variables_centrales
), "Al menos una variable central debe ser temporal o geográfica"

print("\n── variables centrales ─────────────────────────────────────────────────")
for nombre, justificacion in variables_centrales.items():
    print(f"\n  {nombre}:\n    {justificacion}")

print("\n✓ Parte 2 completada")
