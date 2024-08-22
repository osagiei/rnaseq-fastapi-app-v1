from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app
from app.database import Base, get_db
from app.models import Sample

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield
    Base.metadata.drop_all(bind=engine)


def test_create_sample():
    response = client.post(
        "/samples/",
        json={
            "sample_id": "sample123",
            "sample_description": "Test Sample",
            "sample_type": "blood",
            "sample_source": "human"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "sample123"
    assert data["sample_description"] == "Test Sample"
