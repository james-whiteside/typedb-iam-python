import math
import configparser
import json
from json.decoder import JSONDecodeError


def list_print(*args, **kwargs):
    for item in args[0]:
        print(item, *args[1:], **kwargs)


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


def sanitise_strings(record, escape_mode='double'):
    if escape_mode == 'double':
        for i in range(len(record)):
            record[i] = record[i].replace('\'', '\'\'').replace('\"', '\"\"')
    elif escape_mode == 'backslash':
        for i in range(len(record)):
            record[i] = record[i].replace('\'', '\\\'').replace('\"', '\\\"')

    return record


def str_to_json(string):
    # TODO: Add proper handling of apostrophes.
    args = string.split('\'')

    for i in range(0, len(args), 2):
        args[i] = args[i].replace('True', 'true').replace('False', 'false').replace('None', 'null')

    try:
        return json.loads('"'.join(args))
    except JSONDecodeError:
        return {'could_not_convert_string_to_json': string}


def get_config_params(filepath, section):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(filepath)
    params = dict()

    for option in config.options(section):
        value = config.get(section, option)

        if value is not None:
            params[option] = value

    return params


def get_banned_words(filepath):
    with open(filepath, 'r') as file:
        words = file.read().split('\n')
        return words
