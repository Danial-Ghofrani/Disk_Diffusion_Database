import os
import shutil
import pandas as pd
import mysql.connector

db_info = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "disk_database"
}



class DB:

    def __init__(self, db_info):
        self.db_info = db_info
        self.mydb = None
        self.cursor = None

    def connect(self):
        try:
            self.mydb = mysql.connector.connect(
                host = db_info["host"],
                user = db_info["root"],
                password = db_info["password"],
                database = db_info["database"]
            )
            self.cursor = self.mydb.cursor()
            print("Successfully connected to the database.")

        except mysql.connector.Error as err:
            print(f"Error:{err}")

    def disconnect(self, commit = False):
        if commit:
            self.mydb.commit()
        if self.cursor:
            self.cursor.close()
        if self.mydb:
            self.mydb.close()
        print("Disconnected from the database.")

    def calssify_mic_value(self, bacteria_name, antibiotic_name, mic_value):

        self.connect()

        try:
            query = """
            SELECT bacteria_name, antibiotic_name,
                CASE
                    WHEN %s <= resistance_max_value THEN "R"
                    WHEN %s >= susceptible_min_value THEN "S"
                    ELSE "I"
                END AS resistance_category
            
            
            """











