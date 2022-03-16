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


etherscan_client = initialize_etherscan_client()
mongo_client_cluster, mongo_client_database, mongo_client_collection = initialize_mongo_client()

block_number_example = 14247618
address_example = "0x99f806e72c6a192a25e440757bafe9c9169b0c71"

my_transaction = etherscan_client.get_normal_txs_by_address(
    address=address_example,
    startblock=block_number_example,
    endblock=block_number_example,
    sort="asc"
)[0]

my_transaction_date = datetime.utcfromtimestamp(int(my_transaction["timeStamp"])).strftime("%d.%m.%y")

block_reward_data = etherscan_client.get_block_reward_by_block_number(14247618)

block_reward = block_reward_data["blockReward"]

balance_data = etherscan_client.get_eth_balance(address_example)

document_post = {
    "Date": my_transaction_date,
    "Block Reward": convert_amount(block_reward),
    "Account balance": convert_amount(balance_data)
}

mongo_client_collection.insert_one(document_post)
