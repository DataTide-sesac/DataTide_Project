import sqlite3
import os

db_path = "C:\\datatide_workspaceN\\test.db"

# Ensure the directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create alembic_version table and insert a dummy revision
cursor.execute("""
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
)
""")
cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?)", ("dummy_revision",))
conn.commit()
conn.close()

print(f"Dummy test.db created at {db_path} with alembic_version table and 'dummy_revision'.")
