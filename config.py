import os
from dotenv import load_dotenv

load_dotenv()


class config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
