variable "aws_region" {
  default = "eu-west-2"
}

variable "cluster_name" {
  default = "fastapi-cluster"
}

variable "task_name" {
  default = "fastapi-task"
}

variable "service_name" {
  default = "fastapi-service"
}

variable "s3_bucket_name" {
  default = "cf-templates-1uuth22f8zph5-eu-west-2"
}

variable "rds_cluster_identifier" {
  default = "fastapi-rds-cluster"
}

variable "rds_database_name" {
  default = "fastapidb"
}

variable "db_username" {
  default = "admin"
}

variable "db_password" {
  default = "informatics"
}

variable "cidr_block" {
  default = "10.0.0.0/16"
}

variable "ddl_file_path" {
  default = "ddl/db.sql"
}

