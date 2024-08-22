from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


class Metadata(Base):
    __tablename__ = "metadata"

    metadata_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True)
    reference_genome_path = Column(String(255))
    reference_transcriptome_path = Column(String(255))
    known_variants_path = Column(String(255))


class Gene(Base):
    __tablename__ = "gene"

    coord_id = Column(String(25), primary_key=True)
    chromosome = Column(String(10))
    chrom_start = Column(Integer)
    chrom_end = Column(Integer)
    strand = Column(Enum('+', '-', 'UNKWN'))
    ensembl_id = Column(String(25))
    refseq_id = Column(String(25))
    gene_name = Column(String(25))
    biotype = Column(String(25))
    description = Column(String(255))


class Sample(Base):
    __tablename__ = "sample"

    sample_id = Column(String(100), primary_key=True, index=True)
    sample_description = Column(String(255), nullable=True)
    sample_type = Column(String(50), nullable=True)
    sample_source = Column(String(50), nullable=True)


class GeneExpression(Base):
    __tablename__ = "gene_expression"

    gene_expression_id = Column(Integer, primary_key=True, index=True)
    raw_count = Column(Integer, nullable=False)
    TPM = Column(Float, nullable=True)
    FPKM = Column(Float, nullable=True)
    RPKM = Column(Float, nullable=True)
    gene_name = Column(String(25), nullable=False)
    sample_id = Column(
        String(100),
        ForeignKey("sample.sample_id"),
        nullable=False)
    analysis_id = Column(
        Integer,
        ForeignKey("analysis.analysis_id"),
        nullable=False)


class SampleClustering(Base):
    __tablename__ = "sample_clustering"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(100), ForeignKey("sample.sample_id"))
    pca1 = Column(Float)
    pca2 = Column(Float)
    cluster = Column(Integer)
    analysis_id = Column(Integer, ForeignKey("analysis.analysis_id"))

    analysis = relationship("Analysis", back_populates="sample_clusterings")


class TissueSpecificity(Base):
    __tablename__ = "tissue_specificity"

    id = Column(Integer, primary_key=True, index=True)
    gene_name = Column(String(255))
    tau = Column(Float)
    analysis_id = Column(Integer, ForeignKey("analysis.analysis_id"))

    analysis = relationship("Analysis", back_populates="tissue_specificities")


class TissueComplexity(Base):
    __tablename__ = "tissue_complexity"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(100), ForeignKey("sample.sample_id"))
    gene_biotype = Column(String(255))
    proportion = Column(Float)
    total_reads = Column(Integer)
    analysis_id = Column(Integer, ForeignKey("analysis.analysis_id"))

    analysis = relationship("Analysis", back_populates="tissue_complexities")


class Analysis(Base):
    __tablename__ = "analysis"

    analysis_id = Column(Integer, primary_key=True, index=True)
    logic_name = Column(String(50))
    samplesheet_path = Column(String(255))
    analysis_date = Column(Date)
    analysis_parameters = Column(String(255))
    metadata_id = Column(Integer, ForeignKey("metadata.metadata_id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    sample_clusterings = relationship(
        "SampleClustering", back_populates="analysis")
    tissue_specificities = relationship(
        "TissueSpecificity", back_populates="analysis")
    tissue_complexities = relationship(
        "TissueComplexity", back_populates="analysis")
