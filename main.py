from DataBase import DB_model

db_info = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "disk_database"
}

db = DB_model(db_info)

# db.insert_data_interactive()
# db.reindex_table()


print(db.classify_mic_value("Enterobacterales(excluding Salmonella/Shigella)","Ampicillin", 14.1))



#S.pseudintermedius or S.schleiferi