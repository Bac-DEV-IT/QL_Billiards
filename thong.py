# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Đường dẫn tới cơ sở dữ liệu SQLite
db_file = 'database/sqlbida.db'

# HÀM CONNECT SQL
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database '{db_file}'")
    except Error as e:
        print(e)
    return conn

# ĐĂNG KÝ TÀI KHOẢN
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        tendangnhap = request.form['tendangnhap']
        matkhau = request.form['matkhau']
        hoten = request.form['hoten']
        role_id = request.form['role_id']  # role_id là một số nguyên

        conn = create_connection(db_file)
        if conn is not None:
            try:
                # Kiểm tra xem tên đăng nhập đã tồn tại chưa
                cur = conn.cursor()
                cur.execute("SELECT ma_tk FROM account WHERE tendangnhap = ?", (tendangnhap,))
                account = cur.fetchone()

                if account:
                    flash('Tên đăng nhập đã tồn tại, vui lòng chọn tên đăng nhập khác.', 'error')
                else:
                    # Thêm tài khoản mới vào cơ sở dữ liệu
                    cur.execute("INSERT INTO account (tendangnhap, matkhau, hoten, role_id) VALUES (?, ?, ?, ?)",
                                (tendangnhap, matkhau, hoten, role_id))
                    conn.commit()
                    flash('Đăng ký tài khoản thành công!', 'success')
                    return redirect(url_for('login'))
            except Error as e:
                print(e)
                flash('Đã xảy ra lỗi khi đăng ký tài khoản.', 'error')
            finally:
                conn.close()
        else:
            flash('Không thể kết nối đến cơ sở dữ liệu.', 'error')

    return render_template('register.html')
# ĐĂNG NHẬP
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tendangnhap = request.form['tendangnhap']
        matkhau = request.form['matkhau']

        conn = create_connection(db_file)
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM account WHERE tendangnhap = ? AND matkhau = ?", (tendangnhap, matkhau))
                account = cur.fetchone()

                if account:
                    # Lưu session của người dùng đã đăng nhập
                    session['loggedin'] = True
                    session['ma_tk'] = account[0]
                    session['tendangnhap'] = account[1]
                    session['role_id'] = account[4]

                    flash('Đăng nhập thành công!', 'success')

                    # Phân quyền dựa trên role_id
                    if account[4] == 1:
                        return redirect(url_for('admin'))
                    elif account[4] == 2:
                        return redirect(url_for('nhanvien'))
                    else:
                        flash('Không có quyền truy cập.', 'error')

                else:
                    flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
            except sqlite3.Error as e:
                print(e)
                flash('Đã xảy ra lỗi khi đăng nhập.', 'error')
            finally:
                conn.close()
        else:
            flash('Không thể kết nối đến cơ sở dữ liệu.', 'error')

    return render_template('login.html')


# ADMIN từ ĐĂNG NHẬP
@app.route('/admin')
def admin():
    if 'loggedin' in session:
        conn = create_connection(db_file)
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM account WHERE ma_tk = ?", (session['ma_tk'],))
                account = cur.fetchone()
                return render_template('admin.html', account=account)
            except Error as e:
                print(e)
            finally:
                conn.close()

        return render_template('admin.html')
    else:
        return redirect(url_for('login'))


# NHÂN VIÊN từ ĐĂNG NHẬP
@app.route('/nhanvien')
def nhanvien():
    # Kiểm tra đăng nhập
    if 'loggedin' in session and session['loggedin']:
        # Kiểm tra quyền truy cập (nếu cần)
        if 'role_id' in session and session['role_id'] == 2:
            return render_template('nhanvien.html')
        else:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


# ĐĂNG XUẤT
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('ma_tk', None)
    session.pop('tendangnhap', None)
    session.pop('role_id', None)
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('login'))


# Quản Lý Nhân Viên
@app.route('/quan-li-nhan-vien', methods=['GET', 'POST'])
def quan_li_nhan_vien():
    conn = create_connection(db_file)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM member;')
        employees = cursor.fetchall()
        conn.close()
        return render_template('quan_li_nhan_vien.html', employees=employees)

    # Xử lý thêm nhân viên
    elif request.method == 'POST' and request.form['action'] == 'add':
        ten_member = request.form['ten_member']
        dia_chi = request.form['dia_chi']
        so_dien_thoai = request.form['so_dien_thoai']
        email = request.form['email']

        cursor.execute('INSERT INTO member (TenMember, DiaChi, SoDienThoai, Email) VALUES (?, ?, ?, ?);',
                       (ten_member, dia_chi, so_dien_thoai, email))
        conn.commit()
        conn.close()
        return redirect(url_for('quan_li_nhan_vien'))

    # Xử lý xóa nhân viên
    elif request.method == 'POST' and request.form['action'] == 'delete':
        member_id = request.form['member_id']

        cursor.execute('DELETE FROM member WHERE MaMember = ?;', (member_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('quan_li_nhan_vien'))

    # Xử lý tìm kiếm nhân viên
    elif request.method == 'POST' and request.form['action'] == 'search':
        search_term = request.form['search_term']

        cursor.execute('SELECT * FROM member WHERE TenMember LIKE ?;', ('%' + search_term + '%',))
        employees = cursor.fetchall()
        conn.close()
        return render_template('quan_li_nhan_vien.html', employees=employees)

if __name__ == '__main__':
    app.run(debug=True)