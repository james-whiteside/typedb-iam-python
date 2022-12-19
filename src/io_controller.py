import datetime
import os
import sys
import src.utilities as utilities


def get_log_level():
    try:
        log_arg = utilities.get_config_params('src/config.ini', 'logging')['level']
    except IndexError:
        return 5

    if log_arg in ('0', 'fatal'):
        return 0
    elif log_arg in ('1', 'error'):
        return 1
    elif log_arg in ('2', 'warning'):
        return 2
    elif log_arg in ('3', 'info'):
        return 3
    elif log_arg in ('4', 'debug'):
        return 4
    else:
        return 5


def create_log():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_name = str(datetime.datetime.now())[:19].replace(':', '-').replace(' ', '_')

    with open('logs/info.ini', 'w') as log_config:
        log_config.write('[logs]\nlast_log=' + log_name)

    with open('logs/' + log_name + '.log', 'a'):
        pass


def write_to_last_log(entry):
    try:
        last_log = utilities.get_config_params('logs/info.ini', 'logs')['last_log']
    except IndexError:
        create_log()
        last_log = utilities.get_config_params('logs/info.ini', 'logs')['last_log']

    with open('logs/' + last_log + '.log', 'a') as log:
        log.write(entry + '\n')


def kill():
    sys.exit()


def in_raw(prompt, no_log=False):
    user_input = input(prompt)

    if not no_log:
        entry = str(str(datetime.datetime.now()) + ' ' + prompt + user_input)
        write_to_last_log(entry)

    return user_input


def in_input(prompt, no_log=False):
    return in_raw('INPUT: ' + str(prompt) + ': ', no_log=no_log)


def out_raw(*args, log_level=-1, no_log=False, sep=' ', **kwargs):
    if log_level <= get_log_level():
        print(*args, sep=sep, **kwargs)

        if not no_log:
            entry = str(datetime.datetime.now()) + ' ' + sep.join(list(str(arg) for arg in args))
            write_to_last_log(entry)


def out_debug(*args, **kwargs):
    out_raw('DEBUG:', *args, log_level=4, **kwargs)


def out_info(*args, **kwargs):
    out_raw('INFO:', *args, log_level=3, **kwargs)


def out_warning(*args, **kwargs):
    out_raw('WARNING:', *args, log_level=2, **kwargs)


def out_error(*args, **kwargs):
    out_raw('ERROR:', *args, log_level=1, **kwargs)


def out_exception(exception):
    try:
        out_error(exception.message)
    except AttributeError:
        out_error(exception)


def out_fatal(*args, **kwargs):
    out_raw('FATAL:', *args, log_level=0, **kwargs)


def get_out_function(level):
    if level in ('0', 'fatal'):
        return out_fatal
    elif level in ('1', 'error'):
        return out_error
    elif level in ('2', 'warning'):
        return out_warning
    elif level in ('3', 'info'):
        return out_info
    elif level in ('4', 'debug'):
        return out_debug
    elif level in ('raw',):
        return out_raw


class ProgressBar:
    def __init__(self, total_steps, sigfig=2):
        self.start_time = datetime.datetime.now()
        self.current_time = datetime.datetime.now()
        self.last_print_length = 0
        self.sigfig = sigfig
        self.current_step = 0
        self.total_steps = total_steps

    def increment(self):
        self.current_step += 1
        return self

    def set_step(self, step):
        self.current_step = step
        return self

    def terminate(self):
        self.current_step = self.total_steps
        return self

    def print_progress(self, out_level='raw', no_log=True):
        out_function = get_out_function(out_level)
        self.current_time = datetime.datetime.now()
        bar = '|' + '█' * int(50 * self.current_step // self.total_steps) + '-' * (50 - int(50 * self.current_step // self.total_steps)) + '|'
        progress = str(utilities.intsigfig(100 * self.current_step / self.total_steps, self.sigfig)) + '%'

        if self.start_time is None or self.current_time is None or self.start_time == self.current_time:
            progress_bar = 'Progress: ' + bar + ' ' + progress
            out_function(progress_bar + ' ' * max(0, self.last_print_length - len(progress_bar)), end='\r', no_log=no_log)
            print_length = max(self.last_print_length, len(progress_bar))
        else:
            elapsed_time = utilities.format_time(int(round((self.current_time - self.start_time).total_seconds())))
            remaining_time = utilities.format_time(int(round((self.total_steps - self.current_step) * (self.current_time - self.start_time).total_seconds() / self.current_step)))
            progress_bar = 'Progress: ' + bar + ' ' + progress + '   Elapsed: ' + elapsed_time + '   Remaining: ' + remaining_time
            out_function(progress_bar + ' ' * max(0, self.last_print_length - len(progress_bar)), end='\r', no_log=no_log)
            print_length = max(self.last_print_length, len(progress_bar))

        if self.current_step == self.total_steps:
            out_function(no_log=True)

        self.last_print_length = print_length
        return self

    def increment_print(self, out_level='raw'):
        return self.increment().print_progress(out_level=out_level, no_log=True)

    def terminate_print(self, out_level='raw'):
        return self.terminate().print_progress(out_level=out_level, no_log=False)
