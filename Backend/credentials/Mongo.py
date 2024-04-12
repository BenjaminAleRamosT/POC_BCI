import os
from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
ibm_cloud_user = os.environ.get("ibm_cloud_user")
ibm_cloud_password = os.environ.get("ibm_cloud_password")
CONNECTION_STRING = f"mongodb://{ibm_cloud_user}:{ibm_cloud_password}@8f26f425-d81d-49c9-a48b-7be6c29b10e5-0.bkvfu0nd0m8k95k94ujg.databases.appdomain.cloud:30165,8f26f425-d81d-49c9-a48b-7be6c29b10e5-1.bkvfu0nd0m8k95k94ujg.databases.appdomain.cloud:30165,8f26f425-d81d-49c9-a48b-7be6c29b10e5-2.bkvfu0nd0m8k95k94ujg.databases.appdomain.cloud:30165/ibmclouddb?authSource=admin&replicaSet=replset&tls=true&tlsCAFile=tsl_certificate.pem"


def get_mongo_client(CONNECTION_STRING=CONNECTION_STRING):
    client = MongoClient(CONNECTION_STRING)
    return client