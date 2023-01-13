import os
from typedb.common.exception import TypeDBClientException
import src.utilities as utilities
import src.io_controller as io_controller
import src.db_connector as db_connector
import src.db_controller as db_controller
import src.data_loaders as data_loaders


def ensure_connection():
    try:
        db_controller.get_databases()
        io_controller.out_info('Connection to database server confirmed.')
        return True
    except TypeDBClientException:
        io_controller.out_fatal('Could not establish connection to database server.')
        io_controller.out_fatal('Server is not running or client is improperly configured.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def create_database():
    database = db_connector.get_database_name()

    if db_controller.database_exists(database):
        io_controller.out_warning('Existing database with name', database, 'will be deleted.')

        if io_controller.in_input('Continue with database creation? (Y/N)').lower() != 'y':
            io_controller.out_info('Database creation aborted.')
            return False
        else:
            db_controller.delete_database(database)

    db_controller.create_database(database)
    io_controller.out_info('Created database:', database)
    return True


def define_schema():
    database = db_connector.get_database_name()

    if db_controller.schema_exists(database):
        io_controller.out_warning('Schema already defined for database:', database)

        if io_controller.in_input('Continue with schema definition? (Y/N)').lower() != 'y':
            io_controller.out_info('Schema definition aborted.')
            return False

    schema_queries = db_connector.get_saved_queries('schema_queries')

    for query in schema_queries:
        db_controller.define(query, database)

    io_controller.out_info('Defined schema for database:', database)
    return True


def load_data():
    database = db_connector.get_database_name()

    if db_controller.data_exists(database):
        io_controller.out_warning('Data already exists in database:', database)

        if io_controller.in_input('Continue with data loading? (Y/N)').lower() != 'y':
            io_controller.out_info('Data loading aborted.')
            return False

    data_loaders.load_data()
    io_controller.out_info('Data loaded for database:', database)
    return True


def rebuild_database():
    result = create_database()

    if not result:
        return False

    define_schema()
    load_data()
    return True


def provide_graph_statistics():
    database = db_connector.get_database_name()

    try:
        statistics = db_controller.get_graph_statistics(database)
    except TypeDBClientException:
        if not db_controller.database_exists(database):
            io_controller.out_error('Cannot provide graph statistics as no database with name', database, 'exists.')
        else:
            io_controller.out_error('Cannot provide graph statistics as schema is undefined for database:', database)

        return False
    except ZeroDivisionError:
        io_controller.out_error('Cannot provide graph statistics as there is no data loaded for database:', database)
        return False

    io_controller.out_info('Displaying graph statistics for database:', database)

    for stat_name in statistics:
        io_controller.out_info(stat_name.replace('_', ' ').capitalize() + ':', utilities.intsigfig(statistics[stat_name], 3))

    return True


def run_test_queries():
    database = db_connector.get_database_name()
    test_queries = db_connector.get_saved_queries('test_queries')

    for query in test_queries:
        io_controller.out_info('Running test query:', ' '.join(query.replace('\n', ' ').split()))

        try:
            results = db_controller.get(query, database)
        except TypeDBClientException as exception:
            io_controller.out_exception(exception)
            continue

        if len(results) == 0:
            io_controller.out_info('Returned 0 results.')
        else:
            io_controller.out_info('Returned', len(results), 'results:')

            for result in results:
                io_controller.out_info(result)
