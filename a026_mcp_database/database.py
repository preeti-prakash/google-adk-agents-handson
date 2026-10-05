import sqlite3
from pathlib import Path


# Keep employees.db next to this file, whichever folder the server is run from
DB_NAME = Path(__file__).parent / "employees.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Insert demo data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM employees")

    count = cursor.fetchone()[0]

    if count == 0:

        employees = [
            (101, "Preeti", "Cloud Engineering", "Cloud Engineer"),
            (102, "John", "Data Engineering", "Data Engineer"),
            (103, "Sarah", "AI Engineering", "AI Engineer")
        ]

        cursor.executemany(
            """
            INSERT INTO employees
            (id, name, department, role)
            VALUES (?, ?, ?, ?)
            """,
            employees
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized.")
