import sqlite3
import pprint

def list_sqlite_db_contents(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [info[1] for info in cursor.fetchall()]
        print("Columns:", columns)

        # Get all data
        # cursor.execute(f"SELECT * FROM {table_name};")
        # rows = cursor.fetchall()
        # for row in rows:
        #     print(row)

    conn.close()

if __name__ == "__main__":
    db_file = "dhen.db"  # Replace with your SQLite file path
    list_sqlite_db_contents(db_file)