import math
import src.polynomial as polynomial
import src.io_controller as io_controller
import src.db_connector as db_connector
from typedb.client import SessionType, TransactionType
from typedb.common.exception import TypeDBClientException


def unpack_results(results):
    output = list()

    for result in results:
        output.append(result.map())

    return output


def decode_results(results):
    output = list()

    for result in results:
        item = dict()

        for key in result.map():
            concept = result.get(key)

            if not concept.is_attribute():
                continue

            item[key] = concept.get_value()

        output.append(item)

    return output


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


def match(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                results = transaction.query().match(query=query)
                return unpack_results(results)


def get(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                results = transaction.query().match(query=query)
                return decode_results(results)


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


def group(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                results = transaction.query().match_group(query=query)
                return decode_results(results)


def aggregate(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                results = transaction.query().match_aggregate(query=query)
                return decode_results(results)


def group_aggregate(query, database):
    with db_connector.client() as client:
        with client.session(database=database, session_type=SessionType.DATA) as session:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                results = transaction.query().match_group_aggregate(query=query)
                output = list()

                for result in results:
                    output.append(result.numeric().as_int())

                return output


def count_types(database, supertype='thing'):
    if supertype == 'thing':
        modifier = -4
    elif supertype in ('entity', 'relation', 'attribute'):
        modifier = -1
    else:
        modifier = 0

    query = 'match $t sub ' + supertype + ';'

    try:
        results = match(query, database)
    except TypeDBClientException as exception:
        io_controller.out_exception(exception)
        return

    return len(list(results)) + modifier


def count_things(database, thing_type='thing'):
    query = 'match $t isa ' + thing_type + ';'
    results = match(query, database)
    return len(list(results))


def count_players(database):
    query = 'match $r($t);'
    results = match(query, database)
    return len(list(results))


def count_owners(database):
    query = 'match $t has $a;'
    results = match(query, database)
    return len(list(results))


def schema_exists(database):
    return count_types(database) != 0


def data_exists(database):
    return count_things(database) != 0


def get_barabasi_albert_fit(database):
    # Determines the goodness-of-fit of the Barabási–Albert model for the database graph.
    # Returns the graph scale parameter and the coefficient of determination R² for that parameter.
    # It should be noted that R² is not the best measure of goodness-of-fit for log-log graphs.

    query = ' '.join([
        'match',
        '$t isa thing;',
        '$x isa thing;',
        '{ $x($t); } or',
        '{ $t($x); } or',
        '{ $t has $x; } or',
        '{ $x has $t; };',
        'get $t, $x;',
        'group $t;',
        'count;'
    ])

    vertex_degrees = group_aggregate(query, database)
    histogram = dict()

    for degree in vertex_degrees:
        try:
            histogram[degree] += 1
        except KeyError:
            histogram[degree] = 1

    things = count_things(database)
    log_k = list(math.log10(k) for k in sorted(histogram))
    log_P = list(math.log10(histogram[k] / things) for k in sorted(histogram))
    poly = polynomial.lin_reg(log_k, log_P)
    log_f = list(polynomial.poly_point(poly, x) for x in log_k)
    R2 = polynomial.coef_det(log_P, log_f)
    scale_parameter = -poly[1]
    return scale_parameter, R2


def get_graph_statistics(database):
    # Approximates statistics for the database by assuming it is a Barabási–Albert graph.
    # DOI: 10.1126/science.286.5439.509
    # DOI: 10.48550/arXiv.cond-mat/0407098

    vertices = count_things(database)
    edges = count_players(database) + count_owners(database)
    average_vertex_degree = 2 * edges / vertices
    scale_parameter, coefficient_of_determination = get_barabasi_albert_fit(database)
    network_age = (vertices + math.sqrt(vertices ** 2 - 4 * edges)) / 2
    growth_factor = (vertices - math.sqrt(vertices ** 2 - 4 * edges)) / 2
    euler_constant = 0.5772156649
    numerator = math.log(vertices) - math.log(0.5 * growth_factor) - 1 - euler_constant
    denominator = math.log(math.log(vertices)) + math.log(0.5 * growth_factor)
    average_path_length = numerator / denominator + 1.5

    statistics = {
        'vertices': vertices,
        'edges': edges,
        'average_vertex_degree': average_vertex_degree,
        'scale_parameter': scale_parameter,
        'coefficient_of_determination': coefficient_of_determination,
        'network_age': network_age,
        'growth_factor': growth_factor,
        'average_path_length': average_path_length
    }

    return statistics
