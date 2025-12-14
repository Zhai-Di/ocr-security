import pandas as pd
import os


current_dir = os.path.dirname(__file__)
read_file_path = os.path.join(current_dir, "..", "data", "all_observations.csv")
write_file_path = os.path.join(current_dir, "..", "data", "observations_31_exp.csv")
ori_df = pd.read_csv(read_file_path)
ori_df['next_feed_block'] = ori_df['blockNumber'].shift(-1)
next_feed_df = ori_df[:-1].copy()
desired_columns = [
    'blockNumber', 'next_feed_block', 'transactionHash', 'median', 'transmitter', 'obs_len', 'order',
    'ob0', 'ob1', 'ob2', 'ob3', 'ob4', 'ob5', 'ob6', 'ob7', 'ob8', 'ob9', 'ob10',
    'ob11', 'ob12', 'ob13', 'ob14', 'ob15', 'ob16', 'ob17', 'ob18', 'ob19', 'ob20',
    'ob21', 'ob22', 'ob23', 'ob24', 'ob25', 'ob26', 'ob27', 'ob28', 'ob29', 'ob30'
]
reserved_columns = [col for col in desired_columns if col in next_feed_df.columns]
next_feed_df = next_feed_df[reserved_columns]
with_31ob_df = next_feed_df[next_feed_df["obs_len"] == 31].copy()
with_31ob_df.to_csv(write_file_path, index=False)
print("completed")