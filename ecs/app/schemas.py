from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class GeneBase(BaseModel):
    coord_id: str
    chromosome: Optional[str] = None
    chrom_start: Optional[int] = None
    chrom_end: Optional[int] = None
    strand: Optional[str] = None
    ensembl_id: Optional[str] = None
    refseq_id: Optional[str] = None
    gene_name: Optional[str] = None
    biotype: Optional[str] = None
    description: Optional[str] = None


class GeneCreate(GeneBase):
    pass


class Gene(GeneBase):
    class Config:
        orm_mode = True


class GeneExpressionBase(BaseModel):
    raw_count: int
    TPM: Optional[float] = None
    FPKM: Optional[float] = None
    RPKM: Optional[float] = None
    gene_name: Optional[str] = None
    sample_id: str
    analysis_id: int


class GeneExpressionCreate(GeneExpressionBase):
    pass


class GeneExpression(GeneExpressionBase):
    gene_expression_id: int

    class Config:
        orm_mode = True


class AnalysisBase(BaseModel):
    logic_name: str
    samplesheet_path: Optional[str] = None
    analysis_date: Optional[date] = None
    analysis_parameters: Optional[str] = None
    metadata_id: Optional[int] = None


class AnalysisCreate(BaseModel):
    logic_name: str
    samplesheet_path: str
    analysis_date: Optional[date] = None
    analysis_parameters: Optional[str] = None
    metadata_id: Optional[int] = None

    class Config:
        orm_mode = True


class Analysis(AnalysisBase):
    analysis_id: int
    session_id: str

    class Config:
        orm_mode = True


class SampleBase(BaseModel):
    sample_id: str
    sample_description: Optional[str] = None
    sample_type: Optional[str] = None
    sample_source: Optional[str] = None


class SampleCreate(SampleBase):
    pass


class Sample(SampleBase):
    class Config:
        orm_mode = True


class TissueSpecificityBase(BaseModel):
    gene_name: str
    tau: float
    analysis_id: int
    #sample_id: Optional[str] = None


class TissueSpecificityCreate(TissueSpecificityBase):
    pass


class TissueSpecificity(TissueSpecificityBase):
    tissue_specificity_id: int

    class Config:
        orm_mode = True


class TissueComplexityBase(BaseModel):
    gene_biotype: str
    proportion: float
    total_reads: int
    analysis_id: int
    sample_id: Optional[str] = None


class TissueComplexityCreate(TissueComplexityBase):
    pass


class TissueComplexity(TissueComplexityBase):
    tissue_complexity_id: int

    class Config:
        orm_mode = True


class MetadataBase(BaseModel):
    reference_genome_path: Optional[str] = None
    reference_transcriptome_path: Optional[str] = None
    known_variants_path: Optional[str] = None


class MetadataCreate(MetadataBase):
    pass


class Metadata(MetadataBase):
    metadata_id: int

    class Config:
        orm_mode = True


class SampleClusteringBase(BaseModel):
    sample_id: str
    pca1: float
    pca2: float
    cluster: int
    analysis_id: int


class SampleClusteringCreate(SampleClusteringBase):
    pass


class SampleClustering(SampleClusteringBase):
    id: int

    class Config:
        orm_mode = True
