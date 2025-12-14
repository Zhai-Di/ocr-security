import math
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os


def scenario_1_index_inflation(l, f):
    i_ori = math.floor(l / 2)
    k_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_fin_distribution = {}
    for k in range(0, k_range + 1):
        z = k
        i_fin = math.floor(l / 2) + z
        lcombs = math.comb(i_fin, z)
        rcombs = math.comb(l - 1 - i_fin, f - z)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_fin_distribution[i_fin] = p_k
    return expectation, p_k_distribution, p_i_fin_distribution


def scenario_1_index_deflation(l, f):
    i_ori = math.floor(l / 2)
    k_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_fin_distribution = {}
    for k in range(0, k_range + 1):
        z = f - k
        i_fin = math.floor(l / 2) - f + z
        lcombs = math.comb(i_fin, z)
        rcombs = math.comb(l - 1 - i_fin, f - z)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_fin_distribution[i_fin] = p_k
    return expectation, p_k_distribution, p_i_fin_distribution


def scenario_2_index_inflation(l, f):
    i_ori = math.floor(l / 2)
    u_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_fin_distribution = {}
    for u in range(0, u_range + 1):
        i_fin = u + 2 * f
        lcombs = math.comb(i_fin, u)
        rcombs = math.comb(l - 1 - i_fin, f - u)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
        k = u + 2 * f - math.floor(l / 2)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_fin_distribution[i_fin] = p_k
    return expectation, p_k_distribution, p_i_fin_distribution


def scenario_2_index_deflation(l, f):
    i_ori = math.floor(l / 2)
    u_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_fin_distribution = {}
    for u in range(0, u_range + 1):
        i_fin = u
        lcombs = math.comb(i_fin, u)
        rcombs = math.comb(l - 1 - i_fin, f - u)
        combs = lcombs * rcombs
        p_k = Decimal(combs) / Decimal(total_combs)
        p_k = p_k.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
        k = math.floor(l / 2) - u
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_fin_distribution[i_fin] = p_k
    return expectation, p_k_distribution, p_i_fin_distribution


def calculate_ratio(row, col_1, col_2):
    str_col_1 = str(row[col_1])
    str_col_2 = str(row[col_2])
    div_tmp_1 = Decimal(str_col_1) / Decimal(str_col_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def calculate_e_m_fin(row, index_func, l, f):
    _, p_k_distribution, p_i_fin_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_fin_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    return e_m_fin


def apply_calculate_e_m_fin_scenario_1_inflation(row):
    index_func = scenario_1_index_inflation
    l = 31
    f = 10
    return calculate_e_m_fin(row, index_func, l, f)


def apply_calculate_e_m_fin_scenario_1_deflation(row):
    index_func = scenario_1_index_deflation
    l = 31
    f = 10
    return calculate_e_m_fin(row, index_func, l, f)


def apply_calculate_e_m_fin_scenario_2_inflation(row):
    index_func = scenario_2_index_inflation
    l = 31
    f = 10
    return calculate_e_m_fin(row, index_func, l, f)


def apply_calculate_e_m_fin_scenario_2_deflation(row):
    index_func = scenario_2_index_deflation
    l = 31
    f = 10
    return calculate_e_m_fin(row, index_func, l, f)


def calculate_thresholds(series, col_name, percents, len_df):
    sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
    print(f"\n=== Experimental results for {col_name} ===")
    for p in percents:
        idx = max(math.ceil(len_df * p) - 1, 0)
        val = sorted_series.iloc[idx]
        print(f"{p * 100:.3f}% is greater than or equal to     {val}")
        print()


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    obs_file_path = os.path.join(current_dir, "..", "data", "honest_observations.csv")
    df_obs = pd.read_csv(obs_file_path)
    df_obs["median"] = df_obs["median"].apply(lambda x: Decimal(str(x)))
    # Reproducing the experimental results of yyflation under scenario x requires setting both x and yy in the parameter apply_calculate_e_m_fin_scenario_x_yyflation
    # df_obs["e_m_fin"] = df_obs.apply(apply_calculate_e_m_fin_scenario_x_yyflation, axis=1)
    df_obs["e_m_fin"] = df_obs.apply(apply_calculate_e_m_fin_scenario_2_deflation, axis=1)
    # In the inflation case, it is row["e_m_fin"] - row["median"]
    # In the deflation case, it is row["median"] - row["e_m_fin"]
    df_obs["price_deviation"] = df_obs.apply(lambda row: row["median"] - row["e_m_fin"], axis=1)
    df_obs["deviation_ratio"] = df_obs.apply(lambda row: row["price_deviation"] / row["median"], axis=1)
    df_obs["deviation_ratio"] = df_obs["deviation_ratio"].apply(lambda x: x.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP))
    percentiles = [0.00005, 0.0001, 0.001, 0.01, 0.1]
    n = len(df_obs)
    calculate_thresholds(df_obs["price_deviation"], "price_deviation", percentiles, n)
    calculate_thresholds(df_obs["deviation_ratio"], "deviation_ratio", percentiles, n)