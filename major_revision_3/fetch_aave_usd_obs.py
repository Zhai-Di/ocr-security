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


def write_to_csv(file_path, mode, record):
    try:
        with open(file_path, mode=mode, encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(record)
    except Exception as e:
        print("ERROR during writing csv")


def save_to_csv(infura_api_key, csv_file_path, phs_list):
    web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/" + infura_api_key))
    csv_header = ["blockNumber", "transactionHash", "median", "transmitter", "obs_len", "order"]
    for ind in range(19):
        str_ind = "ob" + str(ind)
        csv_header.append(str_ind)
    cp_header = ["min_price", "max_price", "min_median", "median_max", "min_max", "weight_1", "weight_2", "weight_3"]
    csv_header.extend(cp_header)
    # 如果将这几个phase中的obs list都合并在一个csv中，则取消下面这行注释，注释掉for下面的第一行
    # write_to_csv(csv_file_path, 'w', csv_header)
    for ph in phs_list:
        write_to_csv(csv_file_path + str(ph["ph_num"]) + ".csv", 'w', csv_header)
        ph_startBlock = ph["startBlock"]
        ph_endBlock = ph["endBlock"]
        # 还没开始查询之前设置的初始值
        fromBlock = ph_startBlock
        # 每次查询间隔10000个区块
        toBlock = fromBlock + 10000
        dec = 10 ** 8
        while fromBlock <= ph_endBlock:
            topic = "0xf6a97944f31ea060dfde0566e4167c1a1082551e64b60ecb14d599a9d023d451"
            if ph["ph_num"] == 5:
                topic = "0xc797025feeeaf2cd924c99e9205acb8ec04d5cad21c41ce637a38fb6dee6016a"
            log_filter = web3.eth.filter({"fromBlock": fromBlock, "toBlock": toBlock,
                                          "address": Web3.to_checksum_address(ph["address"]), "topics": [topic]})
            raw_r = web3.eth.get_filter_logs(log_filter.filter_id)
            cur_n = len(raw_r)
            print(f"{cur_n} records in 10000 blocks")
            for r in raw_r:
                r_blockNumber = r["blockNumber"]
                raw_transactionHash = r["transactionHash"]
                r_transactionHash = raw_transactionHash.hex()
                raw_data = r["data"]
                bytes_r = bytes(raw_data)
                r_data = None
                if ph["ph_num"] == 5:
                    r_data = decode(["int192", "address", "uint32", "int192[]", "bytes", "int192", "bytes32", "uint40"], bytes_r)
                else:
                    r_data = decode(["int192", "address", "int192[]", "bytes", "bytes32"], bytes_r)
                r_median = exact_divide(r_data[0], dec, "0.0000001")
                r_transmitter = r_data[1]
                rcd_list = [r_blockNumber, r_transactionHash, r_median, r_transmitter]
                obs = r_data[2]
                if ph["ph_num"] == 5:
                    obs = r_data[3]
                obs_len = len(obs)
                rcd_list.append(obs_len)
                r_order = False
                # 保证obs list是nondecreasing的
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
                r_min = obs_list[6]
                # negative index from -1
                r_max = obs_list[-7]
                min_median = exact_divide(r_data[0] - raw_ob_list[6], dec, "0.0000001")
                median_max = exact_divide(raw_ob_list[-7] - r_data[0], dec, "0.0000001")
                min_max = exact_divide(raw_ob_list[-7] - raw_ob_list[6], dec, "0.0000001")
                weight_1 = exact_divide(r_data[0] - raw_ob_list[6], r_data[0], "0.0000001")
                weight_2 = exact_divide(raw_ob_list[-7] - r_data[0], r_data[0], "0.0000001")
                weight_3 = exact_divide(raw_ob_list[-7] - raw_ob_list[6], r_data[0], "0.0000001")
                cp_list = [r_min, r_max, min_median, median_max, min_max, weight_1, weight_2, weight_3]
                # Fill up to 31 observations
                if obs_len < 19:
                    for j in range(obs_len, 19):
                        rcd_list.append("NaN")
                rcd_list.extend(cp_list)
                write_to_csv(csv_file_path + str(ph["ph_num"]) + ".csv", 'a', rcd_list)
            fromBlock = toBlock + 1
            toBlock = min(fromBlock + 10000, ph_endBlock)
            # 在上面这个函数里面可能需要加入循环和等待，因为有查询速率限制


if __name__ == "__main__":
    phs_list = [
        {"ph_num": 3, "startBlock": 12744000, "endBlock": 16848000,
         "address": "0xC45eBD0F901bA6B2B8C7e70b717778f055eF5E6D".lower()},
        {"ph_num": 4, "startBlock": 16848001, "endBlock": 20779313,
         "address": "0x8116B273cD75d79C382aFacc706659DEd5E0a59d".lower()},
        {"ph_num": 5, "startBlock": 20779314, "endBlock": 22648654,
         "address": "0xd8B9aA6E811c935eF63e877CFA7Be276931293DA".lower()}
    ]
    csv_file_path = "../data/aave_usd_observations"
    infura_api_key = "06ea03aa865f49fbbc5c6d68489e302a"
    save_to_csv(infura_api_key, csv_file_path, phs_list)
