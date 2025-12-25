import pandas as pd
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from web3 import Web3
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
from eth_abi import decode
import os
import signal, sys


def handle_sigint(sig, frame):
    print("\nDetected interrupt signal. Exiting immediately...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)


def fetch_sync_prices(w3, from_block, to_block, pool_address, topic, dec0, dec1):
    log_filter = w3.eth.filter(
        {"fromBlock": from_block, "toBlock": to_block,
         "address": Web3.to_checksum_address(pool_address), "topics": [topic]}
    )
    results = w3.eth.get_filter_logs(log_filter.filter_id)
    print(f"Fetched {len(results)} log entries in block {from_block} to {to_block}")
    results_list = []
    for r in results:
        result_dict = {}
        result_dict["block_number"] = r["blockNumber"]
        reserve0, reserve1 = decode(["uint112", "uint112"], bytes(r["data"]))
        scaled_res0 = Decimal(reserve0) / (Decimal(10) ** dec0)
        scaled_res1 = Decimal(reserve1) / (Decimal(10) ** dec1)
        price_token0_in_token1 = (scaled_res1 / scaled_res0) if scaled_res0 != 0 else np.nan
        price_token0_in_token1 = float(
            price_token0_in_token1.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        )
        result_dict["price"] = price_token0_in_token1
        results_list.append(result_dict)
    df = pd.DataFrame(results_list)
    return df


# def save_to_csv(df, write_path, write_mode, write_header):
#     df.to_csv(write_path, mode=write_mode, header=write_header, index=False)


def safe_fetch(index, blk_range, w3, pool_address, topic, dec0, dec1):
    from_blk, to_blk = blk_range
    retry = 0
    while retry < 6:
        try:
            df = fetch_sync_prices(w3, from_blk, to_blk, pool_address, topic, dec0, dec1)
            return index, df
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Too Many Requests" in err_str:
                print(f"Rate limit hit at block {from_blk}-{to_blk}, retrying {retry+1}/6)")
                time.sleep(1)
                retry += 1
            else:
                print(f"Error fetching blocks {from_blk}-{to_blk}  {err_str}")
                break
    return index, None


if __name__ == "__main__":
    PAIR_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "getReserves",
            "outputs": [
                {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
                {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
                {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"},
            ],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "token0",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "token1",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    pool_address = "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852"
    topic = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
    # Replace the infura_key below with a specific Infura key
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/infura_key"))
    pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=PAIR_ABI)
    token0_addr = pool.functions.token0().call()
    token1_addr = pool.functions.token1().call()
    tok0 = w3.eth.contract(address=token0_addr, abi=ERC20_ABI)
    tok1 = w3.eth.contract(address=token1_addr, abi=ERC20_ABI)
    dec0 = tok0.functions.decimals().call()
    dec1 = tok1.functions.decimals().call()
    sym0 = tok0.functions.symbol().call()
    sym1 = tok1.functions.symbol().call()
    print(f"Pair loaded {sym0}/{sym1}, decimals = {dec0}/{dec1}")
    all_lists = pd.read_csv("../data/eth_usd_observations.csv")
    all_lists["blockNumber"] = all_lists["blockNumber"].astype(int)
    start_block = all_lists["blockNumber"].min() - 6
    end_block = all_lists["blockNumber"].max() + 6
    batch_size = int(1000)
    block_ranges = []
    from_block = start_block
    while from_block <= end_block:
        to_block = min(from_block + batch_size, end_block)
        block_ranges.append((int(from_block), int(to_block)))
        from_block = to_block + 1
    print(f"Total {len(block_ranges)} batches from {start_block} to {end_block}")
    temp_dir = "../data/uni_batches"
    os.makedirs(temp_dir, exist_ok=True)
    def fetch_and_save(index, blk_range):
        idx, df = safe_fetch(index, blk_range, w3, pool_address, topic, dec0, dec1)
        if df is not None and not df.empty:
            temp_path = f"{temp_dir}/batch_{idx:05d}.csv"
            df.to_csv(temp_path, index=False)
        return idx
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, blk_range in enumerate(block_ranges):
            futures.append(executor.submit(fetch_and_save, i, blk_range))

        for _ in tqdm(futures, desc="Fetching Sync logs"):
            _.result()
    write_path = "../data/uni_prices.csv"
    csv_files = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".csv")])
    print(csv_files)
    df_all = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    df_all.to_csv(write_path, index=False)
    print(f"\nAll {len(csv_files)} batches merged into {write_path}")