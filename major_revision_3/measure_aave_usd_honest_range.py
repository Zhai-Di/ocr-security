import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
import matplotlib.pyplot as plt


def calculate_ratio(row, col_1, col_2):
    str_col_1 = str(row[col_1])
    str_col_2 = str(row[col_2])
    div_tmp_1 = Decimal(str_col_1) / Decimal(str_col_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def compute_difference_bound(row, f):
    differences = []
    for i in range(f + 1):
        ob_high = "ob" + str(i + 2 * f)
        ob_low = "ob" + str(i)
        differences.append(row[ob_high] - row[ob_low])
    return min(differences)


def apply_difference_bound(row):
    f = 6
    return compute_difference_bound(row, f)
# 以上部分按照BNB的设置改完了


def apply_difference_bound_ratio(row):
    col_1 = 'difference_bound'
    col_2 = 'median'
    return calculate_ratio(row, col_1, col_2)


def apply_calculate_ratio_min(row):
    col_1 = "min_d_v"
    col_2 = "median"
    return calculate_ratio(row, col_1, col_2)


def apply_calculate_ratio_max(row):
    col_1 = "max_d_v"
    col_2 = "median"
    return calculate_ratio(row, col_1, col_2)


def apply_honest_difference_ratio(row):
    col_1 = 'honest_difference'
    col_2 = 'median'
    return calculate_ratio(row, col_1, col_2)


if __name__ == "__main__":
    read_file_path = "../data/aave_usd_full_lists.csv"
    write_file_path = "../data/aave_usd_honest_lists.csv"
    df = pd.read_csv(read_file_path)
    df['difference_bound'] = df.apply(apply_difference_bound, axis=1)
    df['difference_bound_ratio'] = df.apply(apply_difference_bound_ratio, axis=1)
    max_acceptable_nv = df["difference_bound_ratio"].max()
    max_acceptable_nv = float(round(max_acceptable_nv, 4))
    print(f"max_acceptable_nv {max_acceptable_nv}")
    f = 6
    df["min_d_v"] = df["ob" + str(f)] - df["ob0"]
    df["max_d_v"] = df["ob" + str(3 * f)] - df["ob" + str(2 * f)]
    df["min_d_ratio"] = df.apply(apply_calculate_ratio_min, axis=1)
    df["max_d_ratio"] = df.apply(apply_calculate_ratio_max, axis=1)
    filter_df = df[(df["min_d_ratio"] <= max_acceptable_nv) & (df["max_d_ratio"] <= max_acceptable_nv)].copy().reset_index(drop=True)
    filter_df["honest_difference"] = filter_df["ob18"] - filter_df["ob0"]
    filter_df.to_csv(write_file_path, index=False)
    df_honest = pd.read_csv(write_file_path)
    df_honest["honest_difference_ratio"] = df_honest.apply(apply_honest_difference_ratio, axis=1)
    matplotlib.use('TkAgg')
    plt.rcParams['font.family'] = 'Arial'
    scatter_color = (109 / 255, 101 / 255, 163 / 255)
    plt.figure(figsize=(5, 4), dpi=150)
    fig_x = df_honest['blockNumber']
    fig_y = df_honest["honest_difference_ratio"]
    plt.scatter(fig_x, fig_y, color=scatter_color, s=10, marker='o', alpha=0.7)
    plt.xlim([min(fig_x), max(fig_x)])
    plt.ylim([min(fig_y), max(fig_y) + 0.002])
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