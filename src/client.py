import src.operations as operations
import src.generators as generators


def run_client():
    operations.check_connection()
    users = generators.generate_users(100)
    resources = generators.generate_resources(100)

    for resource in resources:
        print(resource)
