import numpy as np
import pandas as pd
import math
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
tqdm.pandas()


# 在下面的函数中，参数l的含义是最终传输到aggregator合约的obs list的长度
# 如果DON中有n个oracle nodes，leader在收到n-f个ob之后进行聚合，则这种情况下l=n-f
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


# 在下面这个函数中，参数n的含义是DON中的oracle nodes数量
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
    df["median_scn1_uncertainty_5"] = df.progress_apply(
        lambda row: median_uncertainty_simulator(row, 5),
        axis=1
    )
    print(f"n = 31, f = 6")
    print(df["median_scn1_uncertainty_6"].max())
    print((df["median_scn1_uncertainty_6"] > 0.95).sum())
    print(f"n = 31, f = 5")
    print(df["median_scn1_uncertainty_5"].max())
    print((df["median_scn1_uncertainty_5"] > 0.95).sum())
