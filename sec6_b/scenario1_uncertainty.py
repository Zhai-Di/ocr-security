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


def calculate_thresholds(series, col_name, percents, len_df):
    sorted_series = series.sort_values(ascending=False).reset_index(drop=True)
    if col_name == "max_variability":
        print("distribution of price deviations (USD)")
    else:
        print("distribution of price deviation ratios")
    print()
    for p in percents:
        idx = max(math.ceil(len_df * p) - 1, 0)
        val = sorted_series.iloc[idx]
        print(f"{p * 100:.3f}%     {val}")
        print()


if __name__ == "__main__":
    obs_file_path = "../data/eth_usd_honest_lists.csv"
    df_obs = pd.read_csv(obs_file_path)
    l = 31
    f = 10
    df_obs["max_variability"] = df_obs.apply(lambda row: calculate_scenario_1_max_variability(row, l, f), axis=1)
    df_obs["median"] = df_obs["median"].apply(lambda x: Decimal(str(x)))
    df_obs["max_variability"] = df_obs["max_variability"].apply(lambda x: Decimal(str(x)))
    df_obs["variability_ratio"] = df_obs.apply(lambda row: row["max_variability"] / row["median"], axis=1)
    df_obs["max_variability"] = df_obs["max_variability"].apply(lambda x: x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    df_obs["variability_ratio"] = df_obs["variability_ratio"].apply(lambda x: x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    percentiles = [0.00005, 0.0001, 0.001, 0.01, 0.1]
    n = len(df_obs)
    calculate_thresholds(df_obs["max_variability"], "max_variability", percentiles, n)
    calculate_thresholds(df_obs["variability_ratio"], "variability_ratio", percentiles, n)