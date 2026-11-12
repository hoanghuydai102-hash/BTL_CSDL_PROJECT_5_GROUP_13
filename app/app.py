import secrets
from datetime import date
import re

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from getpass import getpass
from decimal import Decimal, InvalidOperation

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_PASSWORD = getpass("Nhap mat khau MySQL: ")


def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=DB_PASSWORD,
        database="ql_van_tai"
    )


@app.route("/")
def dashboard():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM XE")
        so_xe = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM TAI_XE")
        so_tai_xe = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM TUYEN_DUONG")
        so_tuyen = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM CHUYEN_XE")
        so_chuyen = cursor.fetchone()[0]

        return render_template(
            "dashboard.html",
            so_xe=so_xe,
            so_tai_xe=so_tai_xe,
            so_tuyen=so_tuyen,
            so_chuyen=so_chuyen
        )

    except mysql.connector.Error as error:
        app.logger.error("Loi tai Dashboard: %s", error)
        return "Không thể tải Dashboard. Vui lòng kiểm tra MySQL.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

@app.route("/xe")
def danh_sach_xe():
    connection = None
    cursor = None

    # Lấy từ khóa tìm kiếm trên URL
    tu_khoa = request.args.get("q", "").strip()

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Truy vấn danh sách xe
        sql = """
            SELECT
                MaXe,
                BienSo,
                HangSanXuat,
                Model,
                NamSanXuat,
                SoChoNgoi,
                TrangThai
            FROM XE
        """

        # Nếu có từ khóa thì lọc theo biển số
        if tu_khoa:
            sql += " WHERE BienSo LIKE %s"
            tham_so = (f"%{tu_khoa}%",)
        else:
            tham_so = ()

        sql += " ORDER BY MaXe"

        # Truy vấn có tham số
        cursor.execute(sql, tham_so)

        danh_sach = cursor.fetchall()

        return render_template(
            "xe/danh_sach.html",
            danh_sach=danh_sach,
            tu_khoa=tu_khoa
        )

    except mysql.connector.Error as error:
        app.logger.error(
            "Loi truy van danh sach xe: %s",
            error
        )

        return (
            "Không thể tải danh sách xe. "
            "Vui lòng kiểm tra kết nối MySQL.",
            500
        )

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

@app.route("/xe/them", methods=["GET", "POST"])
def them_xe():
    loi = None

    du_lieu = {
        "BienSo": "",
        "MauSac": "",
        "HangSanXuat": "",
        "DoiXe": "",
        "Model": "",
        "NamSanXuat": "",
        "SoChoNgoi": "",
        "TrangThai": "1"
    }

    if request.method == "POST":

        # 1. Lấy dữ liệu từ form
        for truong in du_lieu:
            du_lieu[truong] = request.form.get(truong, "").strip()

        # 2. Kiểm tra các trường bắt buộc
        truong_bat_buoc = [
            "BienSo",
            "MauSac",
            "HangSanXuat",
            "DoiXe",
            "Model",
            "NamSanXuat",
            "SoChoNgoi"
        ]

        if any(not du_lieu[t] for t in truong_bat_buoc):
            loi = "Vui lòng nhập đầy đủ thông tin xe."

        # 3. Kiểm tra dữ liệu số
        if loi is None:
            try:
                nam_san_xuat = int(du_lieu["NamSanXuat"])
                so_cho_ngoi = int(du_lieu["SoChoNgoi"])

                if nam_san_xuat < 1901 or nam_san_xuat > 2155:
                    loi = "Năm sản xuất không hợp lệ."

                elif so_cho_ngoi <= 2:
                    loi = "Số chỗ ngồi phải lớn hơn 2."

                elif du_lieu["TrangThai"] not in ("0", "1"):
                    loi = "Trạng thái xe không hợp lệ."

            except ValueError:
                loi = "Năm sản xuất và số chỗ ngồi phải là số nguyên."

        # 4. Kiểm tra độ dài theo schema MySQL
        if loi is None:
            gioi_han = {
                "BienSo": 15,
                "MauSac": 30,
                "HangSanXuat": 50,
                "DoiXe": 50,
                "Model": 50
            }

            for truong, do_dai in gioi_han.items():
                if len(du_lieu[truong]) > do_dai:
                    loi = f"Trường {truong} vượt quá {do_dai} ký tự."
                    break

        # 5. Thêm xe vào MySQL
        if loi is None:
            connection = None
            cursor = None

            try:
                connection = get_connection()
                cursor = connection.cursor()

                sql = """
                    INSERT INTO XE (
                        BienSo,
                        MauSac,
                        HangSanXuat,
                        DoiXe,
                        Model,
                        NamSanXuat,
                        SoChoNgoi,
                        TrangThai
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                gia_tri = (
                    du_lieu["BienSo"],
                    du_lieu["MauSac"],
                    du_lieu["HangSanXuat"],
                    du_lieu["DoiXe"],
                    du_lieu["Model"],
                    nam_san_xuat,
                    so_cho_ngoi,
                    int(du_lieu["TrangThai"])
                )

                cursor.execute(sql, gia_tri)

                connection.commit()

                flash(
                    f"Đã thêm xe {du_lieu['BienSo']} thành công!",
                    "success"
                )

                return redirect(url_for("danh_sach_xe"))

            except mysql.connector.IntegrityError as error:
                if connection is not None:
                    connection.rollback()

                if error.errno == 1062:
                    loi = "Biển số xe đã tồn tại trong hệ thống."
                else:
                    app.logger.error("Loi rang buoc khi them xe: %s", error)
                    loi = "Dữ liệu vi phạm ràng buộc cơ sở dữ liệu."

            except mysql.connector.Error as error:
                if connection is not None:
                    connection.rollback()

                app.logger.error("Loi MySQL khi them xe: %s", error)
                loi = "Không thể thêm xe. Vui lòng kiểm tra MySQL."

            finally:
                if cursor is not None:
                    cursor.close()

                if connection is not None and connection.is_connected():
                    connection.close()

    return render_template(
        "xe/form.html",
        du_lieu=du_lieu,
        loi=loi,
        che_do="them"
    )

@app.route("/xe/sua/<int:ma_xe>", methods=["GET", "POST"])
def sua_xe(ma_xe):
    connection = None
    cursor = None
    loi = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiểm tra xe có tồn tại không
        cursor.execute(
            """
            SELECT
                MaXe,
                BienSo,
                MauSac,
                HangSanXuat,
                DoiXe,
                Model,
                NamSanXuat,
                SoChoNgoi,
                TrangThai
            FROM XE
            WHERE MaXe = %s
            """,
            (ma_xe,)
        )

        xe = cursor.fetchone()

        if xe is None:
            return "Không tìm thấy xe cần sửa.", 404

        # 2. Chuẩn bị dữ liệu hiển thị trên form
        du_lieu = {
            "BienSo": xe["BienSo"],
            "MauSac": xe["MauSac"],
            "HangSanXuat": xe["HangSanXuat"],
            "DoiXe": xe["DoiXe"],
            "Model": xe["Model"],
            "NamSanXuat": str(xe["NamSanXuat"]),
            "SoChoNgoi": str(xe["SoChoNgoi"]),
            "TrangThai": str(int(xe["TrangThai"]))
        }

        # 3. Nếu người dùng nhấn nút Lưu
        if request.method == "POST":

            for truong in du_lieu:
                du_lieu[truong] = request.form.get(
                    truong, ""
                ).strip()

            # 4. Kiểm tra trường bắt buộc
            truong_bat_buoc = [
                "BienSo",
                "MauSac",
                "HangSanXuat",
                "DoiXe",
                "Model",
                "NamSanXuat",
                "SoChoNgoi"
            ]

            if any(not du_lieu[t] for t in truong_bat_buoc):
                loi = "Vui lòng nhập đầy đủ thông tin xe."

            # 5. Kiểm tra dữ liệu số
            if loi is None:
                try:
                    nam_san_xuat = int(du_lieu["NamSanXuat"])
                    so_cho_ngoi = int(du_lieu["SoChoNgoi"])

                    if not 1901 <= nam_san_xuat <= 2155:
                        loi = "Năm sản xuất không hợp lệ."

                    elif so_cho_ngoi <= 2:
                        loi = "Số chỗ ngồi phải lớn hơn 2."

                    elif du_lieu["TrangThai"] not in ("0", "1"):
                        loi = "Trạng thái xe không hợp lệ."

                except ValueError:
                    loi = (
                        "Năm sản xuất và số chỗ ngồi "
                        "phải là số nguyên."
                    )

            # 6. Kiểm tra độ dài VARCHAR
            if loi is None:
                gioi_han = {
                    "BienSo": 15,
                    "MauSac": 30,
                    "HangSanXuat": 50,
                    "DoiXe": 50,
                    "Model": 50
                }

                for truong, do_dai in gioi_han.items():
                    if len(du_lieu[truong]) > do_dai:
                        loi = (
                            f"Trường {truong} "
                            f"vượt quá {do_dai} ký tự."
                        )
                        break

            # 7. Thực hiện UPDATE nếu hợp lệ
            if loi is None:

                sql = """
                    UPDATE XE
                    SET
                        BienSo = %s,
                        MauSac = %s,
                        HangSanXuat = %s,
                        DoiXe = %s,
                        Model = %s,
                        NamSanXuat = %s,
                        SoChoNgoi = %s,
                        TrangThai = %s
                    WHERE MaXe = %s
                """

                gia_tri = (
                    du_lieu["BienSo"],
                    du_lieu["MauSac"],
                    du_lieu["HangSanXuat"],
                    du_lieu["DoiXe"],
                    du_lieu["Model"],
                    nam_san_xuat,
                    so_cho_ngoi,
                    int(du_lieu["TrangThai"]),
                    ma_xe
                )

                try:
                    cursor.execute(sql, gia_tri)
                    connection.commit()

                    flash(
                        "Đã cập nhật thông tin xe thành công!",
                        "success"
                    )

                    return redirect(url_for("danh_sach_xe"))

                except mysql.connector.Error as error:
                    connection.rollback()

                    if error.errno == 1062:
                        loi = "Biển số xe đã tồn tại trong hệ thống."

                    elif error.errno == 1644:
                        loi = (
                            "Không thể cập nhật xe vì "
                            "vi phạm quy tắc nghiệp vụ."
                        )

                    elif error.errno == 3819:
                        loi = (
                            "Thông tin xe vi phạm "
                            "ràng buộc CHECK."
                        )

                    else:
                        app.logger.error(
                            "Loi cap nhat xe: %s",
                            error
                        )
                        loi = "Không thể cập nhật xe."

        return render_template(
            "xe/form.html",
            du_lieu=du_lieu,
            loi=loi,
            che_do="sua",
            ma_xe=ma_xe
        )

    except mysql.connector.Error as error:
        app.logger.error("Loi tai form sua xe: %s", error)
        return "Không thể tải thông tin xe.", 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# CHUC NANG XOA XE
# ==========================================================

@app.route("/xe/xoa/<int:ma_xe>", methods=["POST"])
def xoa_xe(ma_xe):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiem tra xe co ton tai hay khong
        cursor.execute(
            """
            SELECT MaXe, BienSo
            FROM XE
            WHERE MaXe = %s
            FOR UPDATE
            """,
            (ma_xe,)
        )

        xe = cursor.fetchone()

        if xe is None:
            flash("Không tìm thấy xe cần xóa.", "danger")
            return redirect(url_for("danh_sach_xe"))

        # 2. Kiem tra xe co chuyen xe lien quan khong
        cursor.execute(
            """
            SELECT COUNT(*) AS SoLuong
            FROM CHUYEN_XE
            WHERE MaXe = %s
            """,
            (ma_xe,)
        )

        so_chuyen = cursor.fetchone()["SoLuong"]

        if so_chuyen > 0:
            flash(
                f"Không thể xóa xe {xe['BienSo']} "
                f"vì xe đã được sử dụng trong {so_chuyen} chuyến xe.",
                "danger"
            )

            connection.rollback()
            return redirect(url_for("danh_sach_xe"))

        # 3. Kiem tra xe co lich su bao duong khong
        cursor.execute(
            """
            SELECT COUNT(*) AS SoLuong
            FROM BAO_DUONG
            WHERE MaXe = %s
            """,
            (ma_xe,)
        )

        so_bao_duong = cursor.fetchone()["SoLuong"]

        if so_bao_duong > 0:
            flash(
                f"Không thể xóa xe {xe['BienSo']} "
                f"vì xe có {so_bao_duong} bản ghi bảo dưỡng.",
                "danger"
            )

            connection.rollback()
            return redirect(url_for("danh_sach_xe"))

        # 4. Xoa xe neu khong co du lieu lien quan
        cursor.execute(
            """
            DELETE FROM XE
            WHERE MaXe = %s
            """,
            (ma_xe,)
        )

        connection.commit()

        flash(
            f"Đã xóa xe {xe['BienSo']} thành công!",
            "success"
        )

        return redirect(url_for("danh_sach_xe"))

    except mysql.connector.Error as error:

        if connection is not None:
            connection.rollback()

        app.logger.error("Lỗi khi xóa xe: %s", error)

        if error.errno == 1451:
            flash(
                "Không thể xóa xe vì đang có dữ liệu liên quan.",
                "danger"
            )
        else:
            flash(
                "Có lỗi cơ sở dữ liệu khi xóa xe.",
                "danger"
            )

        return redirect(url_for("danh_sach_xe"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# MODULE QUAN LY TAI XE
# 8.1 - HIEN THI DANH SACH TAI XE
# ==========================================================

# ==========================================================
# 8.2 - DANH SACH VA TIM KIEM TAI XE
# ==========================================================

@app.route("/tai-xe", methods=["GET"])
def danh_sach_tai_xe():

    connection = None
    cursor = None

    # Lay tu khoa tu thanh tim kiem
    tu_khoa = request.args.get("q", "").strip()

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if tu_khoa:

            sql = """
                SELECT
                    MaTaiXe,
                    HoTen,
                    SoCCCD
                FROM TAI_XE
                WHERE HoTen LIKE %s
                   OR SoCCCD LIKE %s
                ORDER BY MaTaiXe ASC
            """

            gia_tri_tim = f"%{tu_khoa}%"

            cursor.execute(
                sql,
                (gia_tri_tim, gia_tri_tim)
            )

        else:

            sql = """
                SELECT
                    MaTaiXe,
                    HoTen,
                    SoCCCD
                FROM TAI_XE
                ORDER BY MaTaiXe ASC
            """

            cursor.execute(sql)

        danh_sach = cursor.fetchall()

        return render_template(
            "tai_xe/danh_sach.html",
            danh_sach=danh_sach,
            tu_khoa=tu_khoa
        )

    except mysql.connector.Error as error:

        app.logger.error(
            "Loi truy van danh sach tai xe: %s",
            error
        )

        return "Không thể tải danh sách tài xế.", 500

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 8.3 - THEM TAI XE
# ==========================================================

@app.route("/tai-xe/them", methods=["GET", "POST"])
def them_tai_xe():

    if request.method == "GET":
        return render_template(
            "tai_xe/form.html",
            tai_xe={},
            tieu_de="Thêm tài xế"
        )

    du_lieu = {
        "HoTen": request.form.get("HoTen", "").strip(),
        "SoCCCD": request.form.get("SoCCCD", "").strip(),
        "SoBangLai": request.form.get("SoBangLai", "").strip(),
        "LoaiBangLai": request.form.get("LoaiBangLai", "").strip(),
        "DiaChi": request.form.get("DiaChi", "").strip(),
        "NgaySinh": request.form.get("NgaySinh", "").strip(),
        "NgayVaoNghe": request.form.get("NgayVaoNghe", "").strip(),
        "SDT": request.form.get("SDT", "").strip(),
        "Email": request.form.get("Email", "").strip(),
        "TrangThai": request.form.get("TrangThai", "").strip()
    }

    def bao_loi(thong_bao):
        flash(thong_bao, "danger")
        return render_template(
            "tai_xe/form.html",
            tai_xe=du_lieu,
            tieu_de="Thêm tài xế"
        )

    # 1. Kiem tra bat buoc
    if not all(du_lieu.values()):
        return bao_loi("Vui lòng nhập đầy đủ thông tin!")

    # 2. Kiem tra do dai
    gioi_han = {
        "HoTen": 100,
        "SoCCCD": 20,
        "SoBangLai": 20,
        "LoaiBangLai": 10,
        "DiaChi": 200,
        "SDT": 15,
        "Email": 100
    }

    for cot, do_dai in gioi_han.items():
        if len(du_lieu[cot]) > do_dai:
            return bao_loi(f"{cot} không được vượt quá {do_dai} ký tự!")

    # 3. Kiem tra CCCD
    if not re.fullmatch(r"\d{12}", du_lieu["SoCCCD"]):
        return bao_loi("CCCD phải gồm đúng 12 chữ số!")

    # 4. Kiem tra SDT
    if not re.fullmatch(r"0\d{9}", du_lieu["SDT"]):
        return bao_loi("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0!")

    # 5. Kiem tra Email
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", du_lieu["Email"]):
        return bao_loi("Email không đúng định dạng!")

    # 6. Kiem tra trang thai
    trang_thai_hop_le = (
        "Đang làm việc",
        "Nghỉ phép",
        "Tạm nghỉ",
        "Đã nghỉ việc"
    )

    if du_lieu["TrangThai"] not in trang_thai_hop_le:
        return bao_loi("Trạng thái tài xế không hợp lệ!")

    # 7. Kiem tra ngay
    try:
        ngay_sinh = date.fromisoformat(du_lieu["NgaySinh"])
        ngay_vao_nghe = date.fromisoformat(du_lieu["NgayVaoNghe"])

    except ValueError:
        return bao_loi("Ngày sinh hoặc ngày vào nghề không hợp lệ!")

    if ngay_sinh >= date.today():
        return bao_loi("Ngày sinh phải trước ngày hiện tại!")

    if ngay_vao_nghe < ngay_sinh:
        return bao_loi("Ngày vào nghề không thể trước ngày sinh!")

    if ngay_vao_nghe > date.today():
        return bao_loi("Ngày vào nghề không thể ở tương lai!")

    # 8. Ket noi MySQL
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Kiem tra 4 truong UNIQUE
        cursor.execute("""
            SELECT SoCCCD, SoBangLai, SDT, Email
            FROM TAI_XE
            WHERE SoCCCD = %s
               OR SoBangLai = %s
               OR SDT = %s
               OR Email = %s
        """, (
            du_lieu["SoCCCD"],
            du_lieu["SoBangLai"],
            du_lieu["SDT"],
            du_lieu["Email"]
        ))

        trung = cursor.fetchall()

        for tx in trung:
            if tx["SoCCCD"] == du_lieu["SoCCCD"]:
                return bao_loi("Số CCCD đã tồn tại!")

            if tx["SoBangLai"] == du_lieu["SoBangLai"]:
                return bao_loi("Số bằng lái đã tồn tại!")

            if tx["SDT"] == du_lieu["SDT"]:
                return bao_loi("Số điện thoại đã tồn tại!")

            if tx["Email"] == du_lieu["Email"]:
                return bao_loi("Email đã tồn tại!")

        # Them tai xe moi
        cursor.execute("""
            INSERT INTO TAI_XE (
                HoTen,
                SoCCCD,
                SoBangLai,
                LoaiBangLai,
                DiaChi,
                NgaySinh,
                NgayVaoNghe,
                SDT,
                Email,
                TrangThai
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """, (
            du_lieu["HoTen"],
            du_lieu["SoCCCD"],
            du_lieu["SoBangLai"],
            du_lieu["LoaiBangLai"],
            du_lieu["DiaChi"],
            ngay_sinh,
            ngay_vao_nghe,
            du_lieu["SDT"],
            du_lieu["Email"],
            du_lieu["TrangThai"]
        ))

        connection.commit()

        flash("Thêm tài xế thành công!", "success")

        return redirect(url_for("danh_sach_tai_xe"))

    except mysql.connector.IntegrityError as error:
        if connection:
            connection.rollback()

        if error.errno == 1062:
            return bao_loi(
                "CCCD, bằng lái, số điện thoại hoặc email đã tồn tại!"
            )

        app.logger.exception("Loi rang buoc khi them tai xe")
        return bao_loi("Dữ liệu vi phạm ràng buộc của cơ sở dữ liệu!")

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        app.logger.exception("Loi MySQL khi them tai xe")
        return bao_loi("Không thể thêm tài xế. Vui lòng thử lại!")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 8.4 - SUA THONG TIN TAI XE
# ==========================================================

@app.route("/tai-xe/sua/<int:ma_tai_xe>", methods=["GET", "POST"])
def sua_tai_xe(ma_tai_xe):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Lay thong tin tai xe can sua
        cursor.execute("""
            SELECT *
            FROM TAI_XE
            WHERE MaTaiXe = %s
        """, (ma_tai_xe,))

        tai_xe = cursor.fetchone()

        if tai_xe is None:
            flash("Không tìm thấy tài xế cần sửa!", "danger")
            return redirect(url_for("danh_sach_tai_xe"))

        # 2. GET: Hien thi thong tin hien tai
        if request.method == "GET":

            # Chuyen date thanh chuoi cho input type=date
            for cot in ("NgaySinh", "NgayVaoNghe"):
                if tai_xe[cot] is not None:
                    tai_xe[cot] = tai_xe[cot].isoformat()

            return render_template(
                "tai_xe/form.html",
                tai_xe=tai_xe,
                tieu_de="Sửa thông tin tài xế",
                ma_tai_xe=ma_tai_xe
            )

        # 3. POST: Lay du lieu moi
        du_lieu = {
            "HoTen": request.form.get("HoTen", "").strip(),
            "SoCCCD": request.form.get("SoCCCD", "").strip(),
            "SoBangLai": request.form.get("SoBangLai", "").strip(),
            "LoaiBangLai": request.form.get("LoaiBangLai", "").strip(),
            "DiaChi": request.form.get("DiaChi", "").strip(),
            "NgaySinh": request.form.get("NgaySinh", "").strip(),
            "NgayVaoNghe": request.form.get("NgayVaoNghe", "").strip(),
            "SDT": request.form.get("SDT", "").strip(),
            "Email": request.form.get("Email", "").strip(),
            "TrangThai": request.form.get("TrangThai", "").strip()
        }

        def bao_loi(thong_bao):
            flash(thong_bao, "danger")
            return render_template(
                "tai_xe/form.html",
                tai_xe=du_lieu,
                tieu_de="Sửa thông tin tài xế",
                ma_tai_xe=ma_tai_xe
            )

        # 4. Kiem tra bat buoc
        if not all(du_lieu.values()):
            return bao_loi("Vui lòng nhập đầy đủ thông tin!")

        # 5. Kiem tra do dai
        gioi_han = {
            "HoTen": 100,
            "SoCCCD": 20,
            "SoBangLai": 20,
            "LoaiBangLai": 10,
            "DiaChi": 200,
            "SDT": 15,
            "Email": 100
        }

        for cot, do_dai in gioi_han.items():
            if len(du_lieu[cot]) > do_dai:
                return bao_loi(
                    f"{cot} không được vượt quá {do_dai} ký tự!"
                )

        # 6. Kiem tra CCCD
        if not re.fullmatch(r"\d{12}", du_lieu["SoCCCD"]):
            return bao_loi("CCCD phải gồm đúng 12 chữ số!")

        # 7. Kiem tra SDT
        if not re.fullmatch(r"0\d{9}", du_lieu["SDT"]):
            return bao_loi(
                "Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0!"
            )

        # 8. Kiem tra Email
        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            du_lieu["Email"]
        ):
            return bao_loi("Email không đúng định dạng!")

        # 9. Kiem tra trang thai
        trang_thai_hop_le = (
            "Đang làm việc",
            "Nghỉ phép",
            "Tạm nghỉ",
            "Đã nghỉ việc"
        )

        if du_lieu["TrangThai"] not in trang_thai_hop_le:
            return bao_loi("Trạng thái tài xế không hợp lệ!")

        # 10. Kiem tra ngay
        try:
            ngay_sinh = date.fromisoformat(du_lieu["NgaySinh"])
            ngay_vao_nghe = date.fromisoformat(du_lieu["NgayVaoNghe"])

        except ValueError:
            return bao_loi(
                "Ngày sinh hoặc ngày vào nghề không hợp lệ!"
            )

        if ngay_sinh >= date.today():
            return bao_loi("Ngày sinh phải trước ngày hiện tại!")

        if ngay_vao_nghe < ngay_sinh:
            return bao_loi(
                "Ngày vào nghề không thể trước ngày sinh!"
            )

        if ngay_vao_nghe > date.today():
            return bao_loi(
                "Ngày vào nghề không thể ở tương lai!"
            )

        # 11. Kiem tra trung UNIQUE voi tai xe KHAC
        cursor.execute("""
            SELECT
                MaTaiXe,
                SoCCCD,
                SoBangLai,
                SDT,
                Email
            FROM TAI_XE
            WHERE MaTaiXe <> %s
              AND (
                    SoCCCD = %s
                 OR SoBangLai = %s
                 OR SDT = %s
                 OR Email = %s
              )
        """, (
            ma_tai_xe,
            du_lieu["SoCCCD"],
            du_lieu["SoBangLai"],
            du_lieu["SDT"],
            du_lieu["Email"]
        ))

        trung = cursor.fetchall()

        for tx in trung:

            if tx["SoCCCD"] == du_lieu["SoCCCD"]:
                return bao_loi("Số CCCD đã tồn tại!")

            if tx["SoBangLai"] == du_lieu["SoBangLai"]:
                return bao_loi("Số bằng lái đã tồn tại!")

            if tx["SDT"] == du_lieu["SDT"]:
                return bao_loi("Số điện thoại đã tồn tại!")

            if tx["Email"] == du_lieu["Email"]:
                return bao_loi("Email đã tồn tại!")

        # 12. UPDATE
        cursor.execute("""
            UPDATE TAI_XE
            SET
                HoTen = %s,
                SoCCCD = %s,
                SoBangLai = %s,
                LoaiBangLai = %s,
                DiaChi = %s,
                NgaySinh = %s,
                NgayVaoNghe = %s,
                SDT = %s,
                Email = %s,
                TrangThai = %s
            WHERE MaTaiXe = %s
        """, (
            du_lieu["HoTen"],
            du_lieu["SoCCCD"],
            du_lieu["SoBangLai"],
            du_lieu["LoaiBangLai"],
            du_lieu["DiaChi"],
            ngay_sinh,
            ngay_vao_nghe,
            du_lieu["SDT"],
            du_lieu["Email"],
            du_lieu["TrangThai"],
            ma_tai_xe
        ))

        connection.commit()

        flash("Cập nhật thông tin tài xế thành công!", "success")

        return redirect(url_for("danh_sach_tai_xe"))

    except mysql.connector.IntegrityError as error:

        if connection:
            connection.rollback()

        if error.errno == 1062:
            flash(
                "CCCD, bằng lái, SDT hoặc Email đã tồn tại!",
                "danger"
            )
        else:
            app.logger.exception("Loi rang buoc khi sua tai xe")
            flash("Dữ liệu vi phạm ràng buộc CSDL!", "danger")

        return redirect(
            url_for("sua_tai_xe", ma_tai_xe=ma_tai_xe)
        )

    except mysql.connector.Error:

        if connection:
            connection.rollback()

        app.logger.exception("Loi MySQL khi sua tai xe")
        flash("Không thể cập nhật tài xế!", "danger")

        return redirect(
            url_for("sua_tai_xe", ma_tai_xe=ma_tai_xe)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 8.5 - XOA TAI XE
# ==========================================================

@app.route("/tai-xe/xoa/<int:ma_tai_xe>", methods=["POST"])
def xoa_tai_xe(ma_tai_xe):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Khoa ban ghi tai xe trong transaction
        cursor.execute("""
            SELECT MaTaiXe, HoTen
            FROM TAI_XE
            WHERE MaTaiXe = %s
            FOR UPDATE
        """, (ma_tai_xe,))

        tai_xe = cursor.fetchone()

        if tai_xe is None:
            connection.rollback()
            flash("Không tìm thấy tài xế cần xóa!", "danger")
            return redirect(url_for("danh_sach_tai_xe"))

        # Kiem tra tai xe da duoc phan cong chuyen xe chua
        cursor.execute("""
            SELECT COUNT(*) AS SoChuyen
            FROM CHUYEN_XE
            WHERE MaTaiXe = %s
        """, (ma_tai_xe,))

        ket_qua = cursor.fetchone()

        if ket_qua["SoChuyen"] > 0:
            connection.rollback()

            flash(
                f"Không thể xóa tài xế {tai_xe['HoTen']} "
                f"vì đã được phân công {ket_qua['SoChuyen']} chuyến xe!",
                "danger"
            )

            return redirect(url_for("danh_sach_tai_xe"))

        # Xoa tai xe
        cursor.execute("""
            DELETE FROM TAI_XE
            WHERE MaTaiXe = %s
        """, (ma_tai_xe,))

        connection.commit()

        flash("Xóa tài xế thành công!", "success")

        return redirect(url_for("danh_sach_tai_xe"))

    except mysql.connector.Error as error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Loi khi xoa tai xe")

        if error.errno == 1451:
            flash(
                "Không thể xóa tài xế vì còn dữ liệu liên quan!",
                "danger"
            )
        else:
            flash(
                "Có lỗi xảy ra khi xóa tài xế!",
                "danger"
            )

        return redirect(url_for("danh_sach_tai_xe"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 9.1 - DANH SACH TUYEN DUONG
# ==========================================================

# ==========================================================
# 9.2 - TIM KIEM TUYEN DUONG THEO DIEM DI VA DIEM DEN
# ==========================================================

@app.route("/tuyen-duong", methods=["GET"])
def danh_sach_tuyen_duong():

    connection = None
    cursor = None

    # Lay gia tri tu 2 o tim kiem
    diem_di = request.args.get("diem_di", "").strip()
    diem_den = request.args.get("diem_den", "").strip()

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                MaTuyenDuong,
                TenTuyenDuong,
                DiemDi,
                DiemDen,
                ChieuDai,
                DoPhucTap,
                ThoiGianDi,
                TrangThai
            FROM TUYEN_DUONG
            WHERE 1 = 1
        """

        tham_so = []

        # Loc theo diem di
        if diem_di:
            sql += " AND DiemDi LIKE %s"
            tham_so.append(f"%{diem_di}%")

        # Loc theo diem den
        if diem_den:
            sql += " AND DiemDen LIKE %s"
            tham_so.append(f"%{diem_den}%")

        sql += " ORDER BY MaTuyenDuong ASC"

        cursor.execute(sql, tuple(tham_so))

        danh_sach = cursor.fetchall()

        return render_template(
            "tuyen_duong/danh_sach.html",
            danh_sach=danh_sach,
            diem_di=diem_di,
            diem_den=diem_den
        )

    except mysql.connector.Error:

        app.logger.exception(
            "Loi tim kiem tuyen duong"
        )

        return "Không thể tải danh sách tuyến đường.", 500

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 9.3 - THEM TUYEN DUONG
# ==========================================================

@app.route("/tuyen-duong/them", methods=["GET", "POST"])
def them_tuyen_duong():

    if request.method == "GET":
        return render_template(
            "tuyen_duong/form.html",
            tuyen={},
            tieu_de="Thêm tuyến đường"
        )

    # Lay du lieu tu form
    du_lieu = {
        "DiemDi": request.form.get("DiemDi", "").strip(),
        "DiemDen": request.form.get("DiemDen", "").strip(),
        "ChieuDai": request.form.get("ChieuDai", "").strip(),
        "DoPhucTap": request.form.get("DoPhucTap", "").strip(),
        "ThoiGianDi": request.form.get("ThoiGianDi", "").strip(),
        "TrangThai": request.form.get("TrangThai", "").strip()
    }

    def bao_loi(thong_bao):
        flash(thong_bao, "danger")

        return render_template(
            "tuyen_duong/form.html",
            tuyen=du_lieu,
            tieu_de="Thêm tuyến đường"
        )

    # 1. Kiem tra cac truong bat buoc
    if not all(du_lieu.values()):
        return bao_loi("Vui lòng nhập đầy đủ thông tin tuyến đường!")

    # 2. Kiem tra diem di va diem den
    diem_di = du_lieu["DiemDi"]
    diem_den = du_lieu["DiemDen"]

    if diem_di.casefold() == diem_den.casefold():
        return bao_loi("Điểm đi và điểm đến không được trùng nhau!")

    # 3. Tao ten tuyen tu dong
    ten_tuyen = f"{diem_di} - {diem_den}"

    # 4. Kiem tra cac gia tri so
    try:
        chieu_dai = Decimal(du_lieu["ChieuDai"])
        thoi_gian = Decimal(du_lieu["ThoiGianDi"])
        do_phuc_tap = int(du_lieu["DoPhucTap"])

    except (ValueError, InvalidOperation):
        return bao_loi("Chiều dài, thời gian hoặc độ phức tạp không hợp lệ!")

    if not chieu_dai.is_finite() or chieu_dai <= 0:
        return bao_loi("Chiều dài tuyến phải lớn hơn 0!")

    if not thoi_gian.is_finite() or thoi_gian <= 0:
        return bao_loi("Thời gian di chuyển phải lớn hơn 0!")

    # Tam thoi quy uoc do phuc tap tu 1 den 3
    if do_phuc_tap not in (1, 2, 3):
        return bao_loi("Độ phức tạp phải từ 1 đến 3!")

    if du_lieu["TrangThai"] not in ("0", "1"):
        return bao_loi("Trạng thái tuyến đường không hợp lệ!")

    trang_thai = int(du_lieu["TrangThai"])

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 5. Kiem tra tuyen duong trung
        cursor.execute("""
            SELECT MaTuyenDuong
            FROM TUYEN_DUONG
            WHERE DiemDi = %s
              AND DiemDen = %s
            LIMIT 1
        """, (diem_di, diem_den))

        tuyen_trung = cursor.fetchone()

        if tuyen_trung:
            return bao_loi(
                "Tuyến đường này đã tồn tại trong hệ thống!"
            )

        # 6. INSERT tuyen duong moi
        cursor.execute("""
            INSERT INTO TUYEN_DUONG (
                TenTuyenDuong,
                DiemDi,
                DiemDen,
                ChieuDai,
                DoPhucTap,
                ThoiGianDi,
                TrangThai
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            ten_tuyen,
            diem_di,
            diem_den,
            chieu_dai,
            do_phuc_tap,
            thoi_gian,
            trang_thai
        ))

        connection.commit()

        flash("Thêm tuyến đường thành công!", "success")

        return redirect(url_for("danh_sach_tuyen_duong"))

    except mysql.connector.IntegrityError as error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Loi rang buoc khi them tuyen duong")

        if error.errno == 1062:
            return bao_loi("Tuyến đường đã tồn tại!")

        return bao_loi(
            "Dữ liệu vi phạm ràng buộc của cơ sở dữ liệu!"
        )

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Loi MySQL khi them tuyen duong")

        return bao_loi(
            "Không thể thêm tuyến đường. Vui lòng thử lại!"
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 9.4 - SUA TUYEN DUONG (UPDATE)
# ==========================================================

@app.route("/tuyen-duong/sua/<int:ma_tuyen>", methods=["GET", "POST"])
def sua_tuyen_duong(ma_tuyen):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Lay thong tin tuyen duong can sua
        cursor.execute("""
            SELECT
                MaTuyenDuong,
                TenTuyenDuong,
                DiemDi,
                DiemDen,
                ChieuDai,
                DoPhucTap,
                ThoiGianDi,
                TrangThai
            FROM TUYEN_DUONG
            WHERE MaTuyenDuong = %s
        """, (ma_tuyen,))

        tuyen = cursor.fetchone()

        if tuyen is None:
            flash("Không tìm thấy tuyến đường cần sửa!", "danger")
            return redirect(url_for("danh_sach_tuyen_duong"))

        # 2. GET - Hien thi form sua
        if request.method == "GET":

            return render_template(
                "tuyen_duong/form.html",
                tuyen=tuyen,
                tieu_de="Sửa tuyến đường",
                che_do="sua"
            )

        # 3. POST - Lay du lieu tu form
        du_lieu = {
            "MaTuyenDuong": ma_tuyen,
            "DiemDi": request.form.get("DiemDi", "").strip(),
            "DiemDen": request.form.get("DiemDen", "").strip(),
            "ChieuDai": request.form.get("ChieuDai", "").strip(),
            "DoPhucTap": request.form.get("DoPhucTap", "").strip(),
            "ThoiGianDi": request.form.get("ThoiGianDi", "").strip(),
            "TrangThai": request.form.get("TrangThai", "").strip()
        }

        def bao_loi(thong_bao):

            flash(thong_bao, "danger")

            return render_template(
                "tuyen_duong/form.html",
                tuyen=du_lieu,
                tieu_de="Sửa tuyến đường",
                che_do="sua"
            )

        # 4. Kiem tra du lieu bat buoc
        cac_truong = (
            "DiemDi",
            "DiemDen",
            "ChieuDai",
            "DoPhucTap",
            "ThoiGianDi",
            "TrangThai"
        )

        if any(not du_lieu[truong] for truong in cac_truong):
            return bao_loi("Vui lòng nhập đầy đủ thông tin!")

        diem_di = du_lieu["DiemDi"]
        diem_den = du_lieu["DiemDen"]

        # 5. Kiem tra diem di va diem den
        if diem_di.casefold() == diem_den.casefold():
            return bao_loi(
                "Điểm đi và điểm đến không được trùng nhau!"
            )

        # 6. Tu dong tao ten tuyen
        ten_tuyen = f"{diem_di} - {diem_den}"

        # 7. Kiem tra gia tri so
        try:
            chieu_dai = Decimal(du_lieu["ChieuDai"])
            thoi_gian = Decimal(du_lieu["ThoiGianDi"])
            do_phuc_tap = int(du_lieu["DoPhucTap"])

        except (ValueError, InvalidOperation):
            return bao_loi(
                "Chiều dài, thời gian hoặc độ phức tạp không hợp lệ!"
            )

        if not chieu_dai.is_finite() or chieu_dai <= 0:
            return bao_loi("Chiều dài phải lớn hơn 0!")

        if not thoi_gian.is_finite() or thoi_gian <= 0:
            return bao_loi("Thời gian phải lớn hơn 0!")

        if do_phuc_tap not in (1, 2, 3):
            return bao_loi("Độ phức tạp phải từ 1 đến 3!")

        if du_lieu["TrangThai"] not in ("0", "1"):
            return bao_loi("Trạng thái không hợp lệ!")

        trang_thai = int(du_lieu["TrangThai"])

        # 8. Kiem tra trung tuyen duong
        # Loai tru chinh tuyen dang sua
        cursor.execute("""
            SELECT MaTuyenDuong
            FROM TUYEN_DUONG
            WHERE DiemDi = %s
              AND DiemDen = %s
              AND MaTuyenDuong <> %s
            LIMIT 1
        """, (
            diem_di,
            diem_den,
            ma_tuyen
        ))

        tuyen_trung = cursor.fetchone()

        if tuyen_trung:
            return bao_loi(
                "Đã tồn tại tuyến đường khác có cùng điểm đi và điểm đến!"
            )

        # 9. UPDATE du lieu
        cursor.execute("""
            UPDATE TUYEN_DUONG
            SET
                TenTuyenDuong = %s,
                DiemDi = %s,
                DiemDen = %s,
                ChieuDai = %s,
                DoPhucTap = %s,
                ThoiGianDi = %s,
                TrangThai = %s
            WHERE MaTuyenDuong = %s
        """, (
            ten_tuyen,
            diem_di,
            diem_den,
            chieu_dai,
            do_phuc_tap,
            thoi_gian,
            trang_thai,
            ma_tuyen
        ))

        connection.commit()

        flash("Cập nhật tuyến đường thành công!", "success")

        return redirect(url_for("danh_sach_tuyen_duong"))

    except mysql.connector.IntegrityError as error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Loi rang buoc khi sua tuyen duong")

        if error.errno == 1062:
            flash("Tuyến đường đã tồn tại!", "danger")
        else:
            flash("Dữ liệu vi phạm ràng buộc cơ sở dữ liệu!", "danger")

        return redirect(url_for("danh_sach_tuyen_duong"))

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Loi MySQL khi sua tuyen duong")

        flash("Không thể cập nhật tuyến đường!", "danger")

        return redirect(url_for("danh_sach_tuyen_duong"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 9.5 - XÓA TUYẾN ĐƯỜNG
# ==========================================================

@app.route("/tuyen-duong/xoa/<int:ma_tuyen>", methods=["POST"])
def xoa_tuyen_duong(ma_tuyen):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiểm tra tuyến đường có tồn tại không
        cursor.execute("""
            SELECT MaTuyenDuong
            FROM TUYEN_DUONG
            WHERE MaTuyenDuong = %s
        """, (ma_tuyen,))

        tuyen = cursor.fetchone()

        if tuyen is None:
            flash("Không tìm thấy tuyến đường cần xóa!", "danger")
            return redirect(url_for("danh_sach_tuyen_duong"))

        # 2. Kiểm tra tuyến đường có chuyến xe liên quan không
        cursor.execute("""
            SELECT 1
            FROM CHUYEN_XE
            WHERE MaTuyenDuong = %s
            LIMIT 1
        """, (ma_tuyen,))

        chuyen_xe = cursor.fetchone()

        if chuyen_xe is not None:
            flash(
                "Không thể xóa tuyến đường vì đã có chuyến xe liên quan!",
                "danger"
            )
            return redirect(url_for("danh_sach_tuyen_duong"))

        # 3. Xóa tuyến đường
        cursor.execute("""
            DELETE FROM TUYEN_DUONG
            WHERE MaTuyenDuong = %s
        """, (ma_tuyen,))

        connection.commit()

        flash("Xóa tuyến đường thành công!", "success")

        return redirect(url_for("danh_sach_tuyen_duong"))

    except mysql.connector.IntegrityError:
        if connection is not None:
            connection.rollback()

        app.logger.exception("Lỗi ràng buộc khi xóa tuyến đường")

        flash(
            "Không thể xóa tuyến đường do ràng buộc dữ liệu!",
            "danger"
        )

        return redirect(url_for("danh_sach_tuyen_duong"))

    except mysql.connector.Error:
        if connection is not None:
            connection.rollback()

        app.logger.exception("Lỗi MySQL khi xóa tuyến đường")

        flash("Có lỗi xảy ra khi xóa tuyến đường!", "danger")

        return redirect(url_for("danh_sach_tuyen_duong"))

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.6 - DANH SÁCH VÀ TÌM KIẾM CHUYẾN XE
# CẬP NHẬT 10.9 - HỖ TRỢ ẨN / KHÔI PHỤC
# ==========================================================

@app.route("/chuyen-xe", methods=["GET"])
def danh_sach_chuyen_xe():

    from datetime import datetime

    connection = None
    cursor = None

    # 1. Nhận dữ liệu tìm kiếm từ URL
    ma_chuyen = request.args.get("ma_chuyen", "").strip()
    bien_so = request.args.get("bien_so", "").strip()
    trang_thai = request.args.get("trang_thai", "").strip()
    ma_tuyen = request.args.get("ma_tuyen", "").strip()

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 2. Câu SQL lấy danh sách chuyến xe
        sql = """
            SELECT
                cx.MaChuyen,

                cx.MaXe,
                x.BienSo,

                cx.MaTaiXe,
                tx.HoTen AS TenTaiXe,

                cx.MaPhuXe,
                px.HoTen AS TenPhuXe,

                cx.MaTuyenDuong,
                td.DiemDi,
                td.DiemDen,

                cx.SoKhach,
                cx.ThoiGianKhoiHanh,
                cx.SoKmThucTe,
                cx.GiaVe,
                cx.TrangThai,

                cx.DaAn,
                cx.NgayAn

            FROM CHUYEN_XE AS cx

            LEFT JOIN XE AS x
                ON cx.MaXe = x.MaXe

            LEFT JOIN TAI_XE AS tx
                ON cx.MaTaiXe = tx.MaTaiXe

            LEFT JOIN TAI_XE AS px
                ON cx.MaPhuXe = px.MaTaiXe

            LEFT JOIN TUYEN_DUONG AS td
                ON cx.MaTuyenDuong = td.MaTuyenDuong

            WHERE cx.DaAn = FALSE
        """

        params = []

        # 3. Tìm theo mã chuyến
        if ma_chuyen:
            if ma_chuyen.isdecimal():
                sql += " AND cx.MaChuyen = %s"
                params.append(int(ma_chuyen))
            else:
                sql += " AND 1 = 0"

        # 4. Tìm theo biển số xe
        if bien_so:
            sql += " AND x.BienSo LIKE %s"
            params.append(f"%{bien_so}%")

        # 5. Lọc theo trạng thái
        if trang_thai:
            sql += " AND cx.TrangThai = %s"
            params.append(trang_thai)

        # 6. Lọc theo tuyến đường
        if ma_tuyen:
            if ma_tuyen.isdecimal():
                sql += " AND cx.MaTuyenDuong = %s"
                params.append(int(ma_tuyen))
            else:
                sql += " AND 1 = 0"

        # 7. Sắp xếp chuyến xe mới nhất lên đầu
        sql += " ORDER BY cx.MaChuyen DESC"

        # 8. Thực hiện truy vấn
        cursor.execute(sql, tuple(params))
        danh_sach = cursor.fetchall()

        # 9. Lấy danh sách tuyến đường cho bộ lọc
        cursor.execute("""
            SELECT
                MaTuyenDuong,
                DiemDi,
                DiemDen
            FROM TUYEN_DUONG
            ORDER BY MaTuyenDuong
        """)

        danh_sach_tuyen = cursor.fetchall()

        # 10. Lấy thời gian hiện tại
        # Dùng để kiểm tra chuyến đã đến giờ khởi hành
        now = datetime.now()

        # 11. Trả dữ liệu về HTML
        return render_template(
            "chuyen_xe/danh_sach.html",

            danh_sach=danh_sach,
            danh_sach_tuyen=danh_sach_tuyen,

            ma_chuyen=ma_chuyen,
            bien_so=bien_so,
            trang_thai=trang_thai,
            ma_tuyen=ma_tuyen,

            # Bổ sung cho bước 10.9
            now=now,
            che_do_danh_sach="hien_tai"
        )

    except mysql.connector.Error:

        app.logger.exception(
            "Lỗi MySQL khi tìm kiếm chuyến xe"
        )

        flash(
            "Không thể tải danh sách chuyến xe!",
            "danger"
        )

        return redirect(url_for("dashboard"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.7 - THÊM CHUYẾN XE
# ==========================================================

@app.route("/chuyen-xe/them", methods=["GET", "POST"])
def them_chuyen_xe():

    connection = None
    cursor = None

    trang_thai_hop_le = [
        "Đã lên lịch",
        "Đang chạy",
        "Đã hoàn thành",
        "Đã hủy"
    ]

    du_lieu = {
        "MaXe": "",
        "MaTaiXe": "",
        "MaPhuXe": "",
        "MaTuyenDuong": "",
        "SoKhach": "",
        "ThoiGianKhoiHanh": "",
        "SoKmThucTe": "0",
        "GiaVe": "",
        "TrangThai": "Đã lên lịch"
    }

    danh_sach_xe = []
    danh_sach_tai_xe = []
    danh_sach_tuyen = []

    loi = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Lấy danh sách xe
        cursor.execute("""
            SELECT MaXe, BienSo, SoChoNgoi, TrangThai
            FROM XE
            ORDER BY BienSo
        """)

        danh_sach_xe = cursor.fetchall()

        # 2. Lấy danh sách tài xế
        # MaTaiXe và MaPhuXe đều tham chiếu TAI_XE
        cursor.execute("""
            SELECT MaTaiXe, HoTen, TrangThai
            FROM TAI_XE
            ORDER BY HoTen
        """)

        danh_sach_tai_xe = cursor.fetchall()

        # 3. Lấy danh sách tuyến đường
        cursor.execute("""
            SELECT
                MaTuyenDuong,
                TenTuyenDuong,
                DiemDi,
                DiemDen,
                TrangThai
            FROM TUYEN_DUONG
            ORDER BY MaTuyenDuong
        """)

        danh_sach_tuyen = cursor.fetchall()

        # 4. Nếu GET thì hiển thị form
        if request.method == "GET":
            return render_template(
                "chuyen_xe/form.html",
                du_lieu=du_lieu,
                danh_sach_xe=danh_sach_xe,
                danh_sach_tai_xe=danh_sach_tai_xe,
                danh_sach_tuyen=danh_sach_tuyen,
                loi=loi
            )

        # 5. Lấy dữ liệu POST
        for truong in du_lieu:
            du_lieu[truong] = request.form.get(
                truong, ""
            ).strip()

        # 6. Kiểm tra trường bắt buộc
        truong_bat_buoc = [
            "MaXe",
            "MaTaiXe",
            "MaPhuXe",
            "MaTuyenDuong",
            "SoKhach",
            "ThoiGianKhoiHanh",
            "SoKmThucTe",
            "GiaVe",
            "TrangThai"
        ]

        if any(not du_lieu[t] for t in truong_bat_buoc):
            loi = "Vui lòng nhập đầy đủ thông tin chuyến xe."

        # 7. Kiểm tra dữ liệu
        if loi is None:

            try:
                from datetime import datetime

                ma_xe = int(du_lieu["MaXe"])
                ma_tai_xe = int(du_lieu["MaTaiXe"])
                ma_phu_xe = int(du_lieu["MaPhuXe"])
                ma_tuyen = int(du_lieu["MaTuyenDuong"])
                so_khach = int(du_lieu["SoKhach"])

                so_km = Decimal(du_lieu["SoKmThucTe"])
                gia_ve = Decimal(du_lieu["GiaVe"])

                thoi_gian = datetime.strptime(
                    du_lieu["ThoiGianKhoiHanh"],
                    "%Y-%m-%dT%H:%M"
                )

                trang_thai = du_lieu["TrangThai"]

                if min(
                    ma_xe,
                    ma_tai_xe,
                    ma_phu_xe,
                    ma_tuyen
                ) <= 0:
                    loi = "Mã xe, tài xế và tuyến đường không hợp lệ."

                elif ma_tai_xe == ma_phu_xe:
                    loi = "Tài xế chính và phụ xe phải là hai người khác nhau."

                elif so_khach < 0:
                    loi = "Số khách không được âm."

                elif not so_km.is_finite() or so_km < 0:
                    loi = "Số km thực tế phải lớn hơn hoặc bằng 0."

                elif not gia_ve.is_finite() or gia_ve <= 0:
                    loi = "Giá vé phải lớn hơn 0."

                elif so_km >= Decimal("100000000"):
                    loi = "Số km thực tế vượt quá giới hạn cho phép."

                elif gia_ve >= Decimal("10000000000000"):
                    loi = "Giá vé vượt quá giới hạn cho phép."

                elif trang_thai not in trang_thai_hop_le:
                    loi = "Trạng thái chuyến xe không hợp lệ."

            except (ValueError, InvalidOperation):
                loi = "Dữ liệu số hoặc thời gian không hợp lệ."

        # 8. Kiểm tra xe, tài xế, phụ xe và tuyến đường
        if loi is None:

            cursor.execute("""
                SELECT SoChoNgoi, TrangThai
                FROM XE
                WHERE MaXe = %s
            """, (ma_xe,))

            xe = cursor.fetchone()

            if xe is None:
                loi = "Xe được chọn không tồn tại."

            elif not xe["TrangThai"]:
                loi = "Xe được chọn đang không hoạt động."

            elif so_khach > xe["SoChoNgoi"]:
                loi = (
                    f"Số khách ({so_khach}) vượt quá "
                    f"số chỗ ngồi của xe ({xe['SoChoNgoi']})."
                )

        if loi is None:

            cursor.execute("""
                SELECT MaTaiXe, TrangThai
                FROM TAI_XE
                WHERE MaTaiXe IN (%s, %s)
            """, (ma_tai_xe, ma_phu_xe))

            nhan_su = {
                dong["MaTaiXe"]: dong["TrangThai"]
                for dong in cursor.fetchall()
            }

            if ma_tai_xe not in nhan_su:
                loi = "Tài xế chính không tồn tại."

            elif ma_phu_xe not in nhan_su:
                loi = "Phụ xe không tồn tại."

            elif nhan_su[ma_tai_xe] != "Đang làm việc":
                loi = "Tài xế chính không ở trạng thái đang làm việc."

            elif nhan_su[ma_phu_xe] != "Đang làm việc":
                loi = "Phụ xe không ở trạng thái đang làm việc."

        if loi is None:

            cursor.execute("""
                SELECT TrangThai
                FROM TUYEN_DUONG
                WHERE MaTuyenDuong = %s
            """, (ma_tuyen,))

            tuyen = cursor.fetchone()

            if tuyen is None:
                loi = "Tuyến đường được chọn không tồn tại."

            elif not tuyen["TrangThai"]:
                loi = "Tuyến đường được chọn đang ngừng hoạt động."

        # 9. Kiểm tra trùng lịch xe
        # Không cho cùng xe có hai chuyến tại đúng một thời điểm
        if loi is None and trang_thai != "Đã hủy":

            cursor.execute("""
                SELECT MaChuyen
                FROM CHUYEN_XE
                WHERE MaXe = %s
                  AND ThoiGianKhoiHanh = %s
                  AND TrangThai <> 'Đã hủy'
                LIMIT 1
            """, (ma_xe, thoi_gian))

            if cursor.fetchone():
                loi = (
                    "Xe này đã có chuyến khác "
                    "khởi hành cùng thời điểm."
                )

        # 10. INSERT
        if loi is None:

            cursor.execute("""
                INSERT INTO CHUYEN_XE (
                    MaXe,
                    MaTaiXe,
                    MaPhuXe,
                    MaTuyenDuong,
                    SoKhach,
                    ThoiGianKhoiHanh,
                    SoKmThucTe,
                    GiaVe,
                    TrangThai
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
            """, (
                ma_xe,
                ma_tai_xe,
                ma_phu_xe,
                ma_tuyen,
                so_khach,
                thoi_gian,
                so_km,
                gia_ve,
                trang_thai
            ))

            connection.commit()

            flash(
                "Thêm chuyến xe thành công!",
                "success"
            )

            return redirect(
                url_for("danh_sach_chuyen_xe")
            )

        # 11. Nếu dữ liệu sai thì giữ lại form
        return render_template(
            "chuyen_xe/form.html",
            du_lieu=du_lieu,
            danh_sach_xe=danh_sach_xe,
            danh_sach_tai_xe=danh_sach_tai_xe,
            danh_sach_tuyen=danh_sach_tuyen,
            loi=loi
        ), 400

    except mysql.connector.IntegrityError:

        if connection is not None:
            connection.rollback()

        app.logger.exception(
            "Lỗi ràng buộc khi thêm chuyến xe"
        )

        flash(
            "Không thể thêm chuyến xe do vi phạm ràng buộc dữ liệu!",
            "danger"
        )

        return redirect(
            url_for("danh_sach_chuyen_xe")
        )

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception(
            "Lỗi MySQL khi thêm chuyến xe"
        )

        flash(
            "Có lỗi cơ sở dữ liệu khi thêm chuyến xe!",
            "danger"
        )

        return redirect(
            url_for("danh_sach_chuyen_xe")
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.8 - SỬA THÔNG TIN CHUYẾN XE
# ==========================================================

@app.route("/chuyen-xe/sua/<int:ma_chuyen>", methods=["GET", "POST"])
def sua_chuyen_xe(ma_chuyen):

    connection = None
    cursor = None

    trang_thai_hop_le = [
        "Đã lên lịch",
        "Đang chạy",
        "Đã hoàn thành",
        "Đã hủy"
    ]

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # ==================================================
        # 1. KIỂM TRA CHUYẾN XE CÓ TỒN TẠI KHÔNG
        # ==================================================

        cursor.execute("""
            SELECT
                MaChuyen,
                MaXe,
                MaTaiXe,
                MaPhuXe,
                MaTuyenDuong,
                SoKhach,
                ThoiGianKhoiHanh,
                SoKmThucTe,
                GiaVe,
                TrangThai
            FROM CHUYEN_XE
            WHERE MaChuyen = %s
        """, (ma_chuyen,))

        chuyen = cursor.fetchone()

        if chuyen is None:
            flash("Không tìm thấy chuyến xe cần sửa!", "danger")
            return redirect(url_for("danh_sach_chuyen_xe"))

        # ==================================================
        # 2. LẤY DANH SÁCH XE
        # ==================================================

        cursor.execute("""
            SELECT
                MaXe,
                BienSo,
                SoChoNgoi,
                TrangThai
            FROM XE
            ORDER BY BienSo
        """)

        danh_sach_xe = cursor.fetchall()

        # ==================================================
        # 3. LẤY DANH SÁCH TÀI XẾ
        # ==================================================

        cursor.execute("""
            SELECT
                MaTaiXe,
                HoTen,
                TrangThai
            FROM TAI_XE
            ORDER BY HoTen
        """)

        danh_sach_tai_xe = cursor.fetchall()

        # ==================================================
        # 4. LẤY DANH SÁCH TUYẾN ĐƯỜNG
        # ==================================================

        cursor.execute("""
            SELECT
                MaTuyenDuong,
                DiemDi,
                DiemDen,
                TrangThai
            FROM TUYEN_DUONG
            ORDER BY MaTuyenDuong
        """)

        danh_sach_tuyen = cursor.fetchall()

        # ==================================================
        # 5. CHUẨN BỊ DỮ LIỆU CŨ CHO FORM
        # ==================================================

        du_lieu = {
            "MaXe": str(chuyen["MaXe"]),
            "MaTaiXe": str(chuyen["MaTaiXe"]),
            "MaPhuXe": str(chuyen["MaPhuXe"]),
            "MaTuyenDuong": str(chuyen["MaTuyenDuong"]),
            "SoKhach": str(chuyen["SoKhach"]),
            "ThoiGianKhoiHanh": (
                chuyen["ThoiGianKhoiHanh"].strftime("%Y-%m-%dT%H:%M")
                if chuyen["ThoiGianKhoiHanh"]
                else ""
            ),
            "SoKmThucTe": str(chuyen["SoKmThucTe"]),
            "GiaVe": str(chuyen["GiaVe"]),
            "TrangThai": chuyen["TrangThai"]
        }

        # ==================================================
        # 6. GET - HIỂN THỊ FORM SỬA
        # ==================================================

        if request.method == "GET":

            return render_template(
                "chuyen_xe/form.html",
                che_do="sua",
                ma_chuyen=ma_chuyen,
                du_lieu=du_lieu,
                danh_sach_xe=danh_sach_xe,
                danh_sach_tai_xe=danh_sach_tai_xe,
                danh_sach_tuyen=danh_sach_tuyen,
                loi=None
            )

        # ==================================================
        # 7. POST - LẤY DỮ LIỆU TỪ FORM
        # ==================================================

        for truong in du_lieu:
            du_lieu[truong] = request.form.get(
                truong, ""
            ).strip()

        loi = None

        # ==================================================
        # 8. KIỂM TRA CÁC TRƯỜNG BẮT BUỘC
        # ==================================================

        truong_bat_buoc = [
            "MaXe",
            "MaTaiXe",
            "MaPhuXe",
            "MaTuyenDuong",
            "SoKhach",
            "ThoiGianKhoiHanh",
            "SoKmThucTe",
            "GiaVe",
            "TrangThai"
        ]

        if any(not du_lieu[t] for t in truong_bat_buoc):
            loi = "Vui lòng nhập đầy đủ thông tin chuyến xe."

        # ==================================================
        # 9. KIỂM TRA KIỂU DỮ LIỆU
        # ==================================================

        if loi is None:

            try:
                from datetime import datetime

                ma_xe = int(du_lieu["MaXe"])
                ma_tai_xe = int(du_lieu["MaTaiXe"])
                ma_phu_xe = int(du_lieu["MaPhuXe"])
                ma_tuyen = int(du_lieu["MaTuyenDuong"])
                so_khach = int(du_lieu["SoKhach"])

                so_km = Decimal(du_lieu["SoKmThucTe"])
                gia_ve = Decimal(du_lieu["GiaVe"])

                thoi_gian = datetime.strptime(
                    du_lieu["ThoiGianKhoiHanh"],
                    "%Y-%m-%dT%H:%M"
                )

                trang_thai = du_lieu["TrangThai"]

                if min(
                    ma_xe,
                    ma_tai_xe,
                    ma_phu_xe,
                    ma_tuyen
                ) <= 0:
                    loi = "Thông tin xe, nhân sự hoặc tuyến đường không hợp lệ."

                elif ma_tai_xe == ma_phu_xe:
                    loi = "Tài xế chính và phụ xe không được trùng nhau."

                elif so_khach < 0:
                    loi = "Số khách không được âm."

                elif not so_km.is_finite() or so_km < 0:
                    loi = "Số km thực tế không hợp lệ."

                elif not gia_ve.is_finite() or gia_ve <= 0:
                    loi = "Giá vé phải lớn hơn 0."

                elif so_km >= Decimal("100000000"):
                    loi = "Số km thực tế vượt giới hạn cho phép."

                elif gia_ve >= Decimal("10000000000000"):
                    loi = "Giá vé vượt giới hạn cho phép."

                elif trang_thai not in trang_thai_hop_le:
                    loi = "Trạng thái chuyến xe không hợp lệ."

            except (ValueError, InvalidOperation):
                loi = "Dữ liệu số hoặc thời gian không hợp lệ."

        # ==================================================
        # 10. KIỂM TRA XE
        # ==================================================

        if loi is None:

            cursor.execute("""
                SELECT
                    SoChoNgoi,
                    TrangThai
                FROM XE
                WHERE MaXe = %s
            """, (ma_xe,))

            xe = cursor.fetchone()

            if xe is None:
                loi = "Xe được chọn không tồn tại."

            elif not xe["TrangThai"] and ma_xe != chuyen["MaXe"]:
                loi = "Không thể chuyển sang xe đang ngừng hoạt động."

            elif so_khach > xe["SoChoNgoi"]:
                loi = (
                    f"Số khách ({so_khach}) vượt quá "
                    f"số chỗ ngồi ({xe['SoChoNgoi']})."
                )

        # ==================================================
        # 11. KIỂM TRA TÀI XẾ VÀ PHỤ XE
        # ==================================================

        if loi is None:

            cursor.execute("""
                SELECT
                    MaTaiXe,
                    TrangThai
                FROM TAI_XE
                WHERE MaTaiXe IN (%s, %s)
            """, (ma_tai_xe, ma_phu_xe))

            nhan_su = {
                dong["MaTaiXe"]: dong["TrangThai"]
                for dong in cursor.fetchall()
            }

            if ma_tai_xe not in nhan_su:
                loi = "Tài xế chính không tồn tại."

            elif ma_phu_xe not in nhan_su:
                loi = "Phụ xe không tồn tại."

            elif (
                ma_tai_xe != chuyen["MaTaiXe"]
                and nhan_su[ma_tai_xe] != "Đang làm việc"
            ):
                loi = "Tài xế mới không ở trạng thái đang làm việc."

            elif (
                ma_phu_xe != chuyen["MaPhuXe"]
                and nhan_su[ma_phu_xe] != "Đang làm việc"
            ):
                loi = "Phụ xe mới không ở trạng thái đang làm việc."

        # ==================================================
        # 12. KIỂM TRA TUYẾN ĐƯỜNG
        # ==================================================

        if loi is None:

            cursor.execute("""
                SELECT TrangThai
                FROM TUYEN_DUONG
                WHERE MaTuyenDuong = %s
            """, (ma_tuyen,))

            tuyen = cursor.fetchone()

            if tuyen is None:
                loi = "Tuyến đường không tồn tại."

            elif (
                not tuyen["TrangThai"]
                and ma_tuyen != chuyen["MaTuyenDuong"]
            ):
                loi = "Không thể chuyển sang tuyến đường ngừng hoạt động."

        # ==================================================
        # 13. KIỂM TRA TRÙNG LỊCH XE
        # ==================================================

        if loi is None and trang_thai != "Đã hủy":

            cursor.execute("""
                SELECT MaChuyen
                FROM CHUYEN_XE
                WHERE MaXe = %s
                  AND ThoiGianKhoiHanh = %s
                  AND MaChuyen <> %s
                  AND TrangThai <> 'Đã hủy'
                LIMIT 1
            """, (
                ma_xe,
                thoi_gian,
                ma_chuyen
            ))

            if cursor.fetchone():
                loi = (
                    "Xe này đã có chuyến khác "
                    "khởi hành cùng thời điểm."
                )

        # ==================================================
        # 14. UPDATE CHUYẾN XE
        # ==================================================

        if loi is None:

            cursor.execute("""
                UPDATE CHUYEN_XE
                SET
                    MaXe = %s,
                    MaTaiXe = %s,
                    MaPhuXe = %s,
                    MaTuyenDuong = %s,
                    SoKhach = %s,
                    ThoiGianKhoiHanh = %s,
                    SoKmThucTe = %s,
                    GiaVe = %s,
                    TrangThai = %s
                WHERE MaChuyen = %s
            """, (
                ma_xe,
                ma_tai_xe,
                ma_phu_xe,
                ma_tuyen,
                so_khach,
                thoi_gian,
                so_km,
                gia_ve,
                trang_thai,
                ma_chuyen
            ))

            connection.commit()

            flash(
                "Cập nhật chuyến xe thành công!",
                "success"
            )

            return redirect(
                url_for("danh_sach_chuyen_xe")
            )

        # ==================================================
        # 15. CÓ LỖI - HIỂN THỊ LẠI FORM
        # ==================================================

        return render_template(
            "chuyen_xe/form.html",
            che_do="sua",
            ma_chuyen=ma_chuyen,
            du_lieu=du_lieu,
            danh_sach_xe=danh_sach_xe,
            danh_sach_tai_xe=danh_sach_tai_xe,
            danh_sach_tuyen=danh_sach_tuyen,
            loi=loi
        ), 400

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception(
            "Lỗi MySQL khi sửa chuyến xe"
        )

        flash(
            "Không thể cập nhật chuyến xe!",
            "danger"
        )

        return redirect(
            url_for("danh_sach_chuyen_xe")
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.9.1 - XÓA CHUYẾN XE CÓ ĐIỀU KIỆN
# ==========================================================

@app.route("/chuyen-xe/xoa/<int:ma_chuyen>", methods=["POST"])
def xoa_chuyen_xe(ma_chuyen):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Khóa bản ghi trong lúc kiểm tra và xóa
        cursor.execute("""
            SELECT
                MaChuyen,
                TrangThai,
                ThoiGianKhoiHanh,
                DaAn
            FROM CHUYEN_XE
            WHERE MaChuyen = %s
            FOR UPDATE
        """, (ma_chuyen,))

        chuyen = cursor.fetchone()

        if chuyen is None:
            flash("Không tìm thấy chuyến xe cần xóa!", "danger")
            return redirect(url_for("danh_sach_chuyen_xe"))

        # 2. Chỉ cho xóa chuyến đã lên lịch
        if chuyen["TrangThai"] != "Đã lên lịch":
            flash(
                "Chỉ được xóa chuyến xe đang ở trạng thái Đã lên lịch!",
                "danger"
            )
            return redirect(url_for("danh_sach_chuyen_xe"))

        # 3. Chỉ cho xóa chuyến chưa đến giờ khởi hành
        from datetime import datetime

        if chuyen["ThoiGianKhoiHanh"] <= datetime.now():
            flash(
                "Không thể xóa chuyến xe đã đến hoặc qua giờ khởi hành!",
                "danger"
            )
            return redirect(url_for("danh_sach_chuyen_xe"))

        # 4. Không xóa chuyến đã ẩn
        if chuyen["DaAn"]:
            flash(
                "Chuyến xe đã được lưu trữ, không thể xóa!",
                "danger"
            )
            return redirect(url_for("danh_sach_chuyen_xe"))

        # 5. Tìm các bảng có khóa ngoại tham chiếu CHUYEN_XE
        cursor.execute("""
            SELECT
                TABLE_NAME,
                COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_SCHEMA = DATABASE()
              AND REFERENCED_TABLE_NAME = 'CHUYEN_XE'
              AND REFERENCED_COLUMN_NAME = 'MaChuyen'
        """)

        bang_lien_quan = cursor.fetchall()

        # 6. Kiểm tra dữ liệu liên quan
        for bang in bang_lien_quan:

            ten_bang = bang["TABLE_NAME"]
            ten_cot = bang["COLUMN_NAME"]

            # Tên bảng/cột lấy từ metadata của MySQL.
            ten_bang_sql = ten_bang.replace("`", "``")
            ten_cot_sql = ten_cot.replace("`", "``")

            cursor.execute(
                f"""
                SELECT 1
                FROM `{ten_bang_sql}`
                WHERE `{ten_cot_sql}` = %s
                LIMIT 1
                """,
                (ma_chuyen,)
            )

            if cursor.fetchone():
                flash(
                    f"Không thể xóa chuyến xe #{ma_chuyen} "
                    f"vì đã có dữ liệu liên quan trong bảng {ten_bang}.",
                    "danger"
                )
                return redirect(url_for("danh_sach_chuyen_xe"))

        # 7. Xóa vĩnh viễn
        cursor.execute("""
            DELETE FROM CHUYEN_XE
            WHERE MaChuyen = %s
        """, (ma_chuyen,))

        connection.commit()

        flash(
            f"Đã xóa chuyến xe #{ma_chuyen} thành công!",
            "success"
        )

        return redirect(url_for("danh_sach_chuyen_xe"))

    except mysql.connector.IntegrityError:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Lỗi ràng buộc khi xóa chuyến xe")

        flash(
            "Không thể xóa chuyến xe vì có dữ liệu liên quan!",
            "danger"
        )

        return redirect(url_for("danh_sach_chuyen_xe"))

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Lỗi MySQL khi xóa chuyến xe")

        flash("Có lỗi khi xóa chuyến xe!", "danger")

        return redirect(url_for("danh_sach_chuyen_xe"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.9.2 - ẨN CHUYẾN XE
# ==========================================================

@app.route("/chuyen-xe/an/<int:ma_chuyen>", methods=["POST"])
def an_chuyen_xe(ma_chuyen):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiểm tra chuyến xe
        cursor.execute("""
            SELECT
                MaChuyen,
                TrangThai,
                DaAn
            FROM CHUYEN_XE
            WHERE MaChuyen = %s
            FOR UPDATE
        """, (ma_chuyen,))

        chuyen = cursor.fetchone()

        if chuyen is None:
            flash("Không tìm thấy chuyến xe!", "danger")
            return redirect(url_for("danh_sach_chuyen_xe"))

        # 2. Chỉ cho ẩn chuyến đã hoàn thành hoặc đã hủy
        if chuyen["TrangThai"] not in ["Đã hoàn thành", "Đã hủy"]:

            flash(
                "Chỉ được ẩn chuyến xe đã hoàn thành hoặc đã hủy!",
                "danger"
            )

            return redirect(url_for("danh_sach_chuyen_xe"))

        # 3. Kiểm tra đã ẩn chưa
        if chuyen["DaAn"]:

            flash("Chuyến xe này đã được ẩn trước đó!", "warning")

            return redirect(url_for("danh_sach_chuyen_xe"))

        # 4. Cập nhật trạng thái ẩn
        cursor.execute("""
            UPDATE CHUYEN_XE
            SET
                DaAn = TRUE,
                NgayAn = NOW()
            WHERE MaChuyen = %s
        """, (ma_chuyen,))

        connection.commit()

        flash(
            f"Đã đưa chuyến xe #{ma_chuyen} vào danh sách lưu trữ!",
            "success"
        )

        return redirect(url_for("danh_sach_chuyen_xe"))

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Lỗi MySQL khi ẩn chuyến xe")

        flash("Không thể ẩn chuyến xe!", "danger")

        return redirect(url_for("danh_sach_chuyen_xe"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.9.3 - KHÔI PHỤC CHUYẾN XE ĐÃ ẨN
# ==========================================================

@app.route("/chuyen-xe/khoi-phuc/<int:ma_chuyen>", methods=["POST"])
def khoi_phuc_chuyen_xe(ma_chuyen):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiểm tra chuyến xe
        cursor.execute("""
            SELECT
                MaChuyen,
                DaAn
            FROM CHUYEN_XE
            WHERE MaChuyen = %s
            FOR UPDATE
        """, (ma_chuyen,))

        chuyen = cursor.fetchone()

        if chuyen is None:

            flash("Không tìm thấy chuyến xe!", "danger")

            return redirect(
                url_for("danh_sach_chuyen_duoc_an")
            )

        # 2. Kiểm tra trạng thái ẩn
        if not chuyen["DaAn"]:

            flash("Chuyến xe này chưa bị ẩn!", "warning")

            return redirect(
                url_for("danh_sach_chuyen_duoc_an")
            )

        # 3. Khôi phục
        cursor.execute("""
            UPDATE CHUYEN_XE
            SET
                DaAn = FALSE,
                NgayAn = NULL
            WHERE MaChuyen = %s
        """, (ma_chuyen,))

        connection.commit()

        flash(
            f"Đã khôi phục chuyến xe #{ma_chuyen} thành công!",
            "success"
        )

        return redirect(
            url_for("danh_sach_chuyen_duoc_an")
        )

    except mysql.connector.Error:

        if connection is not None:
            connection.rollback()

        app.logger.exception("Lỗi MySQL khi khôi phục chuyến xe")

        flash("Không thể khôi phục chuyến xe!", "danger")

        return redirect(
            url_for("danh_sach_chuyen_duoc_an")
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 10.9.4 - DANH SÁCH CHUYẾN XE ĐÃ ẨN
# ==========================================================

@app.route("/chuyen-xe/da-an", methods=["GET"])
def danh_sach_chuyen_duoc_an():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                cx.MaChuyen,
                cx.MaXe,
                cx.MaTaiXe,
                cx.MaPhuXe,
                cx.MaTuyenDuong,
                cx.SoKhach,
                cx.ThoiGianKhoiHanh,
                cx.SoKmThucTe,
                cx.GiaVe,
                cx.TrangThai,
                cx.DaAn,
                cx.NgayAn,

                x.BienSo,

                tx.HoTen AS TenTaiXe,
                px.HoTen AS TenPhuXe,

                td.TenTuyenDuong,
                td.DiemDi,
                td.DiemDen

            FROM CHUYEN_XE cx

            LEFT JOIN XE x
                ON cx.MaXe = x.MaXe

            LEFT JOIN TAI_XE tx
                ON cx.MaTaiXe = tx.MaTaiXe

            LEFT JOIN TAI_XE px
                ON cx.MaPhuXe = px.MaTaiXe

            LEFT JOIN TUYEN_DUONG td
                ON cx.MaTuyenDuong = td.MaTuyenDuong

            WHERE cx.DaAn = TRUE

            ORDER BY cx.NgayAn DESC, cx.MaChuyen DESC
        """)

        danh_sach = cursor.fetchall()

        return render_template(
            "chuyen_xe/danh_sach.html",
            danh_sach=danh_sach,
            che_do_danh_sach="da_an",
            danh_sach_tuyen=[],
            ma_chuyen="",
            bien_so="",
            trang_thai="",
            ma_tuyen=""
        )

    except mysql.connector.Error:

        app.logger.exception(
            "Lỗi MySQL khi lấy danh sách chuyến xe đã ẩn"
        )

        flash(
            "Không thể tải danh sách chuyến xe đã ẩn!",
            "danger"
        )

        return redirect(
            url_for("danh_sach_chuyen_xe")
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# ==========================================================
# 11.1 - DANH SÁCH LỊCH BẢO DƯỠNG XE
# ==========================================================

@app.route("/bao-duong", methods=["GET"])
def danh_sach_bao_duong():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Lấy lịch bảo dưỡng từ view đã có trong MySQL
        cursor.execute("""
            SELECT
                v.MaXe,
                v.BienSo,
                v.LanBaoDuongCuoi,
                v.TongKmTrongSo,
                v.SoNgayGiam,
                v.NgayBaoDuongTiepTheo,
                v.TrangThaiBaoDuong,

                (
                    SELECT bd.MaBaoDuong
                    FROM BAO_DUONG bd
                    WHERE bd.MaXe = v.MaXe
                        AND bd.TrangThai = 'Hoàn thành'
                    ORDER BY
                        bd.ThoiGianBaoDuong DESC,
                        bd.MaBaoDuong DESC
                    LIMIT 1
                ) AS MaBaoDuongGanNhat

            FROM vw_lich_bao_duong v

            ORDER BY
                CASE
                    WHEN v.TrangThaiBaoDuong = 'Quá hạn' THEN 1
                    WHEN v.TrangThaiBaoDuong = 'Chưa có lịch sử bảo dưỡng' THEN 2
                    ELSE 3
                END,
                v.NgayBaoDuongTiepTheo ASC
        """)

        danh_sach = cursor.fetchall()

        # Thống kê số xe quá hạn
        so_xe_qua_han = sum(
            1 for xe in danh_sach
            if xe["TrangThaiBaoDuong"] == "Quá hạn"
        )

        return render_template(
            "bao_duong/danh_sach.html",
            danh_sach=danh_sach,
            so_xe_qua_han=so_xe_qua_han
        )

    except Exception as e:
        flash(f"Lỗi tải lịch bảo dưỡng: {e}", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 11.2 - DANH SÁCH XE QUÁ HẠN BẢO DƯỠNG
# ==========================================================

@app.route("/bao-duong/qua-han", methods=["GET"])
def danh_sach_xe_qua_han():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                MaXe,
                BienSo,
                LanBaoDuongCuoi,
                TongKmTrongSo,
                SoNgayGiam,
                NgayBaoDuongTiepTheo,
                TrangThaiBaoDuong
            FROM vw_lich_bao_duong
            WHERE TrangThaiBaoDuong = 'Quá hạn'
            ORDER BY NgayBaoDuongTiepTheo ASC
        """)

        danh_sach = cursor.fetchall()

        return render_template(
            "bao_duong/danh_sach.html",
            danh_sach=danh_sach,
            so_xe_qua_han=len(danh_sach),
            che_do_danh_sach="qua_han"
        )

    except Exception as e:
        flash(f"Lỗi tải danh sách xe quá hạn: {e}", "danger")
        return redirect(url_for("danh_sach_bao_duong"))

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 11.3 - THÊM PHIẾU BẢO DƯỠNG XE
# ==========================================================

@app.route("/bao-duong/them", methods=["GET", "POST"])
def them_bao_duong():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Lấy danh sách xe để hiển thị trong form
        cursor.execute("""
            SELECT MaXe, BienSo
            FROM XE
            ORDER BY BienSo ASC
        """)

        danh_sach_xe = cursor.fetchall()

        # 2. Hiển thị form khi truy cập bằng GET
        if request.method == "GET":

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong={},
                che_do="them"
            )

        # 3. Lấy dữ liệu người dùng nhập
        ma_xe = request.form.get("ma_xe", "").strip()
        thoi_gian = request.form.get("thoi_gian", "").strip()
        noi_dung = request.form.get("noi_dung", "").strip()
        chi_phi = request.form.get("chi_phi", "").strip()
        trang_thai = request.form.get("trang_thai", "").strip()

        # Giữ lại dữ liệu nếu nhập sai
        bao_duong = {
            "MaXe": ma_xe,
            "ThoiGianBaoDuong": thoi_gian,
            "NoiDung": noi_dung,
            "ChiPhi": chi_phi,
            "TrangThai": trang_thai
        }

        # 4. Kiểm tra dữ liệu bắt buộc
        if not all([
            ma_xe,
            thoi_gian,
            noi_dung,
            chi_phi,
            trang_thai
        ]):

            flash(
                "Vui lòng nhập đầy đủ thông tin bảo dưỡng!",
                "danger"
            )

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="them"
            )

        # 5. Kiểm tra dữ liệu hợp lệ
        from datetime import datetime
        from decimal import Decimal, InvalidOperation

        try:
            ma_xe = int(ma_xe)
            chi_phi = Decimal(chi_phi)
            ngay_bao_duong = datetime.strptime(
                thoi_gian,
                "%Y-%m-%dT%H:%M"
            )

        except (ValueError, InvalidOperation):

            flash(
                "Mã xe, ngày giờ hoặc chi phí không hợp lệ!",
                "danger"
            )

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="them"
            )

        if chi_phi < 0:

            flash(
                "Chi phí bảo dưỡng không được âm!",
                "danger"
            )

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="them"
            )

        if len(noi_dung) > 200:

            flash(
                "Nội dung bảo dưỡng không được vượt quá 200 ký tự!",
                "danger"
            )

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="them"
            )

        if trang_thai not in [
            "Đang chờ",
            "Đang bảo dưỡng",
            "Hoàn thành"
        ]:

            flash(
                "Trạng thái bảo dưỡng không hợp lệ!",
                "danger"
            )

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="them"
            )

        # 6. Kiểm tra xe có tồn tại
        cursor.execute("""
            SELECT MaXe
            FROM XE
            WHERE MaXe = %s
        """, (ma_xe,))

        if cursor.fetchone() is None:

            flash("Xe được chọn không tồn tại!", "danger")

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="them"
            )

        # 7. Thêm phiếu bảo dưỡng
        cursor.execute("""
            INSERT INTO BAO_DUONG (
                MaXe,
                ThoiGianBaoDuong,
                NoiDung,
                ChiPhi,
                TrangThai
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ma_xe,
            ngay_bao_duong,
            noi_dung,
            chi_phi,
            trang_thai
        ))

        connection.commit()

        flash(
            "Thêm phiếu bảo dưỡng thành công!",
            "success"
        )

        return redirect(url_for("danh_sach_bao_duong"))

    except Exception as e:

        if connection is not None:
            connection.rollback()

        flash(
            f"Không thể thêm phiếu bảo dưỡng: {e}",
            "danger"
        )

        return redirect(url_for("danh_sach_bao_duong"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 11.4 - DANH SÁCH LỊCH SỬ BẢO DƯỠNG XE
# ==========================================================

@app.route("/bao-duong/lich-su", methods=["GET"])
def lich_su_bao_duong():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Lấy điều kiện tìm kiếm
        bien_so = request.args.get("bien_so", "").strip()
        trang_thai = request.args.get("trang_thai", "").strip()
        ma_xe = request.args.get("ma_xe", "").strip()

        # 2. Truy vấn danh sách bảo dưỡng
        sql = """
            SELECT
                bd.MaBaoDuong,
                bd.MaXe,
                x.BienSo,
                bd.ThoiGianBaoDuong,
                bd.NoiDung,
                bd.ChiPhi,
                bd.TrangThai
            FROM BAO_DUONG bd
            JOIN XE x ON bd.MaXe = x.MaXe
            WHERE 1 = 1
        """

        params = []

        # Tìm kiếm theo biển số
        if bien_so:
            sql += " AND x.BienSo LIKE %s"
            params.append(f"%{bien_so}%")

        # Lọc trạng thái
        if trang_thai:
            if trang_thai not in [
                "Đang chờ",
                "Đang bảo dưỡng",
                "Hoàn thành"
            ]:
                flash("Trạng thái lọc không hợp lệ!", "warning")
                return redirect(url_for("lich_su_bao_duong"))

            sql += " AND bd.TrangThai = %s"
            params.append(trang_thai)

        # Lọc lịch sử của một xe cụ thể
        if ma_xe:
            try:
                ma_xe = int(ma_xe)

                if ma_xe <= 0:
                    raise ValueError

            except ValueError:
                flash("Mã xe không hợp lệ!", "warning")
                return redirect(url_for("lich_su_bao_duong"))

            sql += " AND bd.MaXe = %s"
            params.append(ma_xe)

        # Sắp xếp mới nhất trước
        sql += """
            ORDER BY
                bd.ThoiGianBaoDuong DESC,
                bd.MaBaoDuong DESC
        """

        cursor.execute(sql, tuple(params))
        danh_sach = cursor.fetchall()

        # 3. Thống kê
        tong_phieu = len(danh_sach)

        tong_chi_phi = sum(
            (bd["ChiPhi"] for bd in danh_sach),
            0
        )

        so_phieu_hoan_thanh = sum(
            1 for bd in danh_sach
            if bd["TrangThai"] == "Hoàn thành"
        )

        return render_template(
            "bao_duong/lich_su.html",
            danh_sach=danh_sach,
            bien_so=bien_so,
            trang_thai=trang_thai,
            ma_xe=ma_xe,
            tong_phieu=tong_phieu,
            tong_chi_phi=tong_chi_phi,
            so_phieu_hoan_thanh=so_phieu_hoan_thanh
        )

    except Exception as e:

        flash(
            f"Lỗi tải lịch sử bảo dưỡng: {e}",
            "danger"
        )

        return redirect(url_for("danh_sach_bao_duong"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 11.5 - SỬA PHIẾU BẢO DƯỠNG XE
# ==========================================================

@app.route("/bao-duong/sua/<int:ma_bao_duong>", methods=["GET", "POST"])
def sua_bao_duong(ma_bao_duong):

    from datetime import datetime
    from decimal import Decimal, InvalidOperation

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiểm tra phiếu bảo dưỡng có tồn tại không
        cursor.execute("""
            SELECT
                MaBaoDuong,
                MaXe,
                ThoiGianBaoDuong,
                NoiDung,
                ChiPhi,
                TrangThai
            FROM BAO_DUONG
            WHERE MaBaoDuong = %s
        """, (ma_bao_duong,))

        bao_duong = cursor.fetchone()

        if bao_duong is None:
            flash("Không tìm thấy phiếu bảo dưỡng cần sửa!", "danger")
            return redirect(url_for("lich_su_bao_duong"))

        # 2. Lấy danh sách xe
        cursor.execute("""
            SELECT MaXe, BienSo
            FROM XE
            ORDER BY BienSo ASC
        """)

        danh_sach_xe = cursor.fetchall()

        # 3. Hiển thị form khi GET
        if request.method == "GET":

            # Chuyển datetime thành chuỗi phù hợp datetime-local
            if bao_duong["ThoiGianBaoDuong"]:
                bao_duong["ThoiGianBaoDuong"] = (
                    bao_duong["ThoiGianBaoDuong"].strftime(
                        "%Y-%m-%dT%H:%M"
                    )
                )

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="sua"
            )

        # 4. Nhận dữ liệu POST
        ma_xe = request.form.get("ma_xe", "").strip()
        thoi_gian = request.form.get("thoi_gian", "").strip()
        noi_dung = request.form.get("noi_dung", "").strip()
        chi_phi = request.form.get("chi_phi", "").strip()
        trang_thai = request.form.get("trang_thai", "").strip()

        # Giữ lại dữ liệu khi nhập sai
        bao_duong = {
            "MaBaoDuong": ma_bao_duong,
            "MaXe": ma_xe,
            "ThoiGianBaoDuong": thoi_gian,
            "NoiDung": noi_dung,
            "ChiPhi": chi_phi,
            "TrangThai": trang_thai
        }

        def hien_thi_lai_form(thong_bao):
            flash(thong_bao, "danger")

            return render_template(
                "bao_duong/form.html",
                danh_sach_xe=danh_sach_xe,
                bao_duong=bao_duong,
                che_do="sua"
            )

        # 5. Kiểm tra trường bắt buộc
        if not all([
            ma_xe,
            thoi_gian,
            noi_dung,
            chi_phi,
            trang_thai
        ]):
            return hien_thi_lai_form(
                "Vui lòng nhập đầy đủ thông tin bảo dưỡng!"
            )

        # 6. Kiểm tra kiểu dữ liệu
        try:
            ma_xe = int(ma_xe)

            ngay_bao_duong = datetime.strptime(
                thoi_gian,
                "%Y-%m-%dT%H:%M"
            )

            chi_phi = Decimal(chi_phi)

        except (ValueError, InvalidOperation):
            return hien_thi_lai_form(
                "Mã xe, ngày giờ hoặc chi phí không hợp lệ!"
            )

        # 7. Kiểm tra các điều kiện
        if ma_xe <= 0:
            return hien_thi_lai_form(
                "Mã xe không hợp lệ!"
            )

        if not chi_phi.is_finite() or chi_phi < 0:
            return hien_thi_lai_form(
                "Chi phí bảo dưỡng phải là số không âm hợp lệ!"
            )

        if len(noi_dung) > 200:
            return hien_thi_lai_form(
                "Nội dung không được vượt quá 200 ký tự!"
            )

        if trang_thai not in [
            "Đang chờ",
            "Đang bảo dưỡng",
            "Hoàn thành"
        ]:
            return hien_thi_lai_form(
                "Trạng thái bảo dưỡng không hợp lệ!"
            )

        # 8. Kiểm tra xe tồn tại
        cursor.execute("""
            SELECT MaXe
            FROM XE
            WHERE MaXe = %s
        """, (ma_xe,))

        if cursor.fetchone() is None:
            return hien_thi_lai_form(
                "Xe được chọn không tồn tại!"
            )

        # 9. Cập nhật phiếu bảo dưỡng
        cursor.execute("""
            UPDATE BAO_DUONG
            SET
                MaXe = %s,
                ThoiGianBaoDuong = %s,
                NoiDung = %s,
                ChiPhi = %s,
                TrangThai = %s
            WHERE MaBaoDuong = %s
        """, (
            ma_xe,
            ngay_bao_duong,
            noi_dung,
            chi_phi,
            trang_thai,
            ma_bao_duong
        ))

        connection.commit()

        flash(
            f"Cập nhật phiếu bảo dưỡng #{ma_bao_duong} thành công!",
            "success"
        )

        return redirect(url_for("lich_su_bao_duong"))

    except Exception as e:

        if connection is not None:
            connection.rollback()

        flash(
            f"Không thể sửa phiếu bảo dưỡng: {e}",
            "danger"
        )

        return redirect(url_for("lich_su_bao_duong"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 11.6 - XÓA PHIẾU BẢO DƯỠNG XE
# ==========================================================

@app.route("/bao-duong/xoa/<int:ma_bao_duong>", methods=["POST"])
def xoa_bao_duong(ma_bao_duong):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Kiểm tra phiếu bảo dưỡng có tồn tại không
        cursor.execute("""
            SELECT
                bd.MaBaoDuong,
                bd.MaXe,
                bd.TrangThai,
                x.BienSo
            FROM BAO_DUONG bd
            JOIN XE x ON bd.MaXe = x.MaXe
            WHERE bd.MaBaoDuong = %s
            FOR UPDATE
        """, (ma_bao_duong,))

        bao_duong = cursor.fetchone()

        if bao_duong is None:

            flash(
                "Không tìm thấy phiếu bảo dưỡng cần xóa!",
                "danger"
            )

            return redirect(url_for("lich_su_bao_duong"))

        # 2. Lưu thông tin để hiển thị thông báo
        bien_so = bao_duong["BienSo"]
        trang_thai = bao_duong["TrangThai"]

        # 3. Xóa phiếu bảo dưỡng
        cursor.execute("""
            DELETE FROM BAO_DUONG
            WHERE MaBaoDuong = %s
        """, (ma_bao_duong,))

        connection.commit()

        # 4. Thông báo kết quả
        if trang_thai == "Hoàn thành":

            flash(
                f"Đã xóa phiếu bảo dưỡng #{ma_bao_duong} "
                f"của xe {bien_so}. "
                "Lịch bảo dưỡng của xe có thể đã thay đổi!",
                "warning"
            )

        else:

            flash(
                f"Đã xóa phiếu bảo dưỡng #{ma_bao_duong} "
                f"của xe {bien_so} thành công!",
                "success"
            )

        return redirect(url_for("lich_su_bao_duong"))

    except Exception as e:

        if connection is not None:
            connection.rollback()

        flash(
            f"Không thể xóa phiếu bảo dưỡng: {e}",
            "danger"
        )

        return redirect(url_for("lich_su_bao_duong"))

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 12.2 - BẢNG LƯƠNG TÀI XẾ VÀ PHỤ XE
# ==========================================================

@app.route("/bang-luong", methods=["GET"])
def bang_luong():

    connection = None
    cursor = None

    try:
        from datetime import datetime, date

        # Lấy tháng/năm từ bộ lọc
        now = datetime.now()

        thang = request.args.get("thang", default=now.month, type=int)
        nam = request.args.get("nam", default=now.year, type=int)

        # Kiểm tra dữ liệu đầu vào
        if not 1 <= thang <= 12:
            flash("Tháng không hợp lệ!", "danger")
            return redirect(url_for("bang_luong"))

        if not 2000 <= nam <= 2100:
            flash("Năm không hợp lệ!", "danger")
            return redirect(url_for("bang_luong"))

        ngay_dau=date(nam,thang,1)
        ngay_cuoi=date(nam+1,1,1) if thang == 12 else date(nam,thang+1,1)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                tx.MaTaiXe,
                tx.HoTen,

                COUNT(
                    CASE
                        WHEN cv.VaiTro = 'TaiXe' THEN 1
                    END
                ) AS SoChuyenLai,

                COUNT(
                    CASE
                        WHEN cv.VaiTro = 'PhuXe' THEN 1
                    END
                ) AS SoChuyenPhu,

                COUNT(cv.MaChuyen) AS TongSoChuyen,

                COALESCE(SUM(cv.TienLuong), 0) AS TongLuong

            FROM TAI_XE tx

            LEFT JOIN (

                -- Lương khi làm tài xế
                SELECT
                    cx.MaChuyen,
                    cx.MaTaiXe AS MaNhanVien,
                    'TaiXe' AS VaiTro,

                    CASE td.DoPhucTap
                        WHEN 1 THEN 400000
                        WHEN 2 THEN 600000
                        WHEN 3 THEN 800000
                        ELSE 0
                    END AS TienLuong

                FROM CHUYEN_XE cx

                JOIN TUYEN_DUONG td
                    ON cx.MaTuyenDuong = td.MaTuyenDuong

                WHERE cx.TrangThai = 'Đã hoàn thành'
                  AND cx.ThoiGianKhoiHanh >= %s
                  AND cx.ThoiGianKhoiHanh < LEAST(%s, NOW())

                UNION ALL

                -- Lương khi làm phụ xe
                SELECT
                    cx.MaChuyen,
                    cx.MaPhuXe AS MaNhanVien,
                    'PhuXe' AS VaiTro,

                    CASE td.DoPhucTap
                        WHEN 1 THEN 200000
                        WHEN 2 THEN 300000
                        WHEN 3 THEN 400000
                        ELSE 0
                    END AS TienLuong

                FROM CHUYEN_XE cx

                JOIN TUYEN_DUONG td
                    ON cx.MaTuyenDuong = td.MaTuyenDuong

                WHERE cx.TrangThai = 'Đã hoàn thành'
                  AND cx.ThoiGianKhoiHanh >= %s
                  AND cx.ThoiGianKhoiHanh < LEAST(%s, NOW())

            ) cv
                ON tx.MaTaiXe = cv.MaNhanVien

            GROUP BY
                tx.MaTaiXe,
                tx.HoTen

            ORDER BY
                TongLuong DESC,
                tx.MaTaiXe ASC
        """

        cursor.execute(sql, (ngay_dau, ngay_cuoi, ngay_dau, ngay_cuoi))

        danh_sach_luong = cursor.fetchall()

        # Tổng hợp thống kê
        tong_nhan_vien = sum(
            1 for nv in danh_sach_luong
            if nv["TongSoChuyen"] > 0
        )

        tong_quy_luong = sum(
            nv["TongLuong"] for nv in danh_sach_luong
        )

        # Mỗi chuyến hoàn thành có 1 tài xế
        tong_chuyen = sum(
            nv["SoChuyenLai"] for nv in danh_sach_luong
        )

        return render_template(
            "bang_luong/danh_sach.html",
            danh_sach_luong=danh_sach_luong,
            thang=thang,
            nam=nam,
            tong_nhan_vien=tong_nhan_vien,
            tong_quy_luong=tong_quy_luong,
            tong_chuyen=tong_chuyen
        )

    except Exception as e:
        flash(f"Lỗi khi tải bảng lương: {e}", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==========================================================
# 13 - THỐNG KÊ DOANH THU THEO XE
# ==========================================================

@app.route("/doanh-thu", methods=["GET"])
def doanh_thu():

    connection = None
    cursor = None

    try:
        from datetime import date, timedelta

        # Mặc định thống kê 30 ngày gần nhất
        hom_nay = date.today()
        ngay_bat_dau_mac_dinh = hom_nay - timedelta(days=29)

        tu_ngay = request.args.get(
            "tu_ngay",
            default=ngay_bat_dau_mac_dinh.isoformat()
        )

        den_ngay = request.args.get(
            "den_ngay",
            default=hom_nay.isoformat()
        )

        # ==================================================
        # KIỂM TRA NGÀY
        # ==================================================

        try:
            ngay_bat_dau = date.fromisoformat(tu_ngay)
            ngay_ket_thuc = date.fromisoformat(den_ngay)

        except (ValueError, TypeError):
            flash("Ngày không hợp lệ!", "danger")
            return redirect(url_for("doanh_thu"))

        if ngay_bat_dau > ngay_ket_thuc:
            flash(
                "Ngày bắt đầu không được lớn hơn ngày kết thúc!",
                "danger"
            )
            return redirect(url_for("doanh_thu"))

        # Dùng khoảng [từ ngày, ngày sau ngày kết thúc)
        # để bao gồm toàn bộ ngày kết thúc.
        den_ngay_tiep_theo = ngay_ket_thuc + timedelta(days=1)

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # ==================================================
        # DOANH THU TỪNG XE
        # ==================================================

        sql = """
            SELECT
                x.MaXe,
                x.BienSo,
                x.HangSanXuat,
                x.DoiXe,

                COUNT(cx.MaChuyen) AS SoChuyenHoanThanh,

                COALESCE(
                    SUM(cx.SoKhach),
                    0
                ) AS TongHanhKhach,

                COALESCE(
                    SUM(cx.SoKhach * cx.GiaVe),
                    0
                ) AS TongDoanhThu

            FROM XE x

            LEFT JOIN CHUYEN_XE cx
                ON x.MaXe = cx.MaXe

                AND cx.TrangThai = 'Đã hoàn thành'

                AND cx.ThoiGianKhoiHanh >= %s
                AND cx.ThoiGianKhoiHanh < %s

            GROUP BY
                x.MaXe,
                x.BienSo,
                x.HangSanXuat,
                x.DoiXe

            ORDER BY
                TongDoanhThu DESC,
                x.MaXe ASC
        """

        cursor.execute(
            sql,
            (
                ngay_bat_dau,
                den_ngay_tiep_theo
            )
        )

        danh_sach_doanh_thu = cursor.fetchall()

        # ==================================================
        # TỔNG HỢP THỐNG KÊ
        # ==================================================

        tong_chuyen = sum(
            xe["SoChuyenHoanThanh"]
            for xe in danh_sach_doanh_thu
        )

        tong_hanh_khach = sum(
            xe["TongHanhKhach"]
            for xe in danh_sach_doanh_thu
        )

        tong_doanh_thu = sum(
            xe["TongDoanhThu"]
            for xe in danh_sach_doanh_thu
        )

        so_xe_co_doanh_thu = sum(
            1
            for xe in danh_sach_doanh_thu
            if xe["SoChuyenHoanThanh"] > 0
        )

        return render_template(
            "doanh_thu/danh_sach.html",
            danh_sach_doanh_thu=danh_sach_doanh_thu,
            tu_ngay=tu_ngay,
            den_ngay=den_ngay,
            tong_chuyen=tong_chuyen,
            tong_hanh_khach=tong_hanh_khach,
            tong_doanh_thu=tong_doanh_thu,
            so_xe_co_doanh_thu=so_xe_co_doanh_thu
        )

    except OverflowError:
        flash("Khoảng ngày vượt quá giới hạn cho phép!", "danger")
        return redirect(url_for("doanh_thu"))

    except Exception as e:
        flash(
            f"Lỗi khi thống kê doanh thu: {e}",
            "danger"
        )
        return redirect(url_for("dashboard"))

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

print("\n========== DANH SACH ROUTE FLASK ==========")

for rule in app.url_map.iter_rules():
    print(rule.endpoint, "=>", rule.rule)

print("==========================================\n")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)