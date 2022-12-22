import src.db_operations as db_operations
import src.generators as generators
import src.utilities as utilities


def run_client():
    db_operations.check_connection()
    users, user_groups = generators.generate_subjects(100)
    resources, resource_collections = generators.generate_objects(100)
    operations = generators.get_operations('directory')
    operation_sets = generators.get_operation_sets(operations)

    for item in user_groups:
        print(item)
