import pandas as pd 
from database_connect import mongo_operation as mongo
import os , sys 
from src.constants import *
from src.exception import CustomException 
from database_connect.databases.mongodb import MongoIO1
class MongoIO:
    mongo_ins = None 

    def __init__(self):
        if MongoIO.mongo_ins is None:
            mongo_db_url="mongodb+srv://root:aRaWFZ5pDzq6vOYj@cluster0.adkjuf9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            if mongo_db_url is None:
                raise Exception(f"Environment key:{MONGODB_URL_KEY} is not set.")
            MongoIO.mongo_ins= MongoIO1(client_url=mongo_db_url, 
                                     database_name=MONGO_DATABASE_NAME)
            
        self.mongo_ins=MongoIO.mongo_ins 

    def store_case_study(self,
                    case_study:pd.DataFrame,category: str):
        try:
            collection_name = category.replace(" ","_")
            self.mongo_ins.bulk_insert(case_study, collection_name)

        except Exception as e:
            raise CustomException(e,sys)
        
    def get_case_study(
            self,   category:str):
        try:
            data= self.mongo_ins.find(
                collection_name = category.replace(" ","_")
            )
            return data
        except Exception as e:
            raise CustomException(e,sys)

            