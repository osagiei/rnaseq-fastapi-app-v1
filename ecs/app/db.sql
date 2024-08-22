DROP DATABASE IF EXISTS rnaseq_db;
CREATE DATABASE IF NOT EXISTS rnaseq_db;
USE rnaseq_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_users_email (email),
    INDEX idx_users_id (id)
);


CREATE TABLE IF NOT EXISTS metadata (
    metadata_id INT AUTO_INCREMENT PRIMARY KEY,
    reference_genome_path VARCHAR(255),
    reference_transcriptome_path VARCHAR(255),
    known_variants_path VARCHAR(255)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS gene (
  coord_id VARCHAR(125) NOT NULL,
  chromosome VARCHAR(10) NULL DEFAULT NULL,
  chrom_start INT NULL DEFAULT NULL,
  chrom_end INT NULL DEFAULT NULL,
  strand ENUM('+', '-', 'UNKWN') NULL DEFAULT NULL,
  ensembl_id VARCHAR(25) NULL DEFAULT NULL,
  refseq_id VARCHAR(25) NULL DEFAULT NULL,
  gene_name VARCHAR(25) NULL DEFAULT NULL,
  biotype VARCHAR(255) NULL DEFAULT NULL,
  description VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (coord_id),
  INDEX idx_chromosome (chromosome),
  INDEX idx_chrom_start (chrom_start),
  INDEX idx_chrom_end (chrom_end)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sample (
    sample_id VARCHAR(100) PRIMARY KEY,
    sample_description VARCHAR(255),
    sample_type VARCHAR(50),
    sample_source VARCHAR(50)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    logic_name VARCHAR(50) NOT NULL,
    samplesheet_path VARCHAR(255),
    analysis_date DATE DEFAULT (CURRENT_DATE),
    analysis_parameters VARCHAR(255), 
    metadata_id INT,
    FOREIGN KEY (metadata_id) REFERENCES metadata(metadata_id)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS gene_expression (
  gene_expression_id INT NOT NULL AUTO_INCREMENT,
  raw_count INT NOT NULL,
  TPM FLOAT NULL DEFAULT NULL,
  FPKM FLOAT NULL DEFAULT NULL,
  RPKM FLOAT NULL DEFAULT NULL,
  gene_name VARCHAR(25),
  sample_id VARCHAR(100) NOT NULL,
  analysis_id INT NOT NULL,
  PRIMARY KEY (gene_expression_id),
  KEY idx_sample_id (sample_id),
  KEY idx_analysis_id (analysis_id),
  CONSTRAINT fk_gene_expression_sample1 FOREIGN KEY (sample_id) REFERENCES sample (sample_id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_gene_expression_analysis1 FOREIGN KEY (analysis_id) REFERENCES analysis (analysis_id) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS sample_clustering (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id VARCHAR(100),
    pca1 FLOAT,
    pca2 FLOAT,
    cluster INT,
    analysis_id INT,
    FOREIGN KEY (analysis_id) REFERENCES analysis(analysis_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tissue_specificity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gene_name VARCHAR(255),
    tau FLOAT,
    analysis_id INT,
    FOREIGN KEY (analysis_id) REFERENCES analysis(analysis_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tissue_complexity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id VARCHAR(100),
    gene_biotype VARCHAR(255),
    proportion FLOAT,
    total_reads INT,
    analysis_id INT,
    FOREIGN KEY (analysis_id) REFERENCES analysis(analysis_id) ON DELETE CASCADE
);

ALTER TABLE analysis ADD COLUMN user_id INT NOT NULL;
