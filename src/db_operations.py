import os
from typedb.common.exception import TypeDBClientException
import src.db_connector as db_connector
import src.io_controller as io_controller
import src.db_controller as db_controller


def check_connection():
    try:
        db_controller.get_databases()
        io_controller.out_info('Connection established.')
    except TypeDBClientException:
        io_controller.out_fatal('Could not establish connection to database server.')
        io_controller.out_fatal('Server is not running or client is improperly configured.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def create_database():
    database = db_connector.get_database_name()

    if db_controller.database_exists(database):
        io_controller.out_warning('Existing database with name', database, 'will be deleted.')

        if io_controller.in_input('Continue with database creation? (Y/N)') == 'y':
            db_controller.delete_database(database)
        else:
            return False

    db_controller.create_database(database)
    io_controller.out_info('Created database:', database)
    return True


def define_schema():
    database = db_connector.get_database_name()
    query = db_connector.get_saved_query('define_core_schema')
    db_controller.define(query, database)
    query = db_connector.get_saved_query('define_extended_schema')
    db_controller.define(query, database)
    io_controller.out_info('Defined schema for database:', database)
