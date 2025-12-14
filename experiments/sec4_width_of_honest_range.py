import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker
from decimal import Decimal, ROUND_HALF_UP
import os


def calculate_ratio(row, col_1, col_2):
    str_col_1 = str(row[col_1])
    str_col_2 = str(row[col_2])
    div_tmp_1 = Decimal(str_col_1) / Decimal(str_col_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def apply_honest_difference_ratio(row):
    col_1 = 'honest_difference'
    col_2 = 'median'
    return calculate_ratio(row, col_1, col_2)


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    read_file_path = os.path.join(current_dir, "..", "data", "honest_observations.csv")
    df_obs = pd.read_csv(read_file_path)
    df_obs["honest_difference_ratio"] = df_obs.apply(apply_honest_difference_ratio, axis=1)
    matplotlib.use('TkAgg')
    plt.rcParams['font.family'] = 'Arial'
    scatter_color = (41 / 255, 56 / 255, 144 / 255)
    plt.figure(figsize=(5, 4), dpi=150)
    fig_x = df_obs['blockNumber']
    fig_y = df_obs["honest_difference_ratio"]
    plt.scatter(fig_x, fig_y, color=scatter_color, s=10, marker='o', alpha=0.7)
    plt.xlim([min(fig_x), max(fig_x)])
    plt.ylim([min(fig_y), max(fig_y) + 0.002])
    print(f"xlim is [{min(fig_x)}, {max(fig_x)}]")
    x_min = int(min(fig_x))
    x_max = int(max(fig_x))
    range_span = x_max - x_min
    max_ticks = 20
    raw_step = max(1, range_span // (max_ticks - 1))
    step_rounded = ((raw_step + 9999) // 10000) * 10000
    tick_start = ((x_min + step_rounded - 1) // step_rounded) * step_rounded
    tick_end = (x_max // step_rounded) * step_rounded
    if tick_end < tick_start:
        xticks = np.array([tick_start])
    else:
        xticks = np.arange(tick_start, tick_end + 1, step=step_rounded)
    plt.xticks(ticks=xticks)
    plt.gca().set_xticklabels([str(x) for x in xticks], rotation=45, ha='right', rotation_mode='anchor', fontsize=12)
    plt.yticks(fontsize=16)
    plt.xlabel('block number', fontsize=16)
    plt.ylabel('width of the honest range', fontsize=16)
    plt.tick_params(axis='both', direction='in', width=1.5, length=6)
    plt.grid(True, which='both', linestyle='--', linewidth=0.9)
    plt.tight_layout()
    plt.show()