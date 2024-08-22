provider "aws" {
  region = "eu-west-2"
}

terraform {
  backend "s3" {
    bucket = "cf-templates-1uuth22f8zph5-eu-west-2"
    key    = "fastapi/terraform.tfstate"
    region = "eu-west-2"
  }
}

