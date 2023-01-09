import src.io_controller as io_controller
import src.db_connector as db_connector
from typedb.client import SessionType, TransactionType
from typedb.common.exception import TypeDBClientException


def get_databases():
    with db_connector.client() as client:
        return client.databases().all()


def create_database(database):
    with db_connector.client() as client:
        try:
            return client.databases().create(name=database)
        except TypeDBClientException as exception:
            io_controller.out_exception(exception)
            return


def database_exists(database):
    with db_connector.client() as client:
        return client.databases().contains(name=database)


def delete_database(database):
    with db_connector.client() as client:
        try:
            return client.databases().get(name=database).delete()
        except TypeDBClientException as exception:
            io_controller.out_exception(exception)
            return


def define(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.SCHEMA) as session:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().define(query=query)
                transaction.commit()


def undefine(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.SCHEMA) as session:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().undefine(query=query)
                transaction.commit()


def get(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                transaction.query().match(query=query)


def insert(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().insert(query=query)
                transaction.commit()


def update(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().update(query=query)
                transaction.commit()


def delete(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().delete(query=query)
                transaction.commit()
