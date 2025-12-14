import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import os


def calculate_ratio(para_1, para_2):
    str_para_1 = str(para_1)
    str_para_2 = str(para_2)
    div_tmp_1 = Decimal(str_para_1) / Decimal(str_para_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def apply_calculate_ratio_min(row):
    para_1 = row["min_d_v"]
    para_2 = row["median"]
    return calculate_ratio(para_1, para_2)


def apply_calculate_ratio_max(row):
    para_1 = row["max_d_v"]
    para_2 = row["median"]
    return calculate_ratio(para_1, para_2)


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    read_file_path = os.path.join(current_dir, "..", "data", "observations_31_exp.csv")
    write_file_path = os.path.join(current_dir, "..", "data", "honest_observations.csv")
    df = pd.read_csv(read_file_path)
    f = 10
    df["min_d_v"] = df["ob" + str(f)] - df["ob0"]
    df["max_d_v"] = df["ob" + str(3 * f)] - df["ob" + str(2 * f)]
    df["min_d_ratio"] = df.apply(apply_calculate_ratio_min, axis=1)
    df["max_d_ratio"] = df.apply(apply_calculate_ratio_max, axis=1)
    bound = 0.0851
    filter_df = df[(df["min_d_ratio"] <= bound) & (df["max_d_ratio"] <= bound)].copy()
    filter_df["honest_difference"] = filter_df["ob30"] - filter_df["ob0"]
    filter_df.to_csv(write_file_path, index=False)
    print("completed")