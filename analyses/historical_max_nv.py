import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker
from decimal import Decimal, ROUND_HALF_UP
import os


def calculate_ratio(row, col_1, col_2):
    str_col_1 = str(row[col_1])
    str_col_2 = str(row[col_2])
    div_tmp_1 = Decimal(str_col_1) / Decimal(str_col_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def compute_difference_bound(row, f):
    differences = []
    for i in range(f + 1):
        ob_high = "ob" + str(i + 2 * f)
        ob_low = "ob" + str(i)
        differences.append(row[ob_high] - row[ob_low])
    return min(differences)


def apply_difference_bound(row):
    f = 10
    return compute_difference_bound(row, f)


def apply_difference_bound_ratio(row):
    col_1 = 'difference_bound'
    col_2 = 'median'
    return calculate_ratio(row, col_1, col_2)


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    read_file_path = os.path.join(current_dir, "..", "data", "observations_31_exp.csv")
    df = pd.read_csv(read_file_path)
    df['difference_bound'] = df.apply(apply_difference_bound, axis=1)
    df['difference_bound_ratio'] = df.apply(apply_difference_bound_ratio, axis=1)
    row_max_difference_bound = df.loc[df['difference_bound'].idxmax()]
    print("the max difference_bound")
    print("difference_bound", row_max_difference_bound['difference_bound'])
    print("difference_bound_ratio", row_max_difference_bound['difference_bound_ratio'])
    print("median", row_max_difference_bound['median'])
    print("transactionHash", row_max_difference_bound['transactionHash'])
    print("\n-------------------------\n")
    row_max_difference_bound_ratio = df.loc[df['difference_bound_ratio'].idxmax()]
    print("the max difference_bound_ratio")
    print("difference_bound", row_max_difference_bound_ratio['difference_bound'])
    print("difference_bound_ratio", row_max_difference_bound_ratio['difference_bound_ratio'])
    print("median", row_max_difference_bound_ratio['median'])
    print("transactionHash", row_max_difference_bound_ratio['transactionHash'])
