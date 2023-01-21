from sqlalchemy import create_engine

from src.sync import orm
from src.sync.service import tst
from src.sync import uow
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, FIRST_DB_HOST, SECOND_DB_HOST

first_db_engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{FIRST_DB_HOST}/{POSTGRES_DB}",
    )

second_db_engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{SECOND_DB_HOST}/{POSTGRES_DB}",
    )


if __name__ == "__main__":
    orm.start_mappers()
    orm.drop_tables_in_all_dbs(first_db_engine, second_db_engine)
    orm.create_tables_in_all_dbs(first_db_engine, second_db_engine)

    with uow.SqlAlchemyUnitOfWork(first_db_engine) as first_db_uow:
        with uow.SqlAlchemyUnitOfWork(second_db_engine) as second_db_uow:
            tst.start_service(first_db_uow=first_db_uow,
                              second_db_uow=second_db_uow)
