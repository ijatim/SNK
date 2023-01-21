from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapper

from src.sync.models import ValueObject


metadata = MetaData()

value_objects_table = Table(
    "value_objects",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("uuid", UUID(as_uuid=True), index=True, unique=True),
    Column('data', String(255)),
)


def drop_tables_in_all_dbs(*args):
    for db_engine in args:
        metadata.drop_all(db_engine)


def create_tables_in_all_dbs(*args):
    for db_engine in args:
        metadata.create_all(db_engine)


def start_mappers():
    mapper(ValueObject, value_objects_table)
