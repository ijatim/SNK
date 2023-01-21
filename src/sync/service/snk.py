from src.sync import uow
from src.sync.models import ValueObject


def start_service(first_db_uow: 'uow.AbstractUnitOfWork', second_db_uow: 'uow.AbstractUnitOfWork', cache):
    limit = 200

    while True:
        # Get first database's 200 records after the last synced value_object
        first_db_records = first_db_uow.value_objects.list_gt_id(
            object_value_id=cache.first_database_last_synced_value_object_id, limit=limit
        )
        first_database_last_synced_value_object_id = first_db_records[-1:][0][0] if first_db_records[-1:] \
            else cache.first_database_last_synced_value_object_id
        first_db_records = {
            (row.uuid, row.data) for row in first_db_records
        }

        # Get second database's 200 records after the last synced value_object
        second_db_records = second_db_uow.value_objects.list_gt_id(
            object_value_id=cache.second_database_last_synced_value_object_id, limit=limit
        )
        second_database_last_synced_value_object_id = second_db_records[-1:][0][0] if second_db_records[-1:] \
            else cache.second_database_last_synced_value_object_id
        second_db_records = {
            (row.uuid, row.data) for row in second_db_records
        }

        # These are possible value_objects nominated for bulk insertion
        # These may contain previously added records that must be filtered else we will encounter unique constraint
        # violation
        possible_not_available_value_objects_in_first_db = second_db_records
        possible_not_available_value_objects_in_second_db = first_db_records

        # These steps remove previously added records to ensure uniqueness of inserted records
        previously_added_in_first_db = set()
        not_available_value_objects_in_first_db = set()
        for item in possible_not_available_value_objects_in_first_db:
            if cache.exists(str(item[0])):
                previously_added_in_first_db.add(item[0])
            else:
                not_available_value_objects_in_first_db.add(item)

        previously_added_in_second_db = set()
        not_available_value_objects_in_second_db = set()
        for item in possible_not_available_value_objects_in_second_db:
            if cache.exists(str(item[0])):
                previously_added_in_second_db.add(item[0])
            else:
                not_available_value_objects_in_second_db.add(item)

        # Bulk insertion
        first_db_uow.value_objects.add_bulk(
            [ValueObject(object_value[0], object_value[1]) for object_value in not_available_value_objects_in_first_db]
        )
        second_db_uow.value_objects.add_bulk(
            [ValueObject(object_value[0], object_value[1]) for object_value in not_available_value_objects_in_second_db]
        )

        # Bulk cache insert
        going_to_be_added_cache_keys = map(
            lambda item: str(item[0]),
            (not_available_value_objects_in_first_db | not_available_value_objects_in_second_db)
        )
        cache.set_multiple(1, *going_to_be_added_cache_keys)

        # Bulk cache delete
        going_to_be_deleted_cache_keys = map(
            lambda item: str(item), (previously_added_in_first_db | previously_added_in_second_db)
        )
        cache.delete(*going_to_be_deleted_cache_keys)

        # Insertion commit and last synced record updated in cache
        first_db_uow.commit()
        cache.first_database_last_synced_value_object_id = first_database_last_synced_value_object_id

        second_db_uow.commit()
        cache.second_database_last_synced_value_object_id = second_database_last_synced_value_object_id
