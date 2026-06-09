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
