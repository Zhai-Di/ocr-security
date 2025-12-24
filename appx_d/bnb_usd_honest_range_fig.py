import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


if __name__ == "__main__":
    read_file_path = "../data/bnb_usd_honest_lists.csv"
    df_obs = pd.read_csv(read_file_path)
    matplotlib.use('TkAgg')
    plt.rcParams['font.family'] = 'Arial'
    plt.figure(figsize=(5, 4), dpi=150)
    fig_x = df_obs['blockNumber']
    fig_y = df_obs["honest_difference_ratio"]
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    plt.scatter(fig_x, fig_y, color=colors[4], s=10, marker='o', alpha=0.8)
    plt.xlim([min(fig_x), max(fig_x)])
    plt.ylim([min(fig_y), max(fig_y) + 0.002])
    print(f"xlim is [{min(fig_x)}, {max(fig_x)}]")
    x_min = int(min(fig_x))
    x_max = int(max(fig_x))
    range_span = x_max - x_min
    max_ticks = 20
    raw_step = max(1, range_span // (max_ticks - 1))
    step_rounded = ((raw_step + 9999) // 10000) * 10000
    tick_start = ((x_min + step_rounded - 1) // step_rounded) * step_rounded
    tick_end = (x_max // step_rounded) * step_rounded
    if tick_end < tick_start:
        xticks = np.array([tick_start])
    else:
        xticks = np.arange(tick_start, tick_end + 1, step=step_rounded)
    plt.xticks(ticks=xticks)
    plt.gca().set_xticklabels([str(x) for x in xticks], rotation=45, ha='right', rotation_mode='anchor', fontsize=12)
    plt.yticks(fontsize=16)
    plt.xlabel('block number', fontsize=16)
    plt.ylabel('width of the honest range', fontsize=16)
    plt.tick_params(axis='both', direction='in', width=1.5, length=6)
    plt.grid(True, which='both', linestyle='--', linewidth=0.9)
    plt.tight_layout()
    plt.show()