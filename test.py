import pandas as pd

BASE = "https://raw.githubusercontent.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist/master/files"

df_orders       = pd.read_csv(f"{BASE}/olist_orders_dataset.csv")
df_order_items  = pd.read_csv(f"{BASE}/olist_order_items_dataset.csv")
df_payments     = pd.read_csv(f"{BASE}/olist_order_payments_dataset.csv")
df_reviews      = pd.read_csv(f"{BASE}/olist_order_reviews_dataset.csv")
df_customers    = pd.read_csv(f"{BASE}/olist_customers_dataset.csv")
df_products     = pd.read_csv(f"{BASE}/olist_products_dataset.csv")
df_sellers      = pd.read_csv(f"{BASE}/olist_sellers_dataset.csv")
df_geo          = pd.read_csv(f"{BASE}/olist_geolocation_dataset.csv")
df_translation  = pd.read_csv(f"{BASE}/product_category_name_translation.csv")