import numpy as np
import pandas as pd
import math
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
tqdm.pandas()


def scenario_1_uncertainty_ratio(row, l, f):
    max_inflation_index = math.floor(l / 2) + f
    max_deflation_index = math.floor(l / 2) - f
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    max_uncertainty = row[max_inflation_col] - row[max_deflation_col]
    ratio_temp = Decimal(str(max_uncertainty)) / Decimal(str(row["honest_difference"]))
    ratio_temp = ratio_temp.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    uncertainty_ratio = float(ratio_temp)
    return uncertainty_ratio


def scenario_2_uncertainty_ratio(row, l, f):
    max_inflation_index = 3 * f
    max_deflation_index = 0
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    max_uncertainty = row[max_inflation_col] - row[max_deflation_col]
    ratio_temp = Decimal(str(max_uncertainty)) / Decimal(str(row["honest_difference"]))
    ratio_temp = ratio_temp.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    uncertainty_ratio = float(ratio_temp)
    return uncertainty_ratio


def uniformly_drop(row, f):
    row = row.reset_index(drop=True)
    length = len(row)
    indices_to_drop = []
    group_size = length / f
    for i in range(f):
        start = int(round(i * group_size))
        end = int(round((i + 1) * group_size)) if i != f - 1 else length
        if end > start:
            mid_index = start + (end - start) // 2
            indices_to_drop.append(mid_index)
    row_dropped = row.drop(index=indices_to_drop).reset_index(drop=True)
    col_names = [f"ob{i}" for i in range(len(row_dropped))]
    return pd.Series(row_dropped.values, index=col_names)


def median_uncertainty_simulator(row, f):
    ob_value_cols = [f"ob{i}" for i in range(31)]
    ob_values = row[ob_value_cols]
    sim_row = uniformly_drop(ob_values, f)
    sim_row["honest_difference"] = row["honest_difference"]
    # print(sim_row.index)
    obs_list_len = 31 - f
    return scenario_1_uncertainty_ratio(sim_row, obs_list_len, f)


def dolev_bound(n, f):
    dolev_c = math.floor((n - 3 * f - 1) / f) + 1
    print(f"dolev_c = {dolev_c}")
    bound_temp = Decimal(1) / Decimal(dolev_c)
    bound_temp = bound_temp.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    d_bound = float(bound_temp)
    return d_bound


if __name__ == "__main__":
    df = pd.read_csv("../data/eth_usd_honest_lists.csv")
    # df["median_scn1_uncertainty_10"] = df.progress_apply(
    #     lambda row: scenario_1_uncertainty_ratio(row, 31, 10),
    #     axis=1
    # )
    # df["median_scn2_uncertainty_10"] = df.progress_apply(
    #     lambda row: scenario_2_uncertainty_ratio(row, 31, 10),
    #     axis=1
    # )
    df["median_scn1_uncertainty_6"] = df.progress_apply(
        lambda row: median_uncertainty_simulator(row, 6),
        axis=1
    )
    # df["median_scn1_uncertainty_5"] = df.progress_apply(
    #     lambda row: median_uncertainty_simulator(row, 5),
    #     axis=1
    # )
    df["dolev_bound_6"] = dolev_bound(31, 6)
    # df["dolev_bound_5"] = dolev_bound(31, 5)
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    matplotlib.use('TkAgg')
    plt.rcParams['font.family'] = 'Arial'
    plt.figure(figsize=(5, 4), dpi=150)
    x = df['blockNumber']
    # y_1 = df["median_scn1_uncertainty_10"]
    # y_2 = df["median_scn2_uncertainty_10"]
    y_3 = df["median_scn1_uncertainty_6"]
    # y_4 = df["median_scn1_uncertainty_5"]
    y_5 = df["dolev_bound_6"]
    # y_6 = df["dolev_bound_5"]
    # Below is the code corresponding to subfigure-a
    plt.scatter(x, y_3, color=colors[4], s=2, marker='o', alpha=0.8, label="median-based method")
    plt.scatter(x, y_5, color=colors[3], s=5, marker='o', alpha=1, label="Dolev's function")
    # Below is the code corresponding to subfigure-b
    # plt.scatter(x, y_4, color=colors[0], s=2, marker='o', alpha=0.8, label="median-based method")
    # plt.scatter(x, y_6, color=colors[5], s=5, marker='o', alpha=1, label="Dolev's function")
    plt.xlim([min(x), max(x)])
    plt.ylim([0.0, 1.05])
    x_min = int(min(x))
    x_max = int(max(x))
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
    plt.gca().set_xticklabels([str(x) for x in xticks], rotation=45, ha='right', rotation_mode='anchor', fontsize=14)
    plt.yticks(fontsize=16)
    plt.xlabel('block number', fontsize=18)
    plt.ylabel('ratio', fontsize=18)
    plt.tick_params(axis='both', direction='in', width=1.5, length=6)
    plt.grid(True, which='both', linestyle='--', linewidth=0.9)
    plt.tight_layout()
    plt.legend(fontsize=20, loc="best", markerscale=7)
    plt.show()