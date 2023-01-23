import src.io_controller as io_controller
import src.postgres_iam.db_controller as db_controller
import src.postgres_iam.db_operations as db_operations

io_controller.create_log()

with db_controller.client() as client:
    db_operations.ensure_server_connection(client)
    db_operations.rebuild_database(client)
