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
        except mysql.connector.errors.Error as err:
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
            # Query to fetch all rows matching the given bacteria and antibiotic
            query = """
            SELECT 
                s_value, r_value, 
                i_min, i_max, 
                sdd_min, sdd_max,
                indications
            FROM resistance_thresholds
            WHERE bacteria_name = %s AND antibiotic_name = %s;
            """
            self.cursor.execute(query, (bacteria_name, antibiotic_name))
            results = self.cursor.fetchall()

            if not results:
                print("No data found for the specified bacteria and antibiotic combination in the CLSI's database.")
                add_new = input("Would you like to add a new entry to the database? (yes/no): ").strip().lower()
                if add_new in ['yes', 'y']:
                    self.add_new_entry(bacteria_name, antibiotic_name)
                return "Process terminated as no data was found and/or added."

            # Collect all unique indications from matching rows
            indications_set = set()
            thresholds = []
            for row in results:
                s_value, r_value, i_min, i_max, sdd_min, sdd_max, indications = row
                thresholds.append((s_value, r_value, i_min, i_max, sdd_min, sdd_max))
                if indications:
                    indications_list = [ind.strip() for ind in indications.split(",")]
                    indications_set.update(indications_list)

            # If there are indications, prompt the user to select one
            if indications_set:
                indications_list = sorted(indications_set)
                print("Available indications for the given bacteria and antibiotic combination:")
                for idx, indication in enumerate(indications_list, start=1):
                    print(f"{idx}: {indication}")

                try:
                    selected_index = int(input("Enter the number corresponding to the desired indication: "))
                    if 1 <= selected_index <= len(indications_list):
                        selected_indication = indications_list[selected_index - 1]
                        print(f"Selected indication: {selected_indication}")
                    else:
                        return "Invalid selection. Please try again."
                except ValueError:
                    return "Invalid input. Please enter a number."
            else:
                print("No indications found for the specified bacteria and antibiotic combination.")


            mic_value = int(mic_value)

            # Perform MIC classification based on thresholds from the first matching row
            for s_value, r_value, i_min, i_max, sdd_min, sdd_max in thresholds:
                if s_value is not None and r_value is not None and i_min is None and sdd_min is None:
                    # Case: Only S and R values
                    if mic_value >= s_value:
                        return "S"
                    elif mic_value < s_value:
                        return "R"
                elif i_min is not None and i_max is not None:
                    # Case: I (Intermediate)
                    if i_min <= mic_value <= i_max:
                        return "I"
                    elif mic_value >= s_value:
                        return "S"
                    elif mic_value < s_value:
                        return "R"
                elif sdd_min is not None and sdd_max is not None:
                    # Case: SDD (Susceptible-Dose Dependent)
                    if sdd_min <= mic_value <= sdd_max:
                        return "SDD"
                    elif mic_value >= s_value:
                        return "S"
                    elif mic_value < s_value:
                        return "R"

            # Fallback if no classification matches
            return "Unable to classify based on the provided MIC value."
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            self.disconnect()

    def add_new_entry(self, bacteria_name, antibiotic_name):
        """Prompt the user to add a new row to the database."""
        try:
            print("Adding a new entry to the database.")
            s_value = input("Enter the S value (or press Enter to leave it empty): ").strip()
            r_value = input("Enter the R value (or press Enter to leave it empty): ").strip()
            i_min = input("Enter the I minimum value (or press Enter to leave it empty): ").strip()
            i_max = input("Enter the I maximum value (or press Enter to leave it empty): ").strip()
            sdd_min = input("Enter the SDD minimum value (or press Enter to leave it empty): ").strip()
            sdd_max = input("Enter the SDD maximum value (or press Enter to leave it empty): ").strip()
            indications = input("Enter indications (comma-separated, or leave empty if none): ").strip()

            # Handle empty inputs as NULL values for the database
            s_value = float(s_value) if s_value else None
            r_value = float(r_value) if r_value else None
            i_min = float(i_min) if i_min else None
            i_max = float(i_max) if i_max else None
            sdd_min = float(sdd_min) if sdd_min else None
            sdd_max = float(sdd_max) if sdd_max else None
            indications = indications if indications else None

            # Insert the new row into the database
            query = """
            INSERT INTO resistance_thresholds 
            (bacteria_name, antibiotic_name, s_value, r_value, i_min, i_max, sdd_min, sdd_max, indications)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.cursor.execute(query, (
            bacteria_name, antibiotic_name, s_value, r_value, i_min, i_max, sdd_min, sdd_max, indications))
            self.connection.commit()
            print("New entry added successfully!")
        except mysql.connector.Error as err:
            print(f"Error adding new entry: {err}")
        except ValueError as err:
            print(f"Invalid input: {err}")

    def insert_resistance_threshold(self, bacteria_name, antibiotic_name, disk_content, s_value,
                                    i_min, i_max, sdd_min, sdd_max, r_value, indications):
        self.connect()
        try:
            if not self.table_exists("resistance_thresholds"):
                print("Table 'resistance_thresholds' does not exist. Creating the table.")
                create_table_query = """
                CREATE TABLE resistance_thresholds (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bacteria_name VARCHAR(255),
                    antibiotic_name VARCHAR(255),
                    disk_content VARCHAR(255),
                    s_value FLOAT,
                    i_min FLOAT,
                    i_max FLOAT,
                    sdd_min FLOAT,
                    sdd_max FLOAT,
                    r_value FLOAT,
                    indications TEXT
                );
                """
                self.cursor.execute(create_table_query)

            insert_query = """
            INSERT INTO resistance_thresholds (
                bacteria_name, antibiotic_name, disk_content, s_value, 
                i_min, i_max, sdd_min, sdd_max, r_value, indications
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                bacteria_name, antibiotic_name, disk_content, s_value,
                i_min, i_max, sdd_min, sdd_max, r_value, indications
            ))
            print(f"Inserted data for {bacteria_name} and {antibiotic_name} successfully.")
        except mysql.connector.errors.Error as err:
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
            disk_content = input("Enter the Disk Content (in µg) or '-' if missing: ")

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

            # Prompt user for Indications
            indications = input("Enter the indications (or leave blank if none): ").strip()

            # Insert the collected data into the database
            self.insert_resistance_threshold(
                bacteria_name, antibiotic_name, disk_content, s_value,
                i_min, i_max, sdd_min, sdd_max, r_value, indications
            )

            # Ask if the user wants to continue
            continue_entry = input("Do you want to enter another row? (yes/no): ").strip().lower()
            if continue_entry in ["no", "n"]:
                print("Data entry terminated.")
                break

    def reindex_table(self):
        """
        Reindexes the id column in the 'resistance_thresholds' table, filling gaps
        and resetting the numbering sequentially from 1.
        """
        self.connect()
        try:
            # Create a temporary table to hold the reindexed data
            self.cursor.execute("""
                CREATE TEMPORARY TABLE temp_table AS
                SELECT * FROM resistance_thresholds ORDER BY id;
            """)

            # Drop the existing table
            self.cursor.execute("DROP TABLE resistance_thresholds;")

            # Recreate the original table
            self.cursor.execute("""
                CREATE TABLE resistance_thresholds (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bacteria_name VARCHAR(255),
                    antibiotic_name VARCHAR(255),
                    disk_content VARCHAR(255),
                    s_value FLOAT,
                    i_min FLOAT,
                    i_max FLOAT,
                    sdd_min FLOAT,
                    sdd_max FLOAT,
                    r_value FLOAT,
                    indications TEXT
                );
            """)

            # Insert data from the temporary table while resetting the id
            self.cursor.execute("""
                INSERT INTO resistance_thresholds (
                    bacteria_name, antibiotic_name, disk_content, s_value, 
                    i_min, i_max, sdd_min, sdd_max, r_value, indications
                )
                SELECT bacteria_name, antibiotic_name, disk_content, s_value, 
                       i_min, i_max, sdd_min, sdd_max, r_value, indications
                FROM temp_table;
            """)

            # Commit changes
            print("Reindexing completed successfully.")
        except mysql.connector.Error as err:
            print(f"Error during reindexing: {err}")
        finally:
            self.disconnect(commit=True)


