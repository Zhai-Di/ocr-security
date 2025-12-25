import pandas as pd
import numpy as np
import math
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


def filter_honest_lists(df, threshold, f):
    df["min_d_v"] = df["ob" + str(f)] - df["ob0"]
    df["max_d_v"] = df["ob" + str(3 * f)] - df["ob" + str(2 * f)]
    df["min_d_ratio"] = df.apply(apply_calculate_ratio_min, axis=1)
    df["max_d_ratio"] = df.apply(apply_calculate_ratio_max, axis=1)
    effective_threshold = df["difference_bound_ratio"].apply(lambda x: max(threshold, x))
    filter_df = df[
        (df["min_d_ratio"] <= effective_threshold) &
        (df["max_d_ratio"] <= effective_threshold)
    ].copy().reset_index(drop=True)
    filter_df["honest_difference"] = filter_df["ob" + str(3 * f)] - filter_df["ob0"]
    filter_df["honest_difference_ratio"] = filter_df.apply(apply_honest_difference_ratio, axis=1)
    return filter_df


def calculate_distributions(series, threshold, metric_str):
    sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
    print(f"\n=== The distribution of {metric_str} when threshold is {threshold} ===")
    print(f"The maximum of {metric_str} is {series.max()}")
    percents = [0.0001, 0.001, 0.01, 0.1]
    len_s = len(sorted_series)
    for p in percents:
        idx = max(math.ceil(len_s * p) - 1, 0)
        val = sorted_series.iloc[idx]
        print(f"{p * 100:.3f}% is greater than or equal to {val}, with index {idx}")
        print()


def apply_difference_bound(row):
    f = 10
    return compute_difference_bound(row, f)


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


def calculate_scenario_1_max_variability(row, l, f):
    max_inflation_index = math.floor(l / 2) + f
    max_deflation_index = math.floor(l / 2) - f
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    max_variability = row[max_inflation_col] - row[max_deflation_col]
    return max_variability


def calculate_scenario_2_max_variability(row, l, f):
    max_inflation_index = 3 * f
    max_deflation_index = 0
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    max_variability = row[max_inflation_col] - row[max_deflation_col]
    return max_variability


if __name__ == "__main__":
    read_file_path = "../data/eth_usd_full_lists.csv"
    full_lists = pd.read_csv(read_file_path)
    full_lists['difference_bound'] = full_lists.apply(apply_difference_bound, axis=1)
    full_lists['difference_bound_ratio'] = full_lists.apply(apply_difference_bound_ratio, axis=1)
    # nv_thresholds = [0.0, 0.005, 0.015, 0.025, 0.035, 0.045, 0.055, 0.065, 0.075, 0.0851]
    nv_thresholds = np.linspace(0, 0.0851, 10)
    nv_thresholds = [round(float(x), 4) for x in nv_thresholds]
    print("nv_thresholds =", nv_thresholds)
    for threshold in nv_thresholds:
        honest_lists = filter_honest_lists(full_lists, threshold, 10)
        l = 31
        f = 10
        honest_lists["max_variability"] = honest_lists.apply(
            lambda row: calculate_scenario_2_max_variability(row, l, f), axis=1
        )
        honest_lists["median"] = honest_lists["median"].apply(lambda x: Decimal(str(x)))
        honest_lists["max_variability"] = honest_lists["max_variability"].apply(lambda x: Decimal(str(x)))
        honest_lists["variability_ratio"] = honest_lists.apply(
            lambda row: row["max_variability"] / row["median"], axis=1
        )
        honest_lists["max_variability"] = honest_lists["max_variability"].apply(
            lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        )
        honest_lists["variability_ratio"] = honest_lists["variability_ratio"].apply(
            lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        )
        ratio_col = honest_lists["variability_ratio"].astype(float)
        calculate_distributions(ratio_col, threshold, "metric_2")