import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',  # Địa chỉ host MySQL server của bạn
        port=3308,          # Cổng MySQL server (thay đổi nếu cần thiết)
        user='root',        # Tên người dùng MySQL
        password='',        # Mật khẩu người dùng MySQL
        database='qlbida'   # Tên cơ sở dữ liệu bạn muốn kết nối
    )
    return connection
