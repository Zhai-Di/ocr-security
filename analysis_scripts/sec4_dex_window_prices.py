import pandas as pd
from tqdm import tqdm
import numpy as np

half_window = 6
honest_lists = pd.read_csv("../data/eth_usd_honest_lists.csv")
df_uni = pd.read_csv("../data/uni_prices.csv")
results = []
for block in tqdm(honest_lists["blockNumber"], desc="Processing windows"):
    wd_dict = {}
    wd_dict["blockNumber"] = block
    low, high = block - half_window, block + half_window
    window_prices = df_uni.loc[
        (df_uni["block_number"] >= low) & (df_uni["block_number"] <= high),
        "price"
    ]
    if len(window_prices) > 0:
        wd_dict["wd_min"] = window_prices.min()
        wd_dict["wd_max"] = window_prices.max()
        wd_dict["wd_difference"] = wd_dict["wd_max"] - wd_dict["wd_min"]
    else:
        wd_dict["wd_min"] = np.nan
        wd_dict["wd_max"] = np.nan
        wd_dict["wd_difference"] = np.nan
    results.append(wd_dict)
df_result = pd.DataFrame(results)
df_result.to_csv("../data/uni_window_prices.csv", index=False)