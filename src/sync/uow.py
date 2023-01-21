import abc

from sqlalchemy.orm import sessionmaker

from src.sync import repository
from src.sync import exceptions


class AbstractUnitOfWork(abc.ABC):
    def __init__(self):
        self._value_objects = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    def commit(self):
        self._commit()

    def rollback(self):
        self._rollback()

    def init_repositories(self, value_objects_repository: repository.AbstractRepository):
        self._value_objects = value_objects_repository

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _rollback(self):
        raise NotImplementedError

    @property
    def value_objects(self) -> repository.AbstractRepository:
        if not self._value_objects:
            raise exceptions.NotDefinedRepositoryError

        return self._value_objects


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, engine):
        super().__init__()
        self.session = sessionmaker(bind=engine)()
        self.init_repositories(repository.SqlAlchemyObjectValueRepository(self.session))

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()
