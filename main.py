from datetime import datetime

from etherscan import Etherscan
from pymongo import MongoClient

import config


def initialize_etherscan_client():
    eth = Etherscan(config.ETHERSCAN_API_TOKEN)
    return eth


def initialize_mongo_client():
    cluster = MongoClient(config.MONGO_CLIENT_HOST)
    db = cluster["etherscan_api_pet_project"]
    collection = db["transaction_data"]
    return cluster, db, collection


def convert_amount(amount):
    full_amount = str(amount).zfill(19)
    decimal_amount = f"{full_amount[0]}.{full_amount[1:]}"
    return decimal_amount


def parse_block(block_number):
    block_reward_data = etherscan_client.get_block_reward_by_block_number(block_number)
    block_reward = block_reward_data["blockReward"]
    return {
        "block_reward": block_reward
    }


def parse_transaction(transaction):
    transaction_hash = transaction["hash"]
    transaction_date = datetime.utcfromtimestamp(int(transaction["timeStamp"])).strftime("%d.%m.%y")
    income_amount = convert_amount(transaction["value"])

    block_number = transaction["blockNumber"]
    parse_block_result = parse_block(block_number)
    block_reward = parse_block_result["block_reward"]

    return {
        "_id": transaction_hash,
        "Date": transaction_date,
        "Block Reward": convert_amount(block_reward),
        "Account balance": convert_amount(balance),
        "Income Amount": income_amount,
        "From": transaction["from"],
        "To": transaction["to"],
        "Gas Price": convert_amount(transaction["gasPrice"])
    }


etherscan_client = initialize_etherscan_client()
mongo_client_cluster, mongo_client_database, mongo_client_collection = initialize_mongo_client()
my_address = config.ADDRESS

balance = etherscan_client.get_eth_balance(my_address)

my_transactions = etherscan_client.get_normal_txs_by_address(
    address=my_address,
    startblock=0,
    endblock=99999999,
    sort="asc"
)

parse_transaction_results = [parse_transaction(transaction) for transaction in my_transactions]
mongo_client_collection.insert_many(parse_transaction_results)
