import os
import src.utilities as utilities
import src.io_controller as io_controller


def get_database_name():
    try:
        database = utilities.get_config_params('config.ini', 'database')['database_name']

        if database == '':
            raise KeyError

        return database
    except KeyError:
        io_controller.out_fatal('Attempted to use default database but none was set.')
        io_controller.out_fatal('Check configuration at:', os.getcwd() + '/config.ini')
        io_controller.kill()


def get_rule_inference():
    try:
        inference = utilities.get_config_params('config.ini', 'database')['rule_inference']

        if inference.lower() == 'false':
            io_controller.out_debug('Rule inference set to false.')
            return False
        elif inference.lower() == 'true':
            io_controller.out_debug('Rule inference set to true.')
            return True
        else:
            raise KeyError
    except KeyError:
        io_controller.out_debug('Rule inference set to false by default as no correct option was set.')
        io_controller.out_debug('Check configuration at:', os.getcwd() + '/config.ini')
        return False


def get_saved_query(query_name, query_section):
    try:
        file_name = utilities.get_config_params('config.ini', query_section)[query_name]

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
    return list(get_saved_query(query_name, query_section) for query_name in utilities.get_config_params('config.ini', query_section))
