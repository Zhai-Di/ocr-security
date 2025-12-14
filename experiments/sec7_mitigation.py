import math
import pandas as pd
import numpy as np
import itertools
from eth_abi import decode
from decimal import Decimal, ROUND_HALF_UP
from functools import reduce
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


def calculate_price_deviation_median(row, index_func, l, f, case_type_str):
    _, p_k_distribution, p_i_fin_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_fin_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    print(f"in the median aggregation, m_ori = {row['median']}, e_m_fin = {e_m_fin}")
    if case_type_str == "inflation":
        price_deviation = e_m_fin - Decimal(str(row["median"]))
    else:
        price_deviation = Decimal(str(row["median"])) - e_m_fin
    return price_deviation


def calculate_e_m_fin(row, index_func, l, f):
    _, p_k_distribution, p_i_fin_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_fin_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    return e_m_fin


def simulate_falsification(row, f, case_type_str):
    num_obs = len(row)
    falsify_value = Decimal("1500.0")
    indices = list(range(num_obs))
    combinations = list(itertools.combinations(indices, f))
    print(f"The number of combinations is {len(combinations)}")
    falsified_list = []
    row = row.apply(lambda x: Decimal(str(x)))
    for comb in combinations:
        new_row = row.copy()
        for idx in comb:
            if case_type_str == "inflation":
                new_row.iloc[idx] += falsify_value
            else:
                new_row.iloc[idx] -= falsify_value
        falsified_list.append(new_row)
    return pd.DataFrame(falsified_list)


def dolev_func(row, f, k):
    sorted_row = row.sort_values().reset_index(drop=True)
    if 2 * f >= len(sorted_row):
        raise ValueError("the length of row is less than or equal to 2 * f")
    reduced_row = sorted_row[f: len(sorted_row) - f].reset_index(drop=True)
    j = math.floor((len(reduced_row) - 1) / k)
    selected_values = [reduced_row[i * k] for i in range(j + 1)]
    total = reduce(lambda x, y: x + y, selected_values)
    if isinstance(total, Decimal):
        mean = total / Decimal(len(selected_values))
    else:
        mean = total / len(selected_values)
    return mean


def calculate_price_deviation_dolev(row, f, k, case_type_str):
    df_falsified = simulate_falsification(row, f, case_type_str)
    total_combinations = math.comb(len(row), f)
    print(f"total_combinations = {total_combinations}")
    weight = Decimal("1") / Decimal(total_combinations)
    e_d_fin = Decimal("0")
    d_values = df_falsified.apply(lambda r: dolev_func(r, f, k), axis=1)
    for d_value in d_values:
        e_d_fin += d_value * weight
    row = row.apply(lambda x: Decimal(str(x)))
    d_ori = dolev_func(row, f, k)
    print(f"in the dolev aggregation, d_ori = {d_ori}，e_d_fin = {e_d_fin}")
    if case_type_str == "inflation":
        price_deviation = e_d_fin - d_ori
    else:
        price_deviation = d_ori - e_d_fin
    return d_ori, e_d_fin, price_deviation


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
    return row_dropped


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    read_path = os.path.join(current_dir, "..", "data", "honest_observations.csv")
    df_obs = pd.read_csv(read_path)
    total_rows = len(df_obs)
    top_k = math.floor(total_rows * 0.01)
    df_samples = df_obs.sort_values(by="honest_difference", ascending=False).head(top_k)
    simulate_case = "deflation"
    df_samples["median"] = df_samples["median"].apply(lambda x: Decimal(str(x)))
    df_samples["honest_difference"] = df_samples["honest_difference"].apply(lambda x: Decimal(str(x)))
    # Set the following scenario_1_index_xxflation parameter according to whether the simulation is under the inflation case or the deflation case.
    df_samples["e_m_fin"] = df_samples.apply(lambda row: calculate_e_m_fin(row, scenario_1_index_deflation, 31, 10), axis=1)
    if simulate_case == "inflation":
        df_samples["median_price_deviation"] = df_samples["e_m_fin"] - df_samples["median"]
    else:
        df_samples["median_price_deviation"] = df_samples["median"] - df_samples["e_m_fin"]
    ob_value_columns = [f"ob{i}" for i in range(31)]
    dolev_columns = df_samples[ob_value_columns]
    dolev_columns = dolev_columns.apply(lambda row: uniformly_drop(row, 5), axis=1)
    df_samples[["d_ori", "e_d_fin", "dolev_price_deviation"]] = dolev_columns.apply(
        lambda row: pd.Series(calculate_price_deviation_dolev(row, 5, 5, simulate_case)),
        axis=1
    )
    columns_to_save = ["honest_difference", "median", "e_m_fin", "median_price_deviation",
                       "d_ori", "e_d_fin", "dolev_price_deviation"]
    df_samples_save = df_samples[columns_to_save]
    df_samples_save = df_samples_save.map(lambda x: x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    # Saving and the choice of storage path are at your discretion.
    # df_samples_save.to_csv(f"{simulate_case}_top{top_k}_comparison.csv", index=False)
    fig_x = df_samples_save["median"].astype(float)
    fig_y1 = df_samples_save["median_price_deviation"].astype(float)
    fig_y2 = df_samples_save["dolev_price_deviation"].astype(float)
    matplotlib.use('TkAgg')
    plt.figure(figsize=(10, 6))
    plt.scatter(fig_x, fig_y1, color="blue", alpha=0.6, label="Median Aggregation")
    plt.scatter(fig_x, fig_y2, color="red", alpha=0.6, label="Dolev Aggregation")
    plt.xlabel("Historical Price (USD)")
    plt.ylabel("Price Deviation (USD)")
    plt.title("Comparison of Price Deviation Distributions")
    plt.legend()
    plt.xticks(rotation=60, ha='right', rotation_mode='anchor')
    plt.tight_layout()
    plt.show()
