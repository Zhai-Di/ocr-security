from web3 import Web3
from eth_abi import decode
from decimal import Decimal, ROUND_HALF_UP
import csv
from hexbytes import HexBytes


def exact_divide(op_1, op_2, str_dec):
    div_tmp_1 = Decimal(op_1) / Decimal(op_2)
    div_tmp_2 = div_tmp_1.quantize(Decimal(str_dec), rounding=ROUND_HALF_UP)
    div_final_r = float(div_tmp_2)
    return div_final_r


def write_to_csv(file_name, mode, record):
    try:
        with open(file_name, mode=mode, encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(record)
    except Exception as e:
        print("ERROR during writing csv")


def save_to_csv():
    # replace infura-api-key to your infura api key
    # follow the link https://docs.metamask.io/services/get-started/infura/ to obtain an infura api key
    web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/infura-api-key"))
    info_list = []
    info_header = []
    with open("../data/AggStartBlock.csv", newline="") as f_read:
        reader = csv.reader(f_read)
        info_header.extend(next(reader))
        print(info_header)
        for row in reader:
            info_list.append(row)
    for info in info_list:
        pair_name = info[0].replace(" / ", "-")
        oracle_number = int(info[2])
        bzt_number = oracle_number // 3
        sup_majority = oracle_number - bzt_number
        neg_index = -bzt_number - 1
        print(f"The neg_index of {pair_name} pair is {neg_index}")
        decimals = info[5]
        current_agg = info[7]
        stale_agg = info[11]
        # To facilitate unified processing later, startBlock_0 refers to the starting block number of phase0 collecting
        if info[15] == "NaN":
            startBlock_0 = int(info[14])
        else:
            startBlock_0 = int(info[15])
        endBlock_0 = int(info[14])
        startBlock_1 = int(info[14]) + 1
        # finalized or a specific block number? It should be an int
        endBlock_1 = "finalized"
        fromBlock_0 = startBlock_0
        toBlock_0 = fromBlock_0 + 10000
        dec = 10 ** int(decimals)
        csv_header = ["blockNumber", "transactionHash", "median", "transmitter", "obs_len", "order"]
        for ind in range(oracle_number):
            str_ind = "ob" + str(ind)
            csv_header.append(str_ind)
        cp_header = ["min_price", "max_price", "min_median", "median_max", "min_max", "weight_1", "weight_2", "weight_3"]
        csv_header.extend(cp_header)
        write_to_csv("../data/AllPairsEvents/" + pair_name + ".csv", 'w', csv_header)
        while fromBlock_0 <= endBlock_0:
            log_filter = web3.eth.filter(
                {"fromBlock": fromBlock_0, "toBlock": toBlock_0, "address": stale_agg,
                 "topics": ["0xf6a97944f31ea060dfde0566e4167c1a1082551e64b60ecb14d599a9d023d451"]})
            raw_r = web3.eth.get_filter_logs(log_filter.filter_id)
            cur_n = len(raw_r)
            print(f"{pair_name}, {cur_n} records in 10000 blocks")
            for r in raw_r:
                r_blockNumber = r["blockNumber"]
                raw_transactionHash = r["transactionHash"]
                r_transactionHash = raw_transactionHash.hex()
                raw_data = r["data"]
                bytes_r = bytes(raw_data)
                r_data = decode(["int192", "address", "int192[]", "bytes", "bytes32"], bytes_r)
                r_median = exact_divide(r_data[0], dec, "0.0000001")
                r_transmitter = r_data[1]
                rcd_list = [r_blockNumber, r_transactionHash, r_median, r_transmitter]
                obs = r_data[2]
                obs_len = len(obs)
                rcd_list.append(obs_len)
                r_order = False
                for i in range(obs_len - 1):
                    r_order = (obs[i] <= obs[i+1])
                    if not r_order:
                        break
                rcd_list.append(r_order)
                raw_ob_list = []
                obs_list = []
                for item_ob in obs:
                    raw_ob_list.append(item_ob)
                    r_ob = exact_divide(item_ob, dec, "0.0000001")
                    rcd_list.append(r_ob)
                    obs_list.append(r_ob)
                r_min = obs_list[bzt_number]
                # negative index from -1
                r_max = obs_list[neg_index]
                min_median = exact_divide(r_data[0] - raw_ob_list[bzt_number], dec, "0.0000001")
                median_max = exact_divide(raw_ob_list[neg_index] - r_data[0], dec, "0.0000001")
                min_max = exact_divide(raw_ob_list[neg_index] - raw_ob_list[bzt_number], dec, "0.0000001")
                weight_1 = exact_divide(r_data[0] - raw_ob_list[bzt_number], r_data[0], "0.0000001")
                weight_2 = exact_divide(raw_ob_list[neg_index] - r_data[0], r_data[0], "0.0000001")
                weight_3 = exact_divide(raw_ob_list[neg_index] - raw_ob_list[bzt_number], r_data[0], "0.0000001")
                cp_list = [r_min, r_max, min_median, median_max, min_max, weight_1, weight_2, weight_3]
                # Fill up to oracle_number observations
                if obs_len < oracle_number:
                    for j in range(obs_len, oracle_number):
                        rcd_list.append("NaN")
                rcd_list.extend(cp_list)
                write_to_csv("../data/AllPairsEvents/" + pair_name + ".csv", 'a', rcd_list)
            fromBlock_0 = toBlock_0 + 1
            toBlock_0 = min(fromBlock_0 + 10000, endBlock_0)
