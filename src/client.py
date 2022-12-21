import src.db_operations as db_operations
import src.generators as generators
import src.utilities as utilities


def run_client():
    db_operations.check_connection()
    users = generators.generate_users(100)
    user_groups = generators.get_user_groups(users)
    resources = generators.generate_resources(100)
    resource_collections = generators.get_resource_collections(resources)
    operations = generators.get_operations('directory')
    operation_sets = generators.get_operation_sets(operations)

    for item in operation_sets:
        print(item)
