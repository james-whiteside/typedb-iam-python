import decimal
import math
import configparser
from configparser import NoSectionError
import src.io_controller as io_controller


def sigfig(n, sf):
    if float(n) == 0.0:
        return 0.0
    else:
        return round(float(n), -int(math.floor(math.log10(abs(float(n)))) - sf + 1))


def intsigfig(n, sf):
    if abs(n) >= 10 ** (sf - 1):
        return int(round(n))
    else:
        return sigfig(n, sf)


def format_time(time):
    seconds = time % 60
    time = int(round((time - seconds) / 60))
    minutes = time % 60
    hours = int(round((time - minutes) / 60))
    return str(hours).zfill(2) + ':' + str(minutes).zfill(2) + ':' + str(seconds).zfill(2)


def get_file_length(filepath):
    with open(filepath, 'rb') as file:
        length = 0
        buffer_size = 1024 ** 2
        read_file = file.raw.read
        buffer = read_file(buffer_size)

        while buffer:
            length += buffer.count(b'\n')
            buffer = read_file(buffer_size)

    return length


def cast_string(string):
    if string.lower() == 'none':
        return None
    elif string.lower() == 'true':
        return True
    elif string.lower() == 'false':
        return False
    elif string.strip('1234567890-') == '':
        return int(string)
    elif string.strip('1234567890-.') == '':
        return decimal.Decimal(string)
    else:
        return string


def get_config_params(filepath, section):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(filepath)
    params = dict()

    try:
        for option in config.options(section):
            value = config.get(section, option)

            if value is not None:
                params[option] = value
    except NoSectionError:
        io_controller.out_fatal('No section with name', section, 'in config file:', filepath)
        io_controller.kill()

    return params


def sanitise_strings(record, escape_mode='double'):
    if escape_mode == 'double':
        for i in range(len(record)):
            record[i] = record[i].replace('\'', '\'\'').replace('\"', '\"\"')
    elif escape_mode == 'backslash':
        for i in range(len(record)):
            record[i] = record[i].replace('\'', '\\\'').replace('\"', '\\\"')

    return record
