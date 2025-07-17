import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'), encoding='utf-8')

class Config:
    SQLALCHEMY_DATABASE_URI        = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EMAIL_USER   = os.getenv("EMAIL_USER")
    EMAIL_PASS   = os.getenv("EMAIL_PASS")
    IMAP_HOST    = os.getenv("IMAP_HOST")
    IMAP_FOLDER  = os.getenv("IMAP_FOLDER", "INBOX")
    IMAP_PORT = os.getenv("IMAP_PORT")
