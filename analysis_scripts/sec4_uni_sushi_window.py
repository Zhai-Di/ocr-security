import pandas as pd


df_uni = pd.read_csv("../data/uni_window_prices.csv")
df_sushi = pd.read_csv("../data/sushi_window_prices.csv")
uni_len0 = len(df_uni)
# 第一步：原地删除完全重复的行
df_uni.drop_duplicates(subset=df_uni.columns.tolist(), keep="first", inplace=True)
# 第二步：重置索引（原地）
df_uni.reset_index(drop=True, inplace=True)
# 统计结果
uni_len1 = len(df_uni)
print(f"已删除df_uni中完全重复的行，共删除 {uni_len0 - uni_len1} 行，保留 {uni_len1} 行。")
sushi_len0 = len(df_sushi)
df_sushi.drop_duplicates(subset=df_sushi.columns.tolist(), keep="first", inplace=True)
df_sushi.reset_index(drop=True, inplace=True)
sushi_len1 = len(df_sushi)
print(f"已删除df_sushi中完全重复的行，共删除 {sushi_len0 - sushi_len1} 行，保留 {sushi_len1} 行。")
# 确保关键列存在
required_cols = {"blockNumber", "wd_min", "wd_max"}
if not required_cols.issubset(df_uni.columns):
    raise ValueError("uni_window_prices.csv 中缺少必要的列：blockNumber, wd_min, wd_max")
if not required_cols.issubset(df_sushi.columns):
    raise ValueError("sushi_window_prices.csv 中缺少必要的列：blockNumber, wd_min, wd_max")
# 按 blockNumber 对齐合并
df_merged = pd.merge(df_uni, df_sushi, on="blockNumber", how="inner", suffixes=("_uni", "_sushi"))
# 计算 min_min, max_max
df_merged["min_min"] = df_merged[["wd_min_uni", "wd_min_sushi"]].min(axis=1, skipna=True)
df_merged["max_max"] = df_merged[["wd_max_uni", "wd_max_sushi"]].max(axis=1, skipna=True)
# 计算 total_difference = max_max - min_min
df_merged["total_difference"] = df_merged["max_max"] - df_merged["min_min"]
# 只保留所需列
df_result = df_merged[["blockNumber", "min_min", "max_max", "total_difference"]]
# 保存结果到 CSV
df_result.to_csv("../data/uni_sushi_window.csv", index=False)
print("已成功生成 ../data/uni_sushi_window.csv 文件。")