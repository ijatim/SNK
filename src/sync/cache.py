import abc
from typing import Set, Tuple
from uuid import UUID

import redis

lately_synced_value_objects: Set[Tuple[UUID, str]] = set()


class AbstractCache(abc.ABC):
    FIRST_DATABASE_LAST_SYNCED_VALUE_OBJECT_ID_KEY = "first_database_last_synced_value_object_id"
    SECOND_DATABASE_LAST_SYNCED_VALUE_OBJECT_ID_KEY = "second_database_last_synced_value_object_id"

    @property
    def first_database_last_synced_value_object_id(self):
        value = self.get(key=self.FIRST_DATABASE_LAST_SYNCED_VALUE_OBJECT_ID_KEY)
        return value and int(value) or 0

    @first_database_last_synced_value_object_id.setter
    def first_database_last_synced_value_object_id(self, value):
        self.set(key=self.FIRST_DATABASE_LAST_SYNCED_VALUE_OBJECT_ID_KEY, value=value)

    @property
    def second_database_last_synced_value_object_id(self):
        value = self.get(key=self.SECOND_DATABASE_LAST_SYNCED_VALUE_OBJECT_ID_KEY)
        return value and int(value) or 0

    @second_database_last_synced_value_object_id.setter
    def second_database_last_synced_value_object_id(self, value):
        self.set(key=self.SECOND_DATABASE_LAST_SYNCED_VALUE_OBJECT_ID_KEY, value=value)

    @abc.abstractmethod
    def set(self, key, value):
        raise NotImplementedError

    @abc.abstractmethod
    def set_multiple(self, value, *args):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, *args):
        raise NotImplementedError


class RedisCache(AbstractCache):
    def __init__(self, host, port):
        self._redis = redis.Redis(host=host, port=port)

    def set(self, key, value) -> None:
        self._redis.set(key, value)

    def set_multiple(self, value, *args):
        pipeline = self._redis.pipeline()
        for key in args:
            pipeline.set(key, value)

        pipeline.execute()

    def get(self, key):
        return self._redis.get(key)

    def exists(self, key) -> bool:
        return self._redis.exists(key) or False

    def delete(self, *args):
        if args:
            return self._redis.delete(*args)


# These two should be persisted in production environment
# first_database_last_synced_value_object_id = 0
# second_database_last_synced_value_object_id = 0
