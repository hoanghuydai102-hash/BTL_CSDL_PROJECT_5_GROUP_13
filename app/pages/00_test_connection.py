import os
from getpass import getpass

import mysql.connector
from mysql.connector import Error


def main():
    print("===== KIEM TRA KET NOI MYSQL =====")

    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    user = input("MySQL username [root]: ").strip() or "root"
    password = getpass("MySQL password: ")

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="QL_VAN_TAI",
            connection_timeout=10,
        )

        print("\n[OK] Ket noi MySQL thanh cong!")

        cursor = connection.cursor()

        cursor.execute("SELECT DATABASE(), VERSION()")
        database_name, mysql_version = cursor.fetchone()

        print(f"Database: {database_name}")
        print(f"MySQL version: {mysql_version}")

        print("\n===== KIEM TRA DU LIEU =====")

        tables = [
            "XE",
            "TAI_XE",
            "TUYEN_DUONG",
            "CHUYEN_XE",
            "BAO_DUONG",
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} ban ghi")

        print("\n[OK] Hoan thanh kiem tra!")

    except Error as err:
        print(f"\n[ERROR] Ket noi hoac truy van that bai: {err}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
            print("\nDa dong ket noi MySQL.")


if __name__ == "__main__":
    main()