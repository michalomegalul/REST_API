import os

from dotenv import load_dotenv

load_dotenv("/home/michaluzneni/applifting/applifting-trainee/migrations_/.env")

print(os.getenv("DATABASE_URL"))


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OFFERS_SERVICE_URL = os.getenv("OFFERS_SERVICE_URL")
    REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
    AUTH_ENDPOINT = os.getenv("AUTH_ENDPOINT")
