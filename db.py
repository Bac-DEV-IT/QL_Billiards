import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        port=3308,
        user='root',
        password='',
        database='qlbida'
    )
    return connection
