from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import date

from app.main import app
from app.database import Base, get_db
from app.models import Sample, Analysis, GeneExpression

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

    db = TestingSessionLocal()
    sample = Sample(
        sample_id="sample123",
        sample_description="Test Sample",
        sample_type="blood",
        sample_source="human"
    )
    analysis = Analysis(
        logic_name="test_analysis",
        samplesheet_path="/path/to/samplesheet",
        analysis_date=date(2024, 8, 18),
        analysis_parameters="param1",
        metadata_id=None
    )
    db.add(sample)
    db.add(analysis)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_create_gene_expression():
    response = client.post(
        "/gene_expressions/",
        json={
            "raw_count": 1000,
            "TPM": 0.5,
            "FPKM": 1.5,
            "RPKM": 2.0,
            "gene_name": "GeneA",
            "sample_id": "sample123",
            "analysis_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gene_name"] == "GeneA"
    assert data["sample_id"] == "sample123"
    assert data["analysis_id"] == 1
