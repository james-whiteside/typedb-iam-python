import src.io_controller as io_controller
import src.db_connector as db_connector
import src.operations as operations

io_controller.create_log()

with db_connector.client() as client:
    operations.generate_new_dataset()
    operations.ensure_server_connection(client)
    operations.rebuild_database(client)
    # operations.provide_graph_statistics(client)
    operations.run_test_queries(client)
