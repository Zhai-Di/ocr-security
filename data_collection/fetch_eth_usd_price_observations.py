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
    # A newly deployed contract will not be put into use immediately, and the fact that the end_block of the previous phase is equal to the start_block of the next phase will not cause any issues.
    phs_list = [
        [12007784, 12382429, "0xd3fCD40153E56110e6EEae13E12530e26C9Cb4fd",
         "0xf6a97944f31ea060dfde0566e4167c1a1082551e64b60ecb14d599a9d023d451"],
        [12382429, 16842888, "0x37bC7498f4FF12C19678ee8fE19d713b87F6a9e6",
         "0xf6a97944f31ea060dfde0566e4167c1a1082551e64b60ecb14d599a9d023d451"],
        [16842888, 19426589, "0xE62B71cf983019BFf55bC83B48601ce8419650CC",
         "0xf6a97944f31ea060dfde0566e4167c1a1082551e64b60ecb14d599a9d023d451"],
        [20773403, 21111778, "0x7d4E742018fb52E48b08BE73d041C18B21de6Fb5",
         "0xc797025feeeaf2cd924c99e9205acb8ec04d5cad21c41ce637a38fb6dee6016a"]
    ]
    csv_header = ["blockNumber", "transactionHash", "median", "transmitter", "obs_len", "order"]
    for ind in range(31):
        str_ind = "ob" + str(ind)
        csv_header.append(str_ind)
    cp_header = ["min_price", "max_price", "min_median", "median_max", "min_max", "weight_1", "weight_2", "weight_3"]
    csv_header.extend(cp_header)
    write_to_csv("../data/eth_usd_observations.csv", 'w', csv_header)
    for ph in phs_list:
        ph_startBlock = ph[0]
        ph_endBlock = ph[1]
        fromBlock = ph_startBlock
        toBlock = fromBlock + 10000
        dec = 10 ** 8
        while fromBlock <= ph_endBlock:
            log_filter = web3.eth.filter({"fromBlock": fromBlock, "toBlock": toBlock, "address": ph[2], "topics": [ph[3]]})
            raw_r = web3.eth.get_filter_logs(log_filter.filter_id)
            cur_n = len(raw_r)
            print(f"{cur_n} records in 10000 blocks")
            for r in raw_r:
                r_blockNumber = r["blockNumber"]
                raw_transactionHash = r["transactionHash"]
                r_transactionHash = raw_transactionHash.hex()
                raw_data = r["data"]
                bytes_r = bytes(raw_data)
                r_data = decode(["int192", "address", "uint32", "int192[]", "bytes", "int192", "bytes32", "uint40"], bytes_r)
                r_median = exact_divide(r_data[0], dec, "0.0000001")
                r_transmitter = r_data[1]
                rcd_list = [r_blockNumber, r_transactionHash, r_median, r_transmitter]
                obs = r_data[3]
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
                r_min = obs_list[10]
                # negative index from -1
                r_max = obs_list[-11]
                min_median = exact_divide(r_data[0] - raw_ob_list[10], dec, "0.0000001")
                median_max = exact_divide(raw_ob_list[-11] - r_data[0], dec, "0.0000001")
                min_max = exact_divide(raw_ob_list[-11] - raw_ob_list[10], dec, "0.0000001")
                weight_1 = exact_divide(r_data[0] - raw_ob_list[10], r_data[0], "0.0000001")
                weight_2 = exact_divide(raw_ob_list[-11] - r_data[0], r_data[0], "0.0000001")
                weight_3 = exact_divide(raw_ob_list[-11] - raw_ob_list[10], r_data[0], "0.0000001")
                cp_list = [r_min, r_max, min_median, median_max, min_max, weight_1, weight_2, weight_3]
                # Fill up to 31 observations
                if obs_len < 31:
                    for j in range(obs_len, 31):
                        rcd_list.append("NaN")
                rcd_list.extend(cp_list)
                write_to_csv("../data/eth_usd_observations.csv", 'a', rcd_list)
            fromBlock = toBlock + 1
            toBlock = min(fromBlock + 10000, ph_endBlock)
