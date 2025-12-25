import pandas as pd


df_uni = pd.read_csv("../data/uni_window_prices.csv")
df_sushi = pd.read_csv("../data/sushi_window_prices.csv")
uni_len0 = len(df_uni)
df_uni.drop_duplicates(subset=df_uni.columns.tolist(), keep="first", inplace=True)
df_uni.reset_index(drop=True, inplace=True)
uni_len1 = len(df_uni)
sushi_len0 = len(df_sushi)
df_sushi.drop_duplicates(subset=df_sushi.columns.tolist(), keep="first", inplace=True)
df_sushi.reset_index(drop=True, inplace=True)
sushi_len1 = len(df_sushi)
required_cols = {"blockNumber", "wd_min", "wd_max"}
if not required_cols.issubset(df_uni.columns):
    raise ValueError("uni_window_prices.csv is missing the required columns")
if not required_cols.issubset(df_sushi.columns):
    raise ValueError("sushi_window_prices.csv is missing the required columns")
df_merged = pd.merge(df_uni, df_sushi, on="blockNumber", how="inner", suffixes=("_uni", "_sushi"))
df_merged["min_min"] = df_merged[["wd_min_uni", "wd_min_sushi"]].min(axis=1, skipna=True)
df_merged["max_max"] = df_merged[["wd_max_uni", "wd_max_sushi"]].max(axis=1, skipna=True)
df_merged["total_difference"] = df_merged["max_max"] - df_merged["min_min"]
df_result = df_merged[["blockNumber", "min_min", "max_max", "total_difference"]]
df_result.to_csv("../data/uni_sushi_window.csv", index=False)