# FastAPI RNAseq Project

## Overview

This project is a FastAPI-based web application designed to handle RNASeq data. It allows users to upload gene expression datasets, perform exploratory data analysis (EDA), and view results through a user-friendly web interface. The application is containerized using Docker and deployed to AWS using ECS Fargate with an RDS MySQL database.

## Features

- User authentication and session management
- Upload CSV files containing RNASeq data
- Store uploaded files in S3
- Perform background tasks for data processing and analysis
- Dynamic visualization of RNASeq data using Plotly
- Deployment via ECS Fargate with auto-scaling and RDS MySQL database

## Prerequisites

- Python 3.9+
- Docker
- Terraform
- AWS CLI configured with appropriate credentials

## Getting Started

1. Clone the Repository
```
git clone https://github.com/osagiei/rnaseq-fastapi-app-v1.git
cd rnaseq-fastapi-app/ecs
```
2. Set Up the Environment.
   
Create a .env file with the following variables:
```
SECRET_KEY=
DATABASE_URL=
S3_BUCKET_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
DBUSER=
DBPASSWORD=
DBHOST=
DBPORT=
DBNAME=
```
3. Install Dependencies
```
pip install -r requirements.txt
```
4. Run Locally with Docker.
   
Build and run the Docker container locally:
```
docker build -t fastapi-app .
docker run -p 8000:80 fastapi-app
```
5. Deploy to AWS with Terraform.
   
Navigate to the terraform directory and apply the Terraform configuration:
```
cd ..
terraform init
terraform plan
terraform apply
```
Destroy or remove resources using: ```terraform destroy```

After a successful deployment, you'll receive output containing the URL to access the application.

6. Access the Application
Use the load_balancer_dns output from Terraform to access the application in your browser.


