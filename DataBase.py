import os
import shutil
import pandas as pd
import mysql.connector


class DB_model:

    def __init__(self, db_info):
        self.db_info = db_info
        self.mydb = None
        self.cursor = None

    def create_database_if_not_exists(self):

        temp_db = mysql.connector.connect(
            host=self.db_info["host"],
            user=self.db_info["user"],
            password=self.db_info["password"]
        )
        temp_cursor = temp_db.cursor()

        # Creating the database if it doesn't exist
        try:
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_info['database']}")
            print(f"Database '{self.db_info['database']}' checked/created")
        except mysql.connector.errors as err:
            print(f"Error creating database: {err}")
        finally:
            temp_cursor.close()
            temp_db.close()

    def connect(self):
        self.create_database_if_not_exists()

        try:
            self.mydb = mysql.connector.connect(
                host=self.db_info["host"],
                user=self.db_info["user"],
                password=self.db_info["password"],
                database=self.db_info["database"]
            )
            self.cursor = self.mydb.cursor()
            print("Successfully connected to the database.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def disconnect(self, commit=False):
        if commit:
            self.mydb.commit()
        if self.cursor:
            self.cursor.close()
        if self.mydb:
            self.mydb.close()
        print("Disconnected from the database.")

    def classify_mic_value(self, bacteria_name, antibiotic_name, mic_value):

        self.connect()

        try:
            query = """
            SELECT bacteria_name, antibiotic_name,
                CASE
                    WHEN %s <= resistance_max_value THEN "R"
                    WHEN %s >= susceptible_min_value THEN "S"
                    ELSE "I"
                END AS resistance_category
            FROM resistance_thresholds
            WHERE bacteria_name = %s AND antibiotic_name = %s;
            """

            self.cursor.execute(query, (mic_value, mic_value, bacteria_name, antibiotic_name))
            result = self.cursor.fetchone()

            if result:
                return result[2]
            else:
                return "No data found for the specified bacteria and antibiotic combination."
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            self.disconnect()

    def table_exists(self, table_name):
        self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = self.cursor.fetchone()
        return result is not None

    def insert_resistance_threshold(self, bacteria_name, antibiotic_name, disk_content, s_value,
                                    i_min, i_max, sdd_min, sdd_max, r_value):
        self.connect()
        try:
            if not self.table_exists("resistance_thresholds"):
                print("Table 'resistance_thresholds' does not exist. Creating the table.")
                create_table_query = """
                CREATE TABLE resistance_thresholds (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bacteria_name VARCHAR(255),
                    antibiotic_name VARCHAR(255),
                    disk_content FLOAT,
                    s_value FLOAT,
                    i_min FLOAT,
                    i_max FLOAT,
                    sdd_min FLOAT,
                    sdd_max FLOAT,
                    r_value FLOAT
                );
                """
                self.cursor.execute(create_table_query)

            insert_query = """
            INSERT INTO resistance_thresholds (
                bacteria_name, antibiotic_name, disk_content, s_value, 
                i_min, i_max, sdd_min, sdd_max, r_value
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                bacteria_name, antibiotic_name, disk_content, s_value,
                i_min, i_max, sdd_min, sdd_max, r_value
            ))
            print(f"Inserted data for {bacteria_name} and {antibiotic_name} successfully.")
        except mysql.connector.errors as err:
            print(f"Error: {err}")
        finally:
            self.disconnect(commit=True)

    def parse_numeric_input(self, value):
        """Convert input to float or return None if input is '-'."""
        if value.strip() == '-':
            return None  # Use NULL for missing data
        return float(value)

    def insert_data_interactive(self):
        while True:
            bacteria_name = input("What is the bacteria's name? ")
            antibiotic_name = input("What is the antibiotic's name? ")

            # Prompt user for Disk Content
            disk_content = self.parse_numeric_input(input("Enter the Disk Content (in µg) or '-' if missing: "))

            # Prompt user for S (Susceptible) value
            s_value = float(input("Enter the Susceptible (S) value: "))

            # Prompt user for I (Intermediate) thresholds
            i_min = self.parse_numeric_input(input("Enter the minimum value for Intermediate (I) or '-' if missing: "))
            i_max = self.parse_numeric_input(input("Enter the maximum value for Intermediate (I) or '-' if missing: "))

            # Prompt user for SDD thresholds
            sdd_min = self.parse_numeric_input(input("Enter the minimum value for Susceptible-Dose Dependent (SDD) or '-' if missing: "))
            sdd_max = self.parse_numeric_input(input("Enter the maximum value for Susceptible-Dose Dependent (SDD) or '-' if missing: "))

            # Prompt user for R (Resistant) value
            r_value = float(input("Enter the Resistant (R) value: "))

            # Insert the collected data into the database
            self.insert_resistance_threshold(
                bacteria_name, antibiotic_name, disk_content, s_value,
                i_min, i_max, sdd_min, sdd_max, r_value
            )

            # Ask if the user wants to continue
            continue_entry = input("Do you want to enter another row? (yes/no): ").strip().lower()
            if continue_entry in ["no", "n"]:
                print("Data entry terminated.")
                break
