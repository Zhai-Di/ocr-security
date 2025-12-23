import numpy as np
import pandas as pd
import math
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
tqdm.pandas()


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


def calculate_ratio(row, col_1, col_2):
    str_col_1 = str(row[col_1])
    str_col_2 = str(row[col_2])
    div_tmp_1 = Decimal(str_col_1) / Decimal(str_col_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def price_deviation_ratio(row, index_func, l, f, case_str):
    _, p_k_distribution, p_i_man_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_man_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    md_ind = math.floor(l / 2)
    row_median = Decimal(str(row[f"ob{md_ind}"]))
    if case_str == "inflation":
        price_deviation = e_m_fin - row_median
    else:
        price_deviation = row_median - e_m_fin
    deviation_ratio = (price_deviation / row_median).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return float(deviation_ratio)


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


def price_deviation_simulator(row, index_func, f, case_str):
    ob_value_cols = [f"ob{i}" for i in range(31)]
    ob_values = row[ob_value_cols]
    sim_row = uniformly_drop(ob_values, f)
    obs_list_len = 31 - f
    return price_deviation_ratio(sim_row, index_func, obs_list_len, f, case_str)


if __name__ == "__main__":
    df = pd.read_csv("../data/eth_usd_honest_lists.csv")
    # df["deviation_ratio_10"] = df.progress_apply(
    #     lambda row: price_deviation_simulator(row, scenario_1_index_inflation, 10, "inflation"),
    #     axis=1
    # )
    # df["deviation_ratio_6"] = df.progress_apply(
    #     lambda row: price_deviation_simulator(row, scenario_1_index_inflation, 6, "inflation"),
    #     axis=1
    # )
    # df["deviation_ratio_5"] = df.progress_apply(
    #     lambda row: price_deviation_simulator(row, scenario_1_index_inflation, 5, "inflation"),
    #     axis=1
    # )
    # print(f"When f = 10, the max metric_1 in inflation case is {df["deviation_ratio_10"].max()}")
    # print(f"When f = 6, the max metric_1 in inflation case is {df["deviation_ratio_6"].max()}")
    # print(f"When f = 5, the max metric_1 in inflation case is {df["deviation_ratio_5"].max()}")
    df["deviation_ratio_10"] = df.progress_apply(
        lambda row: price_deviation_simulator(row, scenario_1_index_deflation, 10, "deflation"),
        axis=1
    )
    df["deviation_ratio_6"] = df.progress_apply(
        lambda row: price_deviation_simulator(row, scenario_1_index_deflation, 6, "deflation"),
        axis=1
    )
    df["deviation_ratio_5"] = df.progress_apply(
        lambda row: price_deviation_simulator(row, scenario_1_index_deflation, 5, "deflation"),
        axis=1
    )
    print(f"When f = 10, the max metric_1 in deflation case is {df["deviation_ratio_10"].max()}")
    print(f"When f = 6, the max metric_1 in deflation case is {df["deviation_ratio_6"].max()}")
    print(f"When f = 5, the max metric_1 in deflation case is {df["deviation_ratio_5"].max()}")


