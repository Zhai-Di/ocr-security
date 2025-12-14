import pandas as pd
import math
from decimal import Decimal, ROUND_HALF_UP
import os


def calculate_scenario_1_max_uncertainty(row, l, f):
    max_inflation_index = math.floor(l / 2) + f
    max_deflation_index = math.floor(l / 2) - f
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    max_uncertainty = row[max_inflation_col] - row[max_deflation_col]
    return max_uncertainty


def calculate_scenario_2_max_uncertainty(row, l, f):
    max_inflation_index = 3 * f
    max_deflation_index = 0
    max_inflation_col = "ob" + str(max_inflation_index)
    max_deflation_col = "ob" + str(max_deflation_index)
    max_uncertainty = row[max_inflation_col] - row[max_deflation_col]
    return max_uncertainty


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
    l = 31
    f = 10
    # Simulating under scenario x requires setting x in calculate_scenario_x_max_uncertainty(row, l, f)
    df_obs["max_uncertainty"] = df_obs.apply(lambda row: calculate_scenario_2_max_uncertainty(row, l, f), axis=1)
    df_obs["median"] = df_obs["median"].apply(lambda x: Decimal(str(x)))
    df_obs["honest_difference"] = df_obs["honest_difference"].apply(lambda x: Decimal(str(x)))
    df_obs["max_uncertainty"] = df_obs["max_uncertainty"].apply(lambda x: Decimal(str(x)))
    df_obs["uncertainty_ratio"] = df_obs.apply(lambda row: row["max_uncertainty"] / row["median"], axis=1)
    df_obs["uncertainty_ratio"] = df_obs["uncertainty_ratio"].apply(lambda x: x.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP))
    df_obs["ratio_to_honest_range"] = df_obs.apply(lambda row: row["max_uncertainty"] / row["honest_difference"], axis=1)
    df_obs["ratio_to_honest_range"] = df_obs["ratio_to_honest_range"].apply(lambda x: x.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP))
    percentiles = [0.00005, 0.0001, 0.001, 0.01, 0.1]
    n = len(df_obs)
    calculate_thresholds(df_obs["max_uncertainty"], "max_uncertainty", percentiles, n)
    calculate_thresholds(df_obs["uncertainty_ratio"], "uncertainty_ratio", percentiles, n)
    calculate_thresholds(df_obs["ratio_to_honest_range"], "ratio_to_honest_range", percentiles, n)