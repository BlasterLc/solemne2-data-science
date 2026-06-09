import pandas as pd

# =====================================================================
# PUNTO 3: COMPARACIÓN DE 3 DATASETS CANDIDATOS
# =====================================================================
print("=== PUNTO 3: COMPARACIÓN DE DATASETS CANDIDATOS ===\n")

# Creamos un diccionario con la información de los 3 datasets
datos_comparacion = {
    "Criterio": [
        "Nombre",
        "Volumen (Filas)",
        "Estructura de Datos",
        "Variables Temporales / Geo",
        "Ventaja Principal",
        "Motivo de la Decisión"
    ],
    "Candidato 1 (Seleccionado)": [
        "Brazilian E-Commerce (Olist)",
        "> 99,000 pedidos",
        "Relacional (9 tablas interconectadas)",
        "Fechas exactas (horas) y regiones de Brasil",
        "Alta complejidad técnica; permite cruzar logística, pagos y geografía",
        "ELEGIDO. Su estructura imita entornos reales y permite análisis multivariado profundo."
    ],
    "Candidato 2 (Descartado)": [
        "Customer Shopping Dataset",
        "~ 99,000 registros",
        "Tabla plana única",
        "Solo fechas básicas, sin horas",
        "Datos limpios y listos para usar sin necesidad de hacer merges",
        "DESCARTADO. Demasiado simple; no presenta desafíos en la preparación de datos."
    ],
    "Candidato 3 (Descartado)": [
        "Retail Sales Data",
        "Variable",
        "Tabla plana única",
        "Tendencias estacionales genéricas",
        "Bueno para análisis de series de tiempo básico",
        "DESCARTADO. Variables limitadas que restringen las preguntas analíticas complejas."
    ]
}

# Convertimos a DataFrame para una visualización elegante
df_comparacion = pd.DataFrame(datos_comparacion)

# Mostramos la tabla en formato Markdown (ideal para copiar a tu informe)
print(df_comparacion.to_string(index=False))
print("\n" + "="*70 + "\n")


# =====================================================================
# PUNTO 4: DICCIONARIO DE DATOS (GENERACIÓN AUTOMÁTICA)
# =====================================================================
print("=== PUNTO 4: DICCIONARIO DE DATOS DEL DATASET MAESTRO ===\n")

# Función para simular o realizar la carga real de los datos de Olist
def obtener_dataset_maestro():
    """
    Intenta cargar los CSVs reales de Olist y unirlos. 
    Si los archivos aún no están en tu carpeta, genera un DataFrame 
    de prueba con la estructura exacta para que puedas avanzar.
    """
    try:
        # Si ya tienes los CSV descargados en la misma carpeta, este código los unirá:
        orders = pd.read_csv("olist_orders_dataset.csv")
        customers = pd.read_csv("olist_customers_dataset.csv")
        payments = pd.read_csv("olist_order_payments_dataset.csv")
        
        # Unimos pedidos con clientes y luego con pagos
        df_master = orders.merge(customers, on='customer_id', how='inner')
        df_master = df_master.merge(payments, on='order_id', how='left')
        return df_master
        
    except FileNotFoundError:
        # Si no encuentra los archivos, crea la estructura vacía para generar el diccionario
        print("(Aviso: Archivos CSV no encontrados localmente. Generando diccionario basado en esquema teórico...)\n")
        columnas_estructura = {
            'order_id': pd.Series(dtype='object'),
            'customer_id': pd.Series(dtype='object'),
            'order_status': pd.Series(dtype='object'),
            'order_purchase_timestamp': pd.Series(dtype='datetime64[ns]'),
            'customer_state': pd.Series(dtype='object'),
            'payment_type': pd.Series(dtype='object'),
            'payment_value': pd.Series(dtype='float64')
        }
        return pd.DataFrame(columnas_estructura)

# Obtenemos el DataFrame (real o simulado)
df_maestro = obtener_dataset_maestro()

# Construcción programática del Diccionario
def generar_diccionario(df):
    # 1. Extraemos los nombres de columnas y sus tipos de datos en Pandas
    diccionario = pd.DataFrame({
        'Nombre de la Columna': df.columns,
        'Tipo de Dato (Python)': df.dtypes.astype(str)
    })
    
    # 2. Mapeamos las descripciones de negocio para el informe
    descripciones = {
        'order_id': 'Código alfanumérico único para cada pedido.',
        'customer_id': 'Código alfanumérico único del cliente en ese pedido.',
        'order_status': 'Estado actual del pedido (entregado, cancelado, facturado, etc.).',
        'order_purchase_timestamp': 'Fecha y hora exacta en que se realizó la transacción.',
        'customer_state': 'Sigla del estado (región) de residencia del cliente (ej. SP, RJ).',
        'payment_type': 'Método de pago utilizado (credit_card, boleto, voucher).',
        'payment_value': 'Monto total pagado en esa transacción.'
    }
    
    # 3. Mapeamos los tipos de variables según lo que exige la rúbrica del profesor
    tipo_rubrica = {
        'order_id': 'Identificador',
        'customer_id': 'Identificador',
        'order_status': 'Categórica Nominal',
        'order_purchase_timestamp': 'Temporal',
        'customer_state': 'Geográfica',
        'payment_type': 'Categórica Nominal',
        'payment_value': 'Numérica Continua'
    }
    
    # Asignamos los mapeos al DataFrame
    diccionario['Tipo de Variable (Rúbrica)'] = diccionario['Nombre de la Columna'].map(tipo_rubrica).fillna('Desconocido')
    diccionario['Descripción'] = diccionario['Nombre de la Columna'].map(descripciones).fillna('Sin descripción')
    
    # Reordenamos las columnas para que se vea ordenado
    diccionario = diccionario[['Nombre de la Columna', 'Tipo de Dato (Python)', 'Tipo de Variable (Rúbrica)', 'Descripción']]
    
    return diccionario

# Ejecutamos la función y mostramos el diccionario
df_diccionario = generar_diccionario(df_maestro)
print(df_diccionario.to_string(index=False))

# Opcional: Si quieres exportarlos a CSV para adjuntarlos a tu entrega, descomenta estas líneas:
# df_comparacion.to_csv("03_tabla_comparacion_datasets.csv", index=False)
# df_diccionario.to_csv("04_diccionario_de_datos.csv", index=False)