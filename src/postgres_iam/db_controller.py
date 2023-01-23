import os
import postgresql
from postgresql.exceptions import ClientCannotConnectError
import src.io_controller as io_controller
from src.io_controller import ProgressBar
import src.postgres_iam.db_utilities as db_utilities


def client():
    database = db_utilities.get_database_name()

    try:
        return postgresql.open(database=database)
    except ClientCannotConnectError:
        io_controller.out_fatal('Could not establish connection to database.')
        io_controller.out_fatal('Server is not running, database does not exist, or client is improperly configured.')
        io_controller.out_fatal('Check database exists with PostgreSQL CLI.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def execute(client, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            prepared_query = client.prepare(query)
            result = prepared_query()
            results.append(result)
            progress_bar.increment()

    return results


def get_tables(client):
    query = ' '.join([
        "SELECT tablename",
        "FROM pg_catalog.pg_tables",
        "WHERE schemaname = 'public';"
    ])

    queries = [query]
    results = execute(client, queries)[0]
    return list(result[0] for result in results)


def schema_exists(client):
    return len(get_tables(client)) != 0


def drop_table(client, table, verify=False, cascade=True):
    if not verify:
        arg_verify = 'IF EXISTS'
    else:
        arg_verify = ''

    if cascade:
        arg_cascade = 'CASCADE'
    else:
        arg_cascade = ''

    query = "DROP TABLE %s %s %s;" % (arg_verify, table, arg_cascade)
    queries = [query]
    execute(client, queries)


def drop_schema(client):
    for table in get_tables(client):
        drop_table(client, table)


def count_records(client):
    tables = get_tables(client)
    queries = list()

    for table in tables:
        query = "SELECT COUNT(*) FROM %s;" % table
        queries.append(query)

    results = execute(client, queries)
    return sum(int(result[0][0]) for result in results)


def data_exists(client):
    return count_records(client) != 0


def clear_table(client, table, cascade=True):
    if cascade:
        arg_cascade = 'CASCADE'
    else:
        arg_cascade = ''

    query = "DELETE FROM %s %s;" % (table, arg_cascade)
    queries = [query]
    execute(client, queries)


def clear_data(client):
    for table in get_tables(client):
        clear_table(client, table)
