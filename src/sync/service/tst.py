import random
import uuid

from src.sync import uow
from src.sync.models import ValueObject
from utils.fake import get_random_string


def start_service(first_db_uow: 'uow.AbstractUnitOfWork', second_db_uow: 'uow.AbstractUnitOfWork'):
    while True:
        add_bulk_value_objects(first_db_uow, second_db_uow)


def add_bulk_value_objects(first_db_uow: 'uow.AbstractUnitOfWork', second_db_uow: 'uow.AbstractUnitOfWork'):
    selected_uow = random.choice([first_db_uow, second_db_uow])

    value_objects = [ValueObject(uuid.uuid4(), get_random_string()) for _ in range(1000)]

    selected_uow.value_objects.add_bulk(value_objects)

    selected_uow.commit()
