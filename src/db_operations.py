from typedb.common.exception import TypeDBClientException
import src.io_controller as io_controller
import src.db_controller as db_controller


def check_connection():
    try:
        db_controller.get_databases()
        io_controller.out_info('Connection established.')
    except TypeDBClientException:
        io_controller.out_fatal('Could not establish connection to database server.')
        io_controller.out_fatal('Server is not running or client is improperly configured.')
        io_controller.kill()
