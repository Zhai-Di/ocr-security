import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


df_chlk = pd.read_csv("../data/eth_usd_honest_lists.csv")
df_dex = pd.read_csv("../data/uni_sushi_window.csv")
df_merged = pd.merge(df_chlk, df_dex, on="blockNumber", how="inner")
df_result = pd.DataFrame({
    "blockNumber": df_merged["blockNumber"],
    "chlk_min": df_merged["ob0"],
    "chlk_max": df_merged["ob30"],
    "dex_min": df_merged["min_min"],
    "dex_max": df_merged["max_max"],
    "chlk_difference": df_merged["honest_difference"],
    "dex_difference": df_merged["total_difference"]
})
write_path = "../data/align_prices.csv"
matplotlib.use('TkAgg')
plt.rcParams['font.family'] = 'Arial'
colors = plt.cm.tab10(np.linspace(0, 1, 10))
plt.figure(figsize=(23, 3))
x = df_result["blockNumber"]
y_1 = df_result["dex_min"]
y_2 = df_result["dex_max"]
y_3 = df_result["chlk_min"]
y_4 = df_result["chlk_max"]
plt.fill_between(
    df_result["blockNumber"],
    df_result["chlk_min"],
    df_result["chlk_max"],
    color=colors[3],
    alpha=1,
    label="range of values in each remaining list"
)
plt.fill_between(
    df_result["blockNumber"],
    df_result["dex_min"],
    df_result["dex_max"],
    color=colors[0],
    alpha=0.7,
    label="range of DEX prices"
)
plt.xlim([min(x), max(x)])
plt.ylim([min(y_3) - 80, max(y_4) + 50])
x_min = int(min(x))
x_max = int(max(x))
range_span = x_max - x_min
max_ticks = 32
raw_step = max(1, range_span // (max_ticks - 1))
step_rounded = ((raw_step + 9999) // 10000) * 10000
tick_start = ((x_min + step_rounded - 1) // step_rounded) * step_rounded
tick_end = (x_max // step_rounded) * step_rounded
if tick_end < tick_start:
    xticks = np.array([tick_start])
else:
    xticks = np.arange(tick_start, tick_end + 1, step=step_rounded)
plt.xticks(ticks=xticks)
plt.gca().set_xticklabels([str(x) for x in xticks], rotation=30, ha='right', rotation_mode='anchor', fontsize=11)
yticks = np.arange(1000, y_4.max(), step=500)
plt.yticks(yticks, fontsize=12)
plt.xlabel('block number', fontsize=12)
plt.ylabel('ETH price in USD', fontsize=12)
plt.tick_params(axis='both', direction='in', width=1, length=3)
plt.legend(
    fontsize=12,
    loc='best',
    frameon=True,
)
plt.tight_layout(rect=[0.02, 0.03, 0.99, 0.99])
plt.show()
