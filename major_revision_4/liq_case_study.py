from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def eth_difference(row, c_price):
    d_amount = Decimal(str(row["debtAmount"]))
    d_price = Decimal(str(row["debtPriceUSD"]))
    c_amount = d_amount * d_price * Decimal("1.05") / c_price
    c_amount_difference = c_amount - Decimal(str(row["collateralAmount"]))
    c_amount_difference = c_amount_difference.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)
    return float(c_amount_difference)


if __name__ == '__main__':
    # 以下是区块范围[13179376, 13179389]在Scenario 1下的Byzantine price数据
    max_inflation_price = Decimal("3448.4879163")
    e_inflation_price = Decimal("3401.1658642")
    min_deflation_price = Decimal("3198.99")
    e_deflation_price = Decimal("3239.1833532")
    # 以下是区块范围[13179376, 13179389]在Scenario 2下的Byzantine price数据
    # max_inflation_price = Decimal("3510.3106409")
    # e_inflation_price = Decimal("3502.5447960")
    # min_deflation_price = Decimal("3076.7602584")
    # e_deflation_price = Decimal("3104.2914468")
    df = pd.read_csv("../data/liq_case_study.csv")
    df["max_inflation_difference"] = df.apply(
        lambda row: eth_difference(row, max_inflation_price), axis=1
    )
    df["e_inflation_difference"] = df.apply(
        lambda row: eth_difference(row, e_inflation_price), axis=1
    )
    df["min_deflation_difference"] = df.apply(
        lambda row: eth_difference(row, min_deflation_price), axis=1
    )
    df["e_deflation_difference"] = df.apply(
        lambda row: eth_difference(row, e_deflation_price), axis=1
    )
    selected_columns = ["txHash", "max_inflation_difference", "e_inflation_difference",
                        "min_deflation_difference", "e_deflation_difference"]
    # 以下是Scenario 1下的df
    df_scn_1 = df[selected_columns]
    df_scn_1.to_csv("../data/liq_case_scn_1.csv", index=False)
    # 以下是Scenario 2下的df
    # df_scn_2 = df[selected_columns]
    # df_scn_2.to_csv("../data/liq_case_scn_2.csv", index=False)