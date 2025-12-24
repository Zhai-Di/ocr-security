import pandas as pd
import math
from decimal import Decimal, ROUND_HALF_UP


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


def calculate_distributions(series, metric_str):
    sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
    print(f"\n=== The distribution of {metric_str} ===")
    print(f"The maximum of {metric_str} is {series.max()}")
    percents = [0.0001, 0.001, 0.01, 0.1]
    len_s = len(sorted_series)
    for p in percents:
        idx = max(math.ceil(len_s * p) - 1, 0)
        val = sorted_series.iloc[idx]
        print(f"{p * 100:.3f}% is greater than or equal to {val}, with index {idx}")
        print()


if __name__ == "__main__":
    obs_file_path = "../data/bnb_usd_honest_lists.csv"
    df_obs = pd.read_csv(obs_file_path)
    l = 16
    f = 5
    df_obs["max_variability"] = df_obs.apply(lambda row: calculate_scenario_2_max_variability(row, l, f), axis=1)
    df_obs["median"] = df_obs["median"].apply(lambda x: Decimal(str(x)))
    df_obs["honest_difference"] = df_obs["honest_difference"].apply(lambda x: Decimal(str(x)))
    df_obs["max_variability"] = df_obs["max_variability"].apply(lambda x: Decimal(str(x)))
    df_obs["variability_ratio"] = df_obs.apply(lambda row: row["max_variability"] / row["median"], axis=1)
    df_obs["variability_ratio"] = df_obs["variability_ratio"].apply(lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    df_obs["ratio_to_honest_range"] = df_obs.apply(lambda row: row["max_variability"] / row["honest_difference"], axis=1)
    df_obs["ratio_to_honest_range"] = df_obs["ratio_to_honest_range"].apply(lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    n = len(df_obs)
    print(f"len(bnb_honest_lists) = {n}")
    ratio_col = df_obs["variability_ratio"]
    calculate_distributions(ratio_col, "metric_2")