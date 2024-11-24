from DataBase import DB_model

db_info = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "disk_database"
}

db = DB_model(db_info)

db.insert_data_interactive()



# print(db.classify_mic_value("Salmonella", "Ampicillin", 11))
