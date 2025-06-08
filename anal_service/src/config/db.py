import os
from dotenv import load_dotenv

load_dotenv()

class DBConfig:
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", 5432))
    NAME = os.getenv("DB_NAME", "vacancy_db")
    USER = os.getenv("DB_USER", "vacancy_user")
    PASSWORD = os.getenv("DB_PASSWORD", "supersecret")

    @classmethod
    def as_dict(cls):
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "dbname": cls.NAME,
            "user": cls.USER,
            "password": cls.PASSWORD
        }
