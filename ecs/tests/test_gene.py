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


def test_create_gene():
    response = client.post(
        "/genes/",
        json={
            "coord_id": "chr1:1000-5000:+",
            "chromosome": "chr1",
            "chrom_start": 1000,
            "chrom_end": 5000,
            "strand": "+",
            "ensembl_id": "ENSG000001",
            "gene_name": "GeneA",
            "biotype": "protein_coding",
            "description": "Test gene description"
        }
    )
    assert response.status_code == 200
    assert response.json()["coord_id"] == "chr1:1000-5000:+"
    assert response.json()["gene_name"] == "GeneA"


def test_read_gene():
    client.post(
        "/genes/",
        json={
            "coord_id": "chr1:1000-5000:+",
            "chromosome": "chr1",
            "chrom_start": 1000,
            "chrom_end": 5000,
            "strand": "+",
            "ensembl_id": "ENSG000001",
            "gene_name": "GeneA",
            "biotype": "protein_coding",
            "description": "Test gene description"
        }
    )
    response = client.get("/genes/chr1:1000-5000:+")
    assert response.status_code == 200
    assert response.json()["coord_id"] == "chr1:1000-5000:+"
    assert response.json()["gene_name"] == "GeneA"


def test_update_gene():
    client.post(
        "/genes/",
        json={
            "coord_id": "chr1:1000-5000:+",
            "chromosome": "chr1",
            "chrom_start": 1000,
            "chrom_end": 5000,
            "strand": "+",
            "ensembl_id": "ENSG000001",
            "gene_name": "GeneA",
            "biotype": "protein_coding",
            "description": "Test gene description"
        }
    )
    response = client.put(
        "/genes/chr1:1000-5000:+",
        json={
            "coord_id": "chr1:1000-5000:+",
            "chromosome": "chr1",
            "chrom_start": 1500,
            "chrom_end": 5500,
            "strand": "+",
            "ensembl_id": "ENSG000001",
            "gene_name": "UpdatedGeneA",
            "biotype": "protein_coding",
            "description": "Updated gene description"
        }
    )
    assert response.status_code == 200
    assert response.json()["chrom_start"] == 1500
    assert response.json()["gene_name"] == "UpdatedGeneA"


def test_delete_gene():
    client.post(
        "/genes/",
        json={
            "coord_id": "chr1:1000-5000:+",
            "chromosome": "chr1",
            "chrom_start": 1000,
            "chrom_end": 5000,
            "strand": "+",
            "ensembl_id": "ENSG000001",
            "gene_name": "GeneA",
            "biotype": "protein_coding",
            "description": "Test gene description"
        }
    )
    response = client.delete("/genes/chr1:1000-5000:+")
    assert response.status_code == 200
    get_response = client.get("/genes/chr1:1000-5000:+")
    assert get_response.status_code == 404
