from sqlalchemy import create_engine, text
import os

# Assuming this script is in DataTide_back/
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test.db'))
DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL)

print(f"Connecting to database: {DB_URL}")

try:
    with engine.connect() as connection:
        # Get table creation SQL
        result = connection.execute(text("SELECT sql FROM sqlite_master WHERE name='item_retail';"))
        sql_create_table = result.scalar_one_or_none()

        if sql_create_table:
            print("\n--- item_retail table DDL ---")
            print(sql_create_table)
        else:
            print("item_retail table not found in database.")

        # Get table info (columns)
        result = connection.execute(text("PRAGMA table_info(item_retail);"))
        print("\n--- item_retail table PRAGMA info ---")
        for row in result:
            print(row)

except Exception as e:
    print(f"Error inspecting database: {e}")

print("\nDatabase inspection complete.")
