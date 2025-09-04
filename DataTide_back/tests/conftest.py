import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Assuming the main app and Base are in these locations
from DataTide_back.main import app
from DataTide_back.core.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite
    poolclass=StaticPool, # Use a static pool for in-memory DB
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Pytest fixture to set up the database for a test session
@pytest.fixture(scope="function")
def db_session():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the tables after the test is done
    Base.metadata.drop_all(bind=engine)


# Pytest fixture to provide a TestClient
@pytest.fixture(scope="function")
def client(db_session):
    """
    A TestClient that uses the db_session fixture to automatically
    create and drop the database tables for each test.
    """
    with TestClient(app) as c:
        yield c
