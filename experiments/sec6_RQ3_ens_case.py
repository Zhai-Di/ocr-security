import math
import pandas as pd
import numpy as np
from eth_abi import decode
from decimal import Decimal, ROUND_HALF_UP
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


def calculate_e_m_fin(row, index_func, l, f):
    _, p_k_distribution, p_i_fin_distribution = index_func(l, f)
    e_m_fin = Decimal(0)
    for key, value in p_i_fin_distribution.items():
        col_name = "ob" + str(key)
        str_col_value = str(row[col_name])
        e_m_fin = e_m_fin + value * Decimal(str_col_value)
    e_m_fin = e_m_fin.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP)
    return e_m_fin


def is_string(value):
    return isinstance(value, str)


def checkCall(df):
    df_filtered = df[df["input"].str.startswith("0x50e9a715")]
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered


def decodeOutput(row):
    try:
        raw_rt = row["output"]
        decode_rt = decode(["uint256"], bytes.fromhex(raw_rt[2:]))
        rt = decode_rt[0]
        return rt
    except Exception as e:
        return np.nan


def matchPriceFeed(total_oracles, df_obs, df_trace, case_type_str):
    l = total_oracles
    f = math.floor(total_oracles / 3)
    if case_type_str == "deflation":
        df_obs["e_m_fin_scn_1"] = df_obs.apply(lambda row: calculate_e_m_fin(row, scenario_1_index_deflation, l, f), axis=1)
        df_obs["e_m_fin_scn_2"] = df_obs.apply(lambda row: calculate_e_m_fin(row, scenario_2_index_deflation, l, f), axis=1)
    else:
        df_obs["e_m_fin_scn_1"] = df_obs.apply(lambda row: calculate_e_m_fin(row, scenario_1_index_inflation, l, f), axis=1)
        df_obs["e_m_fin_scn_2"] = df_obs.apply(lambda row: calculate_e_m_fin(row, scenario_2_index_inflation, l, f), axis=1)
    for i in df_obs.index:
        m_ori = df_obs.at[i, "median"]
        e_m_fin_scn_1 = df_obs.at[i, "e_m_fin_scn_1"]
        e_m_fin_scn_2 = df_obs.at[i, "e_m_fin_scn_2"]
        amplify = 10 ** 8
        m_ori = int(m_ori * amplify)
        e_m_fin_scn_1 = e_m_fin_scn_1 * Decimal(amplify)
        e_m_fin_scn_2 = e_m_fin_scn_2 * Decimal(amplify)
        cur_block = df_obs.at[i, "blockNumber"]
        next_block = df_obs.at[i, "next_feed_block"]
        df_trace.loc[(df_trace["block_number"] >= cur_block) & (df_trace["block_number"] < next_block),
                     ["m_ori", "e_m_fin_scn_1", "e_m_fin_scn_2"]] = [m_ori, e_m_fin_scn_1, e_m_fin_scn_2]
    return df_trace


def profitCalculate(row, col_return, case_type_str):
    rt_wei = int(row[col_return])
    ratio_scn_1 = Decimal(row["m_ori"]) / row["e_m_fin_scn_1"]
    ratio_scn_2 = Decimal(row["m_ori"]) / row["e_m_fin_scn_2"]
    deviation_ratio_scn_1 = None
    deviation_ratio_scn_2 = None
    if case_type_str == "deflation":
        deviation_ratio_scn_1 = ratio_scn_1 - Decimal(1)
        deviation_ratio_scn_2 = ratio_scn_2 - Decimal(1)
    else:
        deviation_ratio_scn_1 = Decimal(1) - ratio_scn_1
        deviation_ratio_scn_2 = Decimal(1) - ratio_scn_2
    deviation_wei_scn_1 = Decimal(rt_wei) * deviation_ratio_scn_1
    deviation_wei_scn_2 = Decimal(rt_wei) * deviation_ratio_scn_2
    deviation_eth_scn_1 = deviation_wei_scn_1 / Decimal(10 ** 18)
    deviation_eth_scn_2 = deviation_wei_scn_2 / Decimal(10 ** 18)
    deviation_eth_scn_1 = deviation_eth_scn_1.quantize(Decimal("0.00000000000000001"), rounding=ROUND_HALF_UP)
    deviation_eth_scn_2 = deviation_eth_scn_2.quantize(Decimal("0.00000000000000001"), rounding=ROUND_HALF_UP)
    return deviation_eth_scn_1, deviation_eth_scn_2


def calculate_accumulated_deviations(obs_data_path, traces_data_path, total_oracles, case_type_str):
    df_obs = pd.read_csv(obs_data_path)
    df_trace = pd.read_csv(traces_data_path)
    pre_len = len(df_trace)
    df_trace = df_trace[df_trace['output'].apply(is_string)]
    df_trace.reset_index(drop=True, inplace=True)
    print(f"df_trace.apply(is_string) filtered {len(df_trace) - pre_len} rows from df_trace")
    pre_len = len(df_obs)
    df_obs = df_obs[df_obs["blockNumber"] >= 14678295]
    df_obs.reset_index(drop=True, inplace=True)
    print(f"blockNumber >= 14678295 filtered {len(df_obs) - pre_len} rows from df_obs")
    pre_len = len(df_trace)
    df_trace = df_trace[df_trace["block_number"] < 22648260]
    df_trace.reset_index(drop=True, inplace=True)
    print(f"block_number < 22648260 filtered {len(df_trace) - pre_len} rows from df_trace")
    pre_len = len(df_trace)
    df_trace = checkCall(df_trace)
    print(f"checkCall(df_trace) filtered {len(df_trace) - pre_len} rows from df_trace")
    pre_len = len(df_trace)
    df_trace["return_wei"] = df_trace.apply(decodeOutput, axis=1)
    df_trace.dropna(inplace=True)
    print(f"decodeOutput filtered {len(df_trace) - pre_len} rows from df_trace")
    pre_len = len(df_trace)
    df_case = matchPriceFeed(total_oracles, df_obs, df_trace, case_type_str)
    df_case.dropna(inplace=True)
    df_case.reset_index(drop=True, inplace=True)
    print(f"matchPriceFeed filtered {len(df_case) - pre_len} rows from df_case")
    print(f"len(df_case) = {len(df_case)}")
    df_case[['deviation_eth_scn_1', 'deviation_eth_scn_2']] = df_case.apply(
        lambda row: pd.Series(profitCalculate(row, 'return_wei', case_type_str)), axis=1
    )
    accumulated_deviations_scn_1 = df_case["deviation_eth_scn_1"].sum()
    accumulated_deviations_scn_2 = df_case["deviation_eth_scn_2"].sum()
    return accumulated_deviations_scn_1, accumulated_deviations_scn_2


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    obs_file_path = os.path.join(current_dir, "..", "data", "honest_observations.csv")
    # The corresponding traces dataset is available at https://github.com/SecurityDON/Artifact/blob/main/data/ens_case_data.7z.001
    # After downloading and extracting the traces dataset, replace xxx below with the path where you have stored it.
    traces_file_path = "xxx"
    oracles = 31
    type_str = "deflation"
    eth_usd_price = Decimal("2425.31")
    scenario_1_result, scenario_2_result = calculate_accumulated_deviations(obs_file_path, traces_file_path,
                                                                            oracles, type_str)
    print(f"Experimental results for the {type_str} case.")
    print(f"scenario 1 accumulated ETH deviations   {scenario_1_result} ETH")
    print(f"scenario 1 accumulated USD deviations   {scenario_1_result * eth_usd_price} USD")
    print(f"scenario 2 accumulated ETH deviations   {scenario_2_result} ETH")
    print(f"scenario 2 accumulated USD deviations   {scenario_2_result * eth_usd_price} USD")