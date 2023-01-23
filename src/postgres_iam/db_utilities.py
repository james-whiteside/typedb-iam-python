import os
import src.utilities as utilities
import src.io_controller as io_controller


def get_database_name():
    try:
        database = utilities.get_config_params('postgres_config.ini', 'database')['database_name']

        if database == '':
            raise KeyError

        return database
    except KeyError:
        io_controller.out_fatal('Attempted to use default database but none was set.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def unpack_queries(query_string):
    return list(query + ';' for query in query_string.split(';\n'))


def get_saved_query(query_name, query_section):
    try:
        file_name = utilities.get_config_params('postgres_config.ini', query_section)[query_name]

        if file_name == '':
            raise KeyError

        file_path = 'queries/' + file_name

        with open(file_path) as file:
            io_controller.out_debug('Getting saved query from:', file_path)
            return file.read()
    except KeyError:
        io_controller.out_fatal('Attempted to find saved query with name', query_name, 'but no filepath was set.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()
    except FileNotFoundError:
        io_controller.out_fatal('Attempted to get saved query', file_name, 'but no file was found.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def get_saved_queries(query_section):
    query_strings = list(get_saved_query(query_name, query_section) for query_name in utilities.get_config_params('postgres_config.ini', query_section))
    queries = list()

    for query_string in query_strings:
        queries += unpack_queries(query_string)

    return queries
