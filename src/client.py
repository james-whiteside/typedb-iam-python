import src.db_operations as db_operations
import src.generators as generators


def run_client():
    db_operations.check_connection()
    data = generators.generate_data(100, 100)
