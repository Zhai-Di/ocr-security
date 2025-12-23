import math
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import numpy as np
# from analysis_scripts.index_dev_distribution import *
import matplotlib
import matplotlib.pyplot as plt


def scenario_1_index_inflation(l, f):
    i_ori = math.floor(l / 2)
    k_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_man_distribution = {}
    for k in range(0, k_range + 1):
        # 对应到旧版论文中，k = \Delta i
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


# f是实际参与作恶的预言机数量，不是必须满足l = 3f + 1，也可以l > 3f + 1
# 下面函数体中的x都要改成f
def scenario_1_index_deflation(l, f):
    i_ori = math.floor(l / 2)
    k_range = f
    total_combs = math.comb(l, f)
    p_k_sum = Decimal(0)
    expectation = Decimal(0)
    p_k_distribution = {}
    p_i_man_distribution = {}
    for k in range(0, k_range + 1):
        # 为什么z = x - k？因为在这个函数的计算过程中k就是论文中的\Delta I
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


# 下面的函数scenario_2_index_inflation(l, f)中的f必须满足l = 3f + 1
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
        # k就是论文中的\Delta I
        k = u + 2 * f - math.floor(l / 2)
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_man_distribution[i_man] = p_k
    return expectation, p_k_distribution, p_i_man_distribution


# 下面的函数scenario_2_index_deflation(l, f)中的f必须满足l = 3f + 1
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
        # k就是论文中的\Delta I
        k = math.floor(l / 2) - u
        p_k_sum = p_k_sum + p_k
        expectation = expectation + Decimal(k) * p_k
        p_k_distribution[k] = p_k
        p_i_man_distribution[i_man] = p_k
    return expectation, p_k_distribution, p_i_man_distribution


def calculate_ratio(row, col_1, col_2):
    str_col_1 = str(row[col_1])
    str_col_2 = str(row[col_2])
    div_tmp_1 = Decimal(str_col_1) / Decimal(str_col_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def calculate_e_m_fin(row, index_func, l, f):
    _, p_k_distribution, p_i_man_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_man_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        # 下面计算的是m_fin的期望，概率乘相应索引下的取值
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    return e_m_fin


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


# def calculate_thresholds(series, col_name, percents, len_df):
#     sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
#     print(f"\n=== 以下是{col_name}的实验结果 ===")
#     for p in percents:
#         idx = max(math.ceil(len_df * p) - 1, 0)
#         val = sorted_series.iloc[idx]
#         print(f"{p * 100:.3f}%大于等于     {val}        数据索引是{idx}")
#         print()


def calculate_distributions(series, metric_str):
    sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
    print(f"\n=== {metric_str}的分布 ===")
    print(f"{metric_str}的最大值是 {series.max()}")
    percents = [0.0001, 0.001, 0.01, 0.1]
    len_s = len(sorted_series)
    for p in percents:
        idx = max(math.ceil(len_s * p) - 1, 0)
        val = sorted_series.iloc[idx]
        print(f"{p * 100:.3f}%大于等于     {val}，相应的索引是{idx}")
        print()


if __name__ == "__main__":
    obs_file_path = "../data/bnb_usd_honest_lists.csv"
    df_obs = pd.read_csv(obs_file_path)
    df_obs["median"] = df_obs["median"].apply(lambda x: Decimal(str(x)))
    # 根据scenario_1, scenario_2, inflation, deflation需要改下面这行代码中的apply_calculate_e_m_fin_func
    df_obs["e_m_fin"] = df_obs.apply(apply_calculate_e_m_fin_scenario_2_deflation, axis=1)
    # 根据inflation, deflation需要改下面这行代码中的减数和被减数
    df_obs["price_deviation"] = df_obs.apply(lambda row: row["median"] - row["e_m_fin"], axis=1)
    df_obs["deviation_ratio"] = df_obs.apply(lambda row: row["price_deviation"] / row["median"], axis=1)
    df_obs["deviation_ratio"] = df_obs["deviation_ratio"].apply(lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    n = len(df_obs)
    print(f"len(honest_lists) = {n}")
    ratio_col = df_obs["deviation_ratio"].astype(float)
    calculate_distributions(ratio_col, "metric_1")