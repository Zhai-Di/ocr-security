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


def scenario_1_index_inflation(l, f):
    i_ori = math.floor(l / 2)
    k_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_man_distribution = {}
    for k in range(0, k_range + 1):
        z = k
        i_man = math.floor(l / 2) + z
        lcombs = math.comb(i_man, z)
        rcombs = math.comb(l - 1 - i_man, f - z)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_man_distribution[i_man] = p_k
    return expectation, p_k_distribution, p_i_man_distribution


def scenario_1_index_deflation(l, f):
    i_ori = math.floor(l / 2)
    k_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_man_distribution = {}
    for k in range(0, k_range + 1):
        z = f - k
        i_man = math.floor(l / 2) - f + z
        lcombs = math.comb(i_man, z)
        rcombs = math.comb(l - 1 - i_man, f - z)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_man_distribution[i_man] = p_k
    return expectation, p_k_distribution, p_i_man_distribution


def scenario_2_index_inflation(l, f):
    i_ori = math.floor(l / 2)
    u_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_man_distribution = {}
    for u in range(0, u_range + 1):
        i_man = u + 2 * f
        lcombs = math.comb(i_man, u)
        rcombs = math.comb(l - 1 - i_man, f - u)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
        k = u + 2 * f - math.floor(l / 2)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_man_distribution[i_man] = p_k
    return expectation, p_k_distribution, p_i_man_distribution


def scenario_2_index_deflation(l, f):
    i_ori = math.floor(l / 2)
    u_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_man_distribution = {}
    for u in range(0, u_range + 1):
        i_man = u
        lcombs = math.comb(i_man, u)
        rcombs = math.comb(l - 1 - i_man, f - u)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
        k = math.floor(l / 2) - u
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_man_distribution[i_man] = p_k
    return expectation, p_k_distribution, p_i_man_distribution


def calculate_e_m_fin(row, index_func, l, f):
    _, p_k_distribution, p_i_man_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_man_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    return e_m_fin


def calculate_distributions(series, threshold, metric_str):
    sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
    print(f"\n=== 当threshold = {threshold}时，{metric_str}的分布 ===")
    print(f"{metric_str}的最大值是 {series.max()}")
    percents = [0.0001, 0.001, 0.01, 0.1]
    len_s = len(sorted_series)
    for p in percents:
        idx = max(math.ceil(len_s * p) - 1, 0)
        val = sorted_series.iloc[idx]
        print(f"{p * 100:.3f}%大于等于     {val}，相应的索引是{idx}")
        print()


def apply_difference_bound(row):
    f = 5
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


def apply_calculate_e_m_fin_scenario_1_inflation(row):
    index_func = scenario_1_index_inflation
    l = 16
    f = 5
    return calculate_e_m_fin(row, index_func, l, f)


def apply_calculate_e_m_fin_scenario_1_deflation(row):
    index_func = scenario_1_index_deflation
    l = 16
    f = 5
    return calculate_e_m_fin(row, index_func, l, f)


def apply_calculate_e_m_fin_scenario_2_inflation(row):
    index_func = scenario_2_index_inflation
    l = 16
    f = 5
    return calculate_e_m_fin(row, index_func, l, f)


def apply_calculate_e_m_fin_scenario_2_deflation(row):
    index_func = scenario_2_index_deflation
    l = 16
    f = 5
    return calculate_e_m_fin(row, index_func, l, f)


if __name__ == "__main__":
    # read_file_path = "../data/bnb_usd_full_lists.csv"
    # full_lists = pd.read_csv(read_file_path)
    # full_lists['difference_bound'] = full_lists.apply(apply_difference_bound, axis=1)
    # full_lists['difference_bound_ratio'] = full_lists.apply(apply_difference_bound_ratio, axis=1)
    # nv_thresholds = np.linspace(0, 0.0771, 10)
    # nv_thresholds = [round(float(x), 4) for x in nv_thresholds]
    # print("nv_thresholds =", nv_thresholds)
    # for threshold in nv_thresholds:
    #     honest_lists = filter_honest_lists(full_lists, threshold, 5)
    #     honest_lists["median"] = honest_lists["median"].apply(lambda x: Decimal(str(x)))
    #     honest_lists["e_m_fin"] = honest_lists.apply(apply_calculate_e_m_fin_scenario_2_deflation, axis=1)
    #     honest_lists["price_deviation"] = honest_lists.apply(
    #         lambda row: row["median"] - row["e_m_fin"], axis=1
    #     )
    #     honest_lists["price_deviation"] = honest_lists["price_deviation"].apply(
    #         lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    #     )
    #     honest_lists["deviation_ratio"] = honest_lists.apply(
    #         lambda row: row["price_deviation"] / row["median"], axis=1
    #     )
    #     honest_lists["deviation_ratio"] = honest_lists["deviation_ratio"].apply(
    #         lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    #     )
    #     ratio_col = honest_lists["deviation_ratio"].astype(float)
    #     calculate_distributions(ratio_col, threshold, "metric_1")
    read_file_path = "../data/bnb_usd_honest_lists.csv"
    df = pd.read_csv(read_file_path)
    print(df.columns)