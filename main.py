import config
from etherscan import Etherscan
from pymongo import MongoClient

eth = Etherscan(config.ETHERSCAN_API_TOKEN)
cluster = MongoClient(config.MONGO_CLIENT_HOST)
