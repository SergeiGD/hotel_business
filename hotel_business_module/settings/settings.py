from pytz import timezone
from os import environ
from datetime import timedelta
import pathlib


TIMEZONE = timezone('Asia/Irkutsk')
EMAIL_USER = environ.get('EMAIL_USER')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')
EMAIL_HOST = environ.get('EMAIL_HOST')
SITE_URL = environ.get('SITE_URL', 'http://localhost:8080')
SECRET_KEY = environ.get('SECRET_KEY', 'my_very_secret_key')
ACCESS_TOKEN_LIVE_TIME = timedelta(minutes=60)
REFRESH_TOKEN_LIVE_TIME = timedelta(days=7)
MEDIA_DIR = f'{pathlib.Path().resolve()}/media'
