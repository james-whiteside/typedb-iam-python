import datetime
import os
import sys
import src.utilities as utilities


def get_output_level(level_type):
    try:
        log_arg = utilities.get_config_params('config.ini', 'io_control')[level_type + '_level']
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

    with open('logs/' + log_name + '.log', 'a'):
        pass


def write_to_last_log(entry):
    try:
        last_log = sorted(os.listdir('logs'))[-1]
    except FileNotFoundError or IndexError:
        create_log()
        last_log = sorted(os.listdir('logs'))[-1]

    with open('logs/' + last_log, 'a') as log:
        log.write(entry + '\n')


def in_raw(prompt, no_log=False):
    user_input = input(prompt)

    if not no_log:
        entry = str(str(datetime.datetime.now()) + ' ' + prompt + user_input)
        write_to_last_log(entry)

    return user_input


def in_input(prompt, no_log=False):
    return in_raw('INPUT: ' + str(prompt) + ': ', no_log=no_log)


def out_raw(*args, log_level=-1, no_log=False, sep=' ', **kwargs):
    if log_level <= get_output_level(level_type='display'):
        print(*args, sep=sep, **kwargs)

    if log_level <= get_output_level(level_type='logging') and not no_log:
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


def kill():
    out_debug('io_controller.kill() was called')
    sys.exit()


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
    def __init__(self, total_steps, out_level='info', sigfig=2):
        self.current_step = 0
        self.total_steps = total_steps
        self.start_time = datetime.datetime.now()
        self.current_time = self.start_time
        self.out_level = out_level
        self.sigfig = sigfig
        self.last_print_length = 0
        self.locked = False

    def get_progress(self):
        return self.current_step, self.total_steps

    def __output_progress(self, no_log=True):
        if not self.locked:
            out_function = get_out_function(self.out_level)
            bar = '|' + '█' * int(50 * self.current_step // self.total_steps) + '-' * (50 - int(50 * self.current_step // self.total_steps)) + '|'
            progress = str(utilities.intsigfig(100 * self.current_step / self.total_steps, self.sigfig)) + '%'

            if self.current_step == 0 or self.start_time == self.current_time:
                progress_bar = 'Progress: ' + bar + ' ' + progress
                out_function(progress_bar + ' ' * max(0, self.last_print_length - len(progress_bar)), end='\r', no_log=no_log)
                print_length = max(self.last_print_length, len(progress_bar))
            else:
                elapsed_time = utilities.format_time(int(round((self.current_time - self.start_time).total_seconds())))
                remaining_time = utilities.format_time(int(round((self.total_steps - self.current_step) * (self.current_time - self.start_time).total_seconds() / self.current_step)))
                progress_bar = 'Progress: ' + bar + ' ' + progress + '   Elapsed: ' + elapsed_time + '   Remaining: ' + remaining_time
                out_function(progress_bar + ' ' * max(0, self.last_print_length - len(progress_bar)), end='\r', no_log=no_log)
                print_length = max(self.last_print_length, len(progress_bar))

            self.current_time = datetime.datetime.now()
            self.last_print_length = print_length
            return True
        else:
            return False

    def __output_newline(self):
        if not self.locked:
            out_function = get_out_function(self.out_level)
            out_function(no_log=True)
            return True
        else:
            return False

    def lock(self):
        self.__output_progress(no_log=False)
        self.__output_newline()
        self.locked = True
        return self

    def terminate(self):
        self.current_step = self.total_steps
        self.lock()
        return self

    def __terminate_if_full(self):
        if self.current_step >= self.total_steps:
            self.terminate()
            return True
        else:
            return False

    def increment(self):
        self.current_step += 1
        self.__terminate_if_full()
        self.__output_progress()
        return self

    def set_step(self, step):
        self.current_step = step
        self.__terminate_if_full()
        self.__output_progress()
        return self

    def __enter__(self):
        self.__output_progress()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock()
