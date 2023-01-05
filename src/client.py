import src.db_operations as db_operations
import src.io_controller as io_controller


def run_client():
    db_operations.check_connection()
