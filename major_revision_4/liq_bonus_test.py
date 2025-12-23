import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# 1. 读取原始CSV
df_0 = pd.read_csv("../data/liq_data.csv")

# 2. 筛选 collateralAsset=WETH 且 debtAsset ∈ {USDC, USDT}
# 以下是liq_data_test.csv的过滤条件
# df_1 = df_0[
#     (df_0["collateralAsset"] == "WETH") &
#     (df_0["debtAsset"].isin(["DAI", "USDC", "USDT"]))
# ].copy().reset_index(drop=True)

# 以下是liq_data_test2.csv的过滤条件
# df_1 = df_0[
#     (df_0["collateralAsset"].isin(["USDC", "USDT"])) &
#     (df_0["debtAsset"] == "WETH")
# ].copy().reset_index(drop=True)

# 以下是liq_data_test3.csv和weth_liqs.csv的过滤条件
df_1 = df_0[df_0["collateralAsset"] == "WETH"].copy().reset_index(drop=True)

# 4. 计算清算奖金比例（liq_bonus_ratio）
#    ratio = (collateralAmount * collateralPriceUSD) / (debtAmount * debtPriceUSD)
def calc_ratio(row):
    collateral_amount = Decimal(str(row["collateralAmount"]))
    collateral_price = Decimal(str(row["collateralPriceUSD"]))
    debt_amount = Decimal(str(row["debtAmount"]))
    debt_price = Decimal(str(row["debtPriceUSD"]))
    numerator = collateral_amount * collateral_price
    denominator = debt_amount * debt_price
    # 防止除零
    if denominator == 0:
        return float("nan")
    ratio = numerator / denominator
    ratio = ratio.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    return float(ratio)


df_1["liq_bonus_ratio"] = df_1.apply(calc_ratio, axis=1)

# 5. 写入CSV文件
df_1.to_csv("../data/weth_liqs.csv", index=False)

# 6. 检查是否所有数值相等
unique_values = df_1["liq_bonus_ratio"].dropna().unique()

if len(unique_values) == 1:
    print("所有清算比率(liq_bonus_ratio)都相等。")
    print("清算比率数值为:", unique_values)
else:
    print("清算比率(liq_bonus_ratio)不全部相等。")
    print("不同的比率数值如下:", unique_values)