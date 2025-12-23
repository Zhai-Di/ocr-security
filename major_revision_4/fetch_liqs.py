import requests
import csv
from decimal import Decimal

# Aave v2 Subgraph (你提供的 gateway 入口)
url = "https://gateway.thegraph.com/api/2152074aff2ae7dfd8e1a606ba85095a/subgraphs/id/8wR23o1zkS4gpLqLNU4kG3JHYVucqGyopL5utGxP2q1N"

# 查询起止的时间戳（已改为你指定的范围）
timestamp_start = 1615571506  # 起始时间戳
timestamp_end = 1749245663    # 结束时间戳

BATCH_WRITE_SIZE = 1000
OUTPUT_FILE = "../data/liq_data.csv"

# GraphQL 查询模板
query_template = f"""
query ($skip: Int!) {{
  liquidationCalls(
    first: 1000,
    skip: $skip,
    where: {{
      timestamp_gte: {timestamp_start},
      timestamp_lte: {timestamp_end}
    }}
  ) {{
    id
    txHash
    timestamp
    user {{ id }}
    collateralReserve {{ symbol decimals }}
    collateralAmount
    collateralAssetPriceUSD
    principalReserve {{ symbol decimals }}
    principalAmount
    borrowAssetPriceUSD
  }}
}}
"""


def fetch_liquidations():
    skip = 0
    first_write = True  # 控制 CSV 首次写入 header
    while True:
        results = []
        response = requests.post(url, json={'query': query_template, 'variables': {"skip": skip}})
        data = response.json()
        if "errors" in data:
            print("GraphQL 错误:", data["errors"])
            break
        liquidation_calls = data.get("data", {}).get("liquidationCalls", [])
        if not liquidation_calls:
            break  # 数据抓取完成
        for call in liquidation_calls:
            collateral_symbol = call["collateralReserve"]["symbol"]
            debt_symbol = call["principalReserve"]["symbol"]
            collateral_decimals = int(call["collateralReserve"]["decimals"])
            collateral_amount = Decimal(call["collateralAmount"]) / (Decimal(10) ** collateral_decimals)
            debt_decimals = int(call["principalReserve"]["decimals"])
            debt_amount = Decimal(call["principalAmount"]) / (Decimal(10) ** debt_decimals)
            results.append({
                "id": call["id"],
                "txHash": call["txHash"],
                "timestamp": call["timestamp"],
                "userId": call["user"]["id"],
                "collateralAsset": collateral_symbol,
                "collateralAmount": float(collateral_amount),
                "collateralPriceUSD": float(Decimal(call["collateralAssetPriceUSD"])),
                "debtAsset": debt_symbol,
                "debtAmount": float(debt_amount),
                "debtPriceUSD": float(Decimal(call["borrowAssetPriceUSD"]))
            })
        write_batch_to_csv(results, OUTPUT_FILE, first_write)
        first_write = False
        skip += 1000


def write_batch_to_csv(rows, filename, write_header):
    """写入一批 rows 到 CSV，返回写入条数"""
    mode = "w" if write_header else "a"
    with open(filename, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    print(f"写入 {len(rows)} 条数据，header={write_header}")


if __name__ == "__main__":
    fetch_liquidations()