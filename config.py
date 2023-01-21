from pathlib import Path
from envparse import env

BASE_DIR = Path(__file__).resolve()

env.read_envfile(f'{BASE_DIR}/.env')

POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
FIRST_DB_HOST = env.str("FIRST_DB_HOST")
SECOND_DB_HOST = env.str("SECOND_DB_HOST")
DB_PORT = env.str("DB_PORT")

REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")
