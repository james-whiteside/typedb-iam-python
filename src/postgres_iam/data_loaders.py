import src.io_controller as io_controller
import src.postgres_iam.db_controller as db_controller
import src.data_generation as data_generation


def load_users(client):
    pass


def load_user_groups(client):
    pass


def load_subjects(client):
    load_users(client)
    load_user_groups(client)


def load_resources(client):
    pass


def load_resource_collections(client):
    pass


def load_objects(client):
    load_resources(client)
    load_resource_collections(client)


def load_operations(client):
    pass


def load_operation_sets(client):
    pass


def load_actions(client):
    load_operations(client)
    load_operation_sets(client)


def load_permissions(client):
    pass


def load_data(client):
    load_subjects(client)
    load_objects(client)
    load_actions(client)
    load_permissions(client)
