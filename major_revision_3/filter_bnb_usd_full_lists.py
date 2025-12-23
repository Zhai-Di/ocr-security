import pandas as pd


df_all = pd.read_csv("../data/bnb_usd_observations.csv")
df_full_lists = df_all[df_all["obs_len"] == 16].copy().reset_index(drop=True)
# df_full_lists.to_csv("../data/bnb_usd_full_lists.csv", index=False)
len_all_lists = len(df_all)
len_full_lists = len(df_full_lists)
print(f"The number of full lists is {len_full_lists}")
print(f"The fraction of full lists is {len_full_lists / len_all_lists}")
df_honest_lists = pd.read_csv("../data/bnb_usd_honest_lists.csv")
print(f"The number of honest lists is {len(df_honest_lists)}")