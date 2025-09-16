import pytest
from fastapi.testclient import TestClient

# Import the new db_session context manager
from DataTide_back.db.session import db_session
from DataTide_back.main import app # Import the main FastAPI app

# Define SQL statements for creating and dropping tables
# These should match your actual database schema
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS item (
    item_pk INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS location (
    local_pk INT AUTO_INCREMENT PRIMARY KEY,
    local_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS item_retail (
    retail_pk INT AUTO_INCREMENT PRIMARY KEY,
    item_pk INT NOT NULL,
    production INT,
    inbound INT,
    sales INT,
    month_date DATE,
    FOREIGN KEY (item_pk) REFERENCES item(item_pk)
);

CREATE TABLE IF NOT EXISTS ground_weather (
    ground_pk INT AUTO_INCREMENT PRIMARY KEY,
    month_date DATE NOT NULL,
    temperature FLOAT,
    rain FLOAT
);

CREATE TABLE IF NOT EXISTS sea_weather (
    sea_pk INT AUTO_INCREMENT PRIMARY KEY,
    local_pk INT NOT NULL,
    month_date DATE NOT NULL,
    temperature FLOAT,
    wind FLOAT,
    salinity FLOAT,
    wave_height FLOAT,
    wave_period FLOAT,
    wave_speed FLOAT,
    rain FLOAT,
    snow FLOAT,
    FOREIGN KEY (local_pk) REFERENCES location(local_pk)
);
"""

DROP_TABLE_SQL = """
DROP TABLE IF EXISTS sea_weather;
DROP TABLE IF EXISTS ground_weather;
DROP TABLE IF EXISTS item_retail;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS location;
"""

import pytest
from fastapi.testclient import TestClient

# Import the new db_session context manager
from DataTide_back.db.session import db_session
from DataTide_back.main import app # Import the main FastAPI app

# Define SQL statements for creating and dropping tables
# These should match your actual database schema
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS item (
    item_pk INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS location (
    local_pk INT AUTO_INCREMENT PRIMARY KEY,
    local_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS item_retail (
    retail_pk INT AUTO_INCREMENT PRIMARY KEY,
    item_pk INT NOT NULL,
    production INT,
    inbound INT,
    sales INT,
    month_date DATE,
    FOREIGN KEY (item_pk) REFERENCES item(item_pk)
);

CREATE TABLE IF NOT EXISTS ground_weather (
    ground_pk INT AUTO_INCREMENT PRIMARY KEY,
    month_date DATE NOT NULL,
    temperature FLOAT,
    rain FLOAT
);

CREATE TABLE IF NOT EXISTS sea_weather (
    sea_pk INT AUTO_INCREMENT PRIMARY KEY,
    local_pk INT NOT NULL,
    month_date DATE NOT NULL,
    temperature FLOAT,
    wind FLOAT,
    salinity FLOAT,
    wave_height FLOAT,
    wave_period FLOAT,
    wave_speed FLOAT,
    rain FLOAT,
    snow FLOAT,
    FOREIGN KEY (local_pk) REFERENCES location(local_pk)
);
"""

DROP_TABLE_SQL = """
DROP TABLE IF EXISTS sea_weather;
DROP TABLE IF EXISTS ground_weather;
DROP TABLE IF EXISTS item_retail;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS location;
"""

@pytest.fixture(scope="session") # Change scope to session for initial setup
def setup_test_db_schema():
    """
    Fixture to set up and tear down the test database for each test function.
    It uses the actual database connection configured via .env.
    Ensure your .env points to a dedicated test database!
    """
    with db_session() as cursor:
        # Drop tables in reverse order to handle foreign key constraints
        for stmt in DROP_TABLE_SQL.split(';'):
            if stmt.strip():
                cursor.execute(stmt)
        
        # Create tables
        for stmt in CREATE_TABLE_SQL.split(';'):
            if stmt.strip():
                cursor.execute(stmt)
    
    yield # Run the test function

    with db_session() as cursor:
        # Drop tables again after the test session is done
        for stmt in DROP_TABLE_SQL.split(';'):
            if stmt.strip():
                cursor.execute(stmt)

@pytest.fixture(scope="function")
def client(setup_test_db_schema):
    """
    A TestClient that ensures the test database is set up for each test.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def client(setup_test_db):
    """
    A TestClient that ensures the test database is set up for each test.
    """
    with TestClient(app) as c:
        yield c
