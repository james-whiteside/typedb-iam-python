import src.io_controller as io_controller
import src.db_controller as db_controller
import src.operations as operations

io_controller.create_log()

with db_controller.client() as client:
    operations.generate_new_dataset()
    operations.ensure_server_connection(client)
    operations.rebuild_database(client)
    # operations.provide_graph_statistics(client)
    operations.run_test_queries(client)
