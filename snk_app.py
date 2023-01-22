from sqlalchemy import create_engine

from src.sync import orm
from src.sync import uow
from src.sync import cache
from src.sync.service import snk
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, FIRST_DB_HOST, SECOND_DB_HOST, REDIS_HOST, REDIS_PORT

first_db_engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{FIRST_DB_HOST}/{POSTGRES_DB}",
)

second_db_engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{SECOND_DB_HOST}/{POSTGRES_DB}",
)

redis_cache = cache.RedisCache(host=REDIS_HOST, port=REDIS_PORT)

if __name__ == "__main__":
    orm.start_mappers()

    redis_cache.flush()

    with uow.SqlAlchemyUnitOfWork(first_db_engine) as first_db_uow:
        with uow.SqlAlchemyUnitOfWork(second_db_engine) as second_db_uow:
            snk.start_service(first_db_uow=first_db_uow,
                              second_db_uow=second_db_uow,
                              cache=redis_cache)
