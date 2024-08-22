from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app
from app.database import Base, get_db

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


def test_create_metadata():
    response = client.post(
        "/metadata/",
        json={
            "reference_genome_path": "/path/to/genome",
            "reference_transcriptome_path": "/path/to/transcriptome",
            "known_variants_path": "/path/to/variants"})
    assert response.status_code == 200
    assert response.json()["reference_genome_path"] == "/path/to/genome"


def test_read_metadata():
    client.post(
        "/metadata/",
        json={
            "reference_genome_path": "/path/to/genome",
            "reference_transcriptome_path": "/path/to/transcriptome",
            "known_variants_path": "/path/to/variants"})
    response = client.get("/metadata/1")
    assert response.status_code == 200
    assert response.json()["reference_genome_path"] == "/path/to/genome"


def test_update_metadata():
    client.post(
        "/metadata/",
        json={
            "reference_genome_path": "/path/to/genome",
            "reference_transcriptome_path": "/path/to/transcriptome",
            "known_variants_path": "/path/to/variants"})
    response = client.put(
        "/metadata/1",
        json={
            "reference_genome_path": "/new/path/to/genome",
            "reference_transcriptome_path": "/new/path/to/transcriptome",
            "known_variants_path": "/new/path/to/variants"})
    assert response.status_code == 200
    assert response.json()["reference_genome_path"] == "/new/path/to/genome"


def test_delete_metadata():
    client.post(
        "/metadata/",
        json={
            "reference_genome_path": "/path/to/genome",
            "reference_transcriptome_path": "/path/to/transcriptome",
            "known_variants_path": "/path/to/variants"})
    response = client.delete("/metadata/1")
    assert response.status_code == 200
    get_response = client.get("/metadata/1")
    assert get_response.status_code == 404
