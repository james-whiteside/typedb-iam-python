import src.db_connector as db_connector


def get_databases():
    with db_connector.client() as client:
        return client.databases().all()
