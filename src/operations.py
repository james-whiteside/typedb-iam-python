from typedb.common.exception import TypeDBClientException
import src.db_controller as db_controller


def check_connection():
    try:
        db_controller.get_databases()
        return True
    except TypeDBClientException:
        return False
