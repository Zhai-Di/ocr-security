import itertools
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import math
from functools import reduce
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json


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


# # 下面的函数中参数row中的元素默认是float类型的变量
# def simulate_falsification(row, f):
#     num_obs = len(row)
#     falsify_value = Decimal("1500.0")
#     indices = list(range(num_obs))
#     combinations = list(itertools.combinations(indices, f))
#     print(f"The number of combinations is {len(combinations)}")
#     inflation_list = []
#     deflation_list = []
#     row = row.apply(lambda x: Decimal(str(x)))
#     for comb in combinations:
#         inflation_row = row.copy()
#         deflation_row = row.copy()
#         for idx in comb:
#             # 下面的代码要改成计算metric 2的，针对每一个falsifying idx的组合，分别计算inflation和deflation之间的差距，得出最大值
#             # 这个函数最终要生成两个df，一个df是inflation的，一个df是deflation的
#             # inflation df和deflation df中，索引相同的行对应的是同一组comb，在下面的代码中遍历到一组comb时，先后生成inflation和deflation的行
#             inflation_row.iloc[idx] += falsify_value
#             deflation_row.iloc[idx] -= falsify_value
#         # falsified_list.append(new_row)
#         inflation_list.append(inflation_row)
#         deflation_list.append(deflation_row)
#     return pd.DataFrame(inflation_list), pd.DataFrame(deflation_list)


def dolev_func(row, f, k):
    sorted_row = row.sort_values().reset_index(drop=True)
    if 2 * f >= len(sorted_row):
        raise ValueError("the length of row is less than or equal to 2 * f")
    reduced_row = sorted_row[f: len(sorted_row) - f].reset_index(drop=True)
    j = math.floor((len(reduced_row) - 1) / k)
    selected_values = [reduced_row[i * k] for i in range(j + 1)]
    total = reduce(lambda x, y: x + y, selected_values)
    # mean = total / len(selected_values)
    if isinstance(total, Decimal):
        mean = total / Decimal(len(selected_values))
    else:
        mean = total / len(selected_values)
    return mean


# worker 函数（单个组合上运行）
def process_comb(args):
    row, comb, f, k, falsify_value = args
    inflation_row = row.copy()
    deflation_row = row.copy()
    for idx in comb:
        inflation_row.iloc[idx] += falsify_value
        deflation_row.iloc[idx] -= falsify_value
    inflation_v = dolev_func(inflation_row, f, k)
    deflation_v = dolev_func(deflation_row, f, k)
    dolev_d = inflation_v - deflation_v
    return dolev_d, comb


def dolev_uncertainty(row, f, k):
    row = row.apply(lambda x: Decimal(str(x)))
    num_obs = len(row)
    falsify_value = Decimal("1500.0")
    indices = list(range(num_obs))
    combinations = list(itertools.combinations(indices, f))
    print(f"Total combinations = {len(combinations)}")
    print(f"Using {cpu_count()} CPU cores")
    # 准备参数
    args_list = [(row, comb, f, k, falsify_value) for comb in combinations]
    max_dolev_d = Decimal("-Infinity")
    best_comb = None
    with Pool(cpu_count()) as p:
        for dolev_d, comb in tqdm(
            p.imap(process_comb, args_list, chunksize=200),
            total=len(combinations),
            desc="Running parallel simulation"
        ):
            if dolev_d > max_dolev_d:
                max_dolev_d = dolev_d
                best_comb = comb
    return max_dolev_d, best_comb


def median_uncertainty(row, l, f):
    max_inflation_index = math.floor(l / 2) + f
    max_deflation_index = math.floor(l / 2) - f
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    m_uncertainty = row[max_inflation_col] - row[max_deflation_col]
    return Decimal(str(m_uncertainty))


if __name__ == "__main__":
    read_path = "/home/zd/CodeFromZD/EmpCode/data/honest_observations.csv"
    df_obs = pd.read_csv(read_path)
    total_rows = len(df_obs)
    # top_k = math.floor(total_rows * 0.005)
    top_k = 200
    df_samples = df_obs.sort_values(by="honest_difference", ascending=False).head(top_k)
    ob_value_columns = [f"ob{i}" for i in range(31)]
    dolev_columns = df_samples[ob_value_columns]
    dolev_columns = dolev_columns.apply(lambda row: uniformly_drop(row, 6), axis=1)
    df_samples[["dolev_uncertainty", "dolev_positions"]] = dolev_columns.apply(
        lambda row: pd.Series(dolev_uncertainty(row, 6, 6)),
        axis=1
    )
    # df_samples["dolev_positions"] = df_samples["dolev_positions"].apply(lambda x: json.dumps(x))
    df_samples["median_uncertainty"] = dolev_columns.apply(
        lambda row: median_uncertainty(row, 25, 6),
        axis=1
    )
    df_samples["dolev_bound"] = df_samples["honest_difference"].apply(
        lambda x: Decimal(str(x)) / Decimal(3)
    )
    values_to_save = ["dolev_uncertainty", "dolev_bound", "median_uncertainty"]
    info_to_save = ["blockNumber", "transactionHash","dolev_positions"]
    for col in values_to_save:
        df_samples[col] = df_samples[col].apply(
            lambda x: x.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        )
    columns_to_save = values_to_save + info_to_save
    df_samples[columns_to_save].to_csv(f"major_top{top_k}_5f+1.csv", index=False)