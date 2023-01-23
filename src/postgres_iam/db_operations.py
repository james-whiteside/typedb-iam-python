import os
from postgresql.exceptions import ClientCannotConnectError
import src.io_controller as io_controller
import src.postgres_iam.db_utilities as db_utilities
import src.postgres_iam.db_controller as db_controller
import src.postgres_iam.data_loaders as data_loaders


def ensure_server_connection(client):
    try:
        db_controller.get_tables(client)
        io_controller.out_info('Connection to database server confirmed.')
        return True
    except ClientCannotConnectError:
        io_controller.out_fatal('Could not establish connection to database.')
        io_controller.out_fatal('Server is not running, database does not exist, or client is improperly configured.')
        io_controller.out_fatal('Check database exists with PostgreSQL CLI.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def define_schema(client):
    database = db_utilities.get_database_name()

    if db_controller.schema_exists(client):
        io_controller.out_warn('Schema already defined for database:', database)

        if io_controller.in_input('Continue with schema definition? (Y/N)').lower() != 'y':
            io_controller.out_info('Schema definition aborted.')
            return False

    db_controller.drop_schema(client)
    schema_queries = db_utilities.get_saved_queries('schema_queries')
    db_controller.execute(client, schema_queries)
    io_controller.out_info('Defined schema for database:', database)
    return True


def load_data(client):
    database = db_utilities.get_database_name()

    if db_controller.data_exists(client):
        io_controller.out_warn('Data already exists in database:', database)

        if io_controller.in_input('Continue with data loading? (Y/N)').lower() != 'y':
            io_controller.out_info('Data loading aborted.')
            return False

    data_loaders.load_data(client)
    io_controller.out_info('Data loaded for database:', database)
    return True


def rebuild_database(client):
    define_schema(client)
    load_data(client)
    return True
