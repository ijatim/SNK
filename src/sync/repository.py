import abc
from typing import Iterator

from sqlalchemy import asc

from src.sync.models import ValueObject


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_bulk(self, *args):
        raise NotImplementedError

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError

    @abc.abstractmethod
    def list_gt_id(self, object_value_id, limit=None):
        raise NotImplementedError


class SqlAlchemyObjectValueRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add_bulk(self, *args: Iterator[ValueObject]) -> None:
        self.session.add_all(*args)

    def list(self):
        return self.session.query(ValueObject.uuid, ValueObject.data).all()

    def list_gt_id(self, object_value_id: int, limit: int = None):
        query = self.session.query(
            ValueObject.id, ValueObject.uuid, ValueObject.data
        ).filter(ValueObject.id > object_value_id).order_by(asc(ValueObject.id))

        if limit:
            query = query.limit(limit)

        return query.all()
