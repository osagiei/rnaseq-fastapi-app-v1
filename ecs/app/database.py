from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    with engine.connect() as connection:
        ddl_file_path = "app/db.sql"
        with open(ddl_file_path, "r") as ddl_file:
            ddl_commands = ddl_file.read()

        ddl_statements = ddl_commands.split(';')

        try:
            for statement in ddl_statements:
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))
        except SQLAlchemyError as e:
            print(f"An error occurred while executing DDL: {e}")


init_db()
