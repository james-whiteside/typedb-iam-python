import os
from typedb.client import SessionType, TypeDBOptions
from typedb.common.exception import TypeDBClientException
import src.utilities as utilities
import src.io_controller as io_controller
import src.data_generation as data_generation
import src.db_utilities as db_utilities
import src.db_controller as db_controller
import src.data_loaders as data_loaders


def generate_new_dataset():
    data = data_generation.generate_data()
    data_generation.save_data(data)


def ensure_server_connection(client):
    try:
        db_controller.get_databases(client)
        io_controller.out_info('Connection to database server confirmed.')
        return True
    except TypeDBClientException:
        io_controller.out_fatal('Could not establish connection to database server.')
        io_controller.out_fatal('Server is not running or client is improperly configured.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def create_database(client):
    database = db_utilities.get_database_name()

    if db_controller.database_exists(client, database):
        io_controller.out_warning('Existing database with name', database, 'will be deleted.')

        if io_controller.in_input('Continue with database creation? (Y/N)').lower() != 'y':
            io_controller.out_info('Database creation aborted.')
            return False
        else:
            db_controller.delete_database(client, database)

    db_controller.create_database(client, database)
    io_controller.out_info('Created database:', database)
    return True


def define_schema(client):
    database = db_utilities.get_database_name()

    with client.session(database=database, session_type=SessionType.SCHEMA) as session:
        if db_controller.schema_exists(session):
            io_controller.out_warning('Schema already defined for database:', database)

            if io_controller.in_input('Continue with schema definition? (Y/N)').lower() != 'y':
                io_controller.out_info('Schema definition aborted.')
                return False

        schema_queries = db_utilities.get_saved_queries('schema_queries')
        db_controller.define(session, schema_queries)
        io_controller.out_info('Defined schema for database:', database)
        return True


def load_data(client):
    database = db_utilities.get_database_name()

    with client.session(database=database, session_type=SessionType.DATA) as session:
        if db_controller.data_exists(session):
            io_controller.out_warning('Data already exists in database:', database)

            if io_controller.in_input('Continue with data loading? (Y/N)').lower() != 'y':
                io_controller.out_info('Data loading aborted.')
                return False

        data_loaders.load_data(session)
        io_controller.out_info('Data loaded for database:', database)
        return True


def rebuild_database(client):
    result = create_database(client)

    if not result:
        return False

    define_schema(client)
    load_data(client)
    return True


def provide_graph_statistics(client):
    database = db_utilities.get_database_name()

    with client.session(database=database, session_type=SessionType.DATA) as session:
        try:
            statistics = db_controller.get_graph_statistics(session)
        except TypeDBClientException:
            if not db_controller.database_exists(client, database):
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


def run_test_queries(client):
    database = db_utilities.get_database_name()
    options = TypeDBOptions.core().set_infer(db_utilities.get_rule_inference())

    with client.session(database=database, session_type=SessionType.DATA, options=options) as session:
        test_queries = db_utilities.get_saved_queries('test_queries')

        for query in test_queries:
            io_controller.out_info('Running test query:', ' '.join(query.replace('\n', ' ').split()))
            queries = [query]

            try:
                results = db_controller.get(session, queries)
            except TypeDBClientException as exception:
                io_controller.out_exception(exception)
                continue

            result = results[0]

            if len(result) == 0:
                io_controller.out_info('Returned 0 results.')
            else:
                io_controller.out_info('Returned', len(result), 'results:')

                for item in result:
                    io_controller.out_info(item)
