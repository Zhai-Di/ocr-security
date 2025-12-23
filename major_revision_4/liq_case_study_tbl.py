import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# 下面是scenario 1 下的计算数据
# read_path = "../data/liq_case_scn_1.csv"
# 下面是scenario 2 下的计算数据
read_path = "../data/liq_case_scn_2.csv"
print(f"read_path = {read_path}")
df = pd.read_csv(read_path)
usd_price = Decimal("3230.3202218")
data_columns = ["max_inflation_difference", "e_inflation_difference", "min_deflation_difference", "e_deflation_difference"]
for col in data_columns:
    col_sum = Decimal("0")
    for x in df[col]:
        col_sum += Decimal(str(x))
    col_sum_rounded = float(col_sum.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    print(f"total amount of column {col}   {col_sum_rounded} WETH")
    usd_sum = (col_sum * usd_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print(f"total price of column {col}in usd   {usd_sum} USD")
