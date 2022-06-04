import mysql.connector
from datetime import date


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="product_listings")

mycursor = db.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS product_listings")

T1_user_db = "CREATE TABLE IF NOT EXISTS user_db\
              (email VARCHAR(30) PRIMARY KEY,\
               first_name VARCHAR(30),\
               last_name VARCHAR(30),\
               DOB DATE,\
               date_created datetime,\
               password VARCHAR(30))"

T2_receipt_scans_db = "CREATE TABLE IF NOT EXISTS receipt_scans_db\
                       (email VARCHAR(30),\
                       product_name VARCHAR(50),\
                       product_price FLOAT,\
                       vendor VARCHAR(50),\
                       date_created datetime)"

mycursor.execute(T1_user_db)
mycursor.execute(T2_receipt_scans_db)
db.commit()


def Q_create_user(user_data):
    try:
        create_user_query = "INSERT INTO user_db (email, first_name, last_name, DOB, date_created, password) VALUES (%s, %s, %s, %s, %s, %s)"
        mycursor.execute(create_user_query, (user_data[0], user_data[1], user_data[2], user_data[3], date.today(), user_data[4]))
        db.commit()
    except Exception as ex:
        print("ERROR: Email already in use.")


def Q_add_product_data(product_info, email):
    create_user_query = "INSERT INTO receipt_scans_db (email, product_name, product_price, date_created, vendor) VALUES (%s, %s, %s, %s, %s)"
    for i in range(len(product_info) - 1):
        mycursor.execute(create_user_query,
                         (email, product_info[i][0], product_info[i][1], product_info[i][2], product_info[i][3]))
    db.commit()


def print_user_db():
    # print all records under user_db
    mycursor.execute("SELECT * FROM user_db")
    for x in mycursor:
        print(x)


def print_receiptScans_db():
    # print all records under receipt_scans_db
    mycursor.execute("SELECT * FROM receipt_scans_db")
    for x in mycursor:
        print(x)


def print_scan_count(user_data):
    # scan count per email
    # user_data = ["test.w@gmail.com", "Aj", "Ishac", "1954/09/02", "pass1954"]
    scan_count_query = "SELECT count(*) AS item_count FROM receipt_scans_db WHERE email = %s"
    mycursor.execute(scan_count_query, (user_data[0],))
    print(mycursor.fetchone()[0])


def print_user_count():
    # print number of distinct users
    user_count_query = "SELECT distinct count(*) AS item_count FROM user_db"
    mycursor.execute(user_count_query)
    print(mycursor.fetchone()[0])
