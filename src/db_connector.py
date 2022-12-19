from typedb.client import TypeDB


def client():
    return TypeDB.core_client(address=TypeDB.DEFAULT_ADDRESS)
