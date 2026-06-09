import pandas as pd

hash = pd.util.hash_pandas_object(pd.Series([1, 2, 3]))
print(hash)
