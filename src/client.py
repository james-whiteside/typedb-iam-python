import src.db_operations as db_operations
import src.data_loaders as data_loaders


def run_client():
    db_operations.check_connection()
    db_operations.create_database()
    db_operations.define_schema()
    data_loaders.load_data()
