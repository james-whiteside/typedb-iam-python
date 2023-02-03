import src.io_controller as io_controller
import src.data_operations as data_operations
import src.typedb_iam.db_controller as db_controller
import src.typedb_iam.db_operations as db_operations

io_controller.create_log()

with db_controller.client() as client:
    data_operations.generate_new_dataset()
    db_operations.ensure_server_connection(client)
    db_operations.rebuild_database(client)
    # db_operations.provide_graph_statistics(client)
    # db_operations.run_test_queries(client)
    db_operations.run_prove_query_test(client)
