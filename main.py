import webbrowser
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


def parse_transaction(transaction, balance):
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


def process_transactions(mongo_client_collection):
    etherscan_client = initialize_etherscan_client()
    my_address = config.ADDRESS

    balance = etherscan_client.get_eth_balance(my_address)

    my_transactions = etherscan_client.get_normal_txs_by_address(
        address=my_address,
        startblock=0,
        endblock=99999999,
        sort="asc"
    )

    parse_transaction_results = [parse_transaction(transaction, balance) for transaction in my_transactions]
    mongo_client_collection.insert_many(parse_transaction_results)


def display_data(mongo_client_collection, open_in_browser=False):
    filename = "output.html"
    transaction_data_list = []
    first_time = True
    for transaction in mongo_client_collection.find():
        if first_time:
            first_time = False
            transaction_headers = "\n".join(f"\t\t\t\t<th>{header}</th>" for header in transaction)
            transaction_data_list.append(
                f"""<tr>
{transaction_headers}
            </tr>
            """
            )
        transaction_values = "\n".join(f"\t\t\t\t<td>{transaction[key]}</td>" for key in transaction)
        transaction_data_list.append(
            f"""<tr>
{transaction_values}
            </tr>
            """
        )
    transactions = "".join(transaction_data_list).rstrip()

    content = f"""<!DOCTYPE html>
<html>
    <head>
        <meta content="text/html">
        <title>My Transactions</title>
        <style>
            td, th {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            tr:nth-child(even){{background-color: #f2f2f2;}}
            tr:hover {{background-color: #ddd;}}
            th {{
              padding-top: 12px;
              padding-bottom: 12px;
              text-align: left;
              background-color: #04AA6D;
              color: white;
            }}
        </style>
    </head>
    <body>
        <table>
            {transactions}
        </table>
    </body>
</html>
    """

    with open(filename, "w") as out:
        out.write(content)

    if open_in_browser:
        webbrowser.open(filename)


def main(insert_transactions=False):
    mongo_client_cluster, mongo_client_database, mongo_client_collection = initialize_mongo_client()
    if insert_transactions:
        process_transactions(mongo_client_collection)
    display_data(mongo_client_collection, open_in_browser=True)


if __name__ == "__main__":
    main()
