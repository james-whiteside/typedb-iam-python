import src.io_controller as io_controller
import src.data_builder as data_builder
import src.db_operations as db_operations


io_controller.create_log()
db_operations.ensure_connection()
db_operations.rebuild_database()
db_operations.provide_graph_statistics()
db_operations.run_test_queries()
