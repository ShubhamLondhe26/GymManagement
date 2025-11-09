import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        # update user:password@host:port/dbname as needed
        "mysql+pymysql://gymuser:gympass@localhost:3306/gymdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
