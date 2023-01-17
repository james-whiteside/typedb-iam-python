import math
from typedb.client import SessionType, TransactionType, TypeDBOptions
from typedb.common.exception import TypeDBClientException
import src.polynomial as polynomial
import src.io_controller as io_controller
from src.io_controller import ProgressBar
import src.db_connector as db_connector


def unpack_result(result):
    output = list()

    for item in result:
        output.append(item.map())

    return output


def decode_result(result):
    output = list()

    for item in result:
        item_dict = dict()

        for key in item.map():
            concept = item.get(key)

            if not concept.is_attribute():
                continue

            item_dict[key] = concept.get_value()

        output.append(item_dict)

    return output


def get_databases(client):
    return client.databases().all()


def create_database(client, database):
    try:
        return client.databases().create(name=database)
    except TypeDBClientException as exception:
        io_controller.out_exception(exception)
        return


def database_exists(client, database):
    return client.databases().contains(name=database)


def delete_database(client, database):
    try:
        return client.databases().get(name=database).delete()
    except TypeDBClientException as exception:
        io_controller.out_exception(exception)
        return


def define(client, database, queries, display_progress=False):
    with client.session(database=database, session_type=SessionType.SCHEMA) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                    transaction.query().define(query=query)
                    transaction.commit()

                progress_bar.increment()


def undefine(client, database, queries, display_progress=False):
    with client.session(database=database, session_type=SessionType.SCHEMA) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                    transaction.query().undefine(query=query)
                    transaction.commit()

                progress_bar.increment()


def match(client, database, queries, display_progress=False):
    options = TypeDBOptions.core().set_infer(db_connector.get_rule_inference())
    results = list()

    with client.session(database=database, session_type=SessionType.DATA, options=options) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.READ) as transaction:
                    result = transaction.query().match(query=query)
                    results.append(unpack_result(result))

                progress_bar.increment()

    return results


def get(client, database, queries, display_progress=False):
    results = list()
    options = TypeDBOptions.core().set_infer(db_connector.get_rule_inference())

    with client.session(database=database, session_type=SessionType.DATA, options=options) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.READ) as transaction:
                    result = transaction.query().match(query=query)
                    results.append(decode_result(result))

                progress_bar.increment()

    return results


def insert(client, database, queries, display_progress=False):
    with client.session(database=database, session_type=SessionType.DATA) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                    transaction.query().insert(query=query)
                    transaction.commit()

                progress_bar.increment()


def update(client, database, queries, display_progress=False):
    with client.session(database=database, session_type=SessionType.DATA) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                    transaction.query().update(query=query)
                    transaction.commit()

                progress_bar.increment()


def delete(client, database, queries, display_progress=False):
    with client.session(database=database, session_type=SessionType.DATA) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                    transaction.query().delete(query=query)
                    transaction.commit()

                progress_bar.increment()


def group(client, database, queries, display_progress=False):
    options = TypeDBOptions.core().set_infer(db_connector.get_rule_inference())
    results = list()

    with client.session(database=database, session_type=SessionType.DATA, options=options) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.READ) as transaction:
                    result = transaction.query().match_group(query=query)
                    results.append(decode_result(result))

                progress_bar.increment()

    return results


def aggregate(client, database, queries, display_progress=False):
    options = TypeDBOptions.core().set_infer(db_connector.get_rule_inference())
    results = list()

    with client.session(database=database, session_type=SessionType.DATA, options=options) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.READ) as transaction:
                    result = transaction.query().match_aggregate(query=query)
                    results.append(decode_result(result))

                progress_bar.increment()

    return results


def group_aggregate(client, database, queries, display_progress=False):
    options = TypeDBOptions.core().set_infer(db_connector.get_rule_inference())
    results = list()

    with client.session(database=database, session_type=SessionType.DATA, options=options) as session:
        with ProgressBar(len(queries), locked=not display_progress) as progress_bar:
            for query in queries:
                with session.transaction(transaction_type=TransactionType.READ) as transaction:
                    result = transaction.query().match_group_aggregate(query=query)
                    output = list()
    
                    for item in result:
                        output.append(item.numeric().as_int())
    
                    results.append(output)

                progress_bar.increment()

    return results


def count_types(client, database, supertype='thing'):
    if supertype == 'thing':
        modifier = -4
    elif supertype in ('entity', 'relation', 'attribute'):
        modifier = -1
    else:
        modifier = 0

    queries = [
        'match $t sub ' + supertype + ';'
    ]

    try:
        results = match(client, database, queries)
    except TypeDBClientException as exception:
        io_controller.out_exception(exception)
        return

    return len(list(results[0])) + modifier


def count_things(client, database, thing_type='thing'):
    queries = [
        'match $t isa ' + thing_type + ';'
    ]

    results = match(client, database, queries)
    return len(list(results[0]))


def count_players(client, database):
    queries = [
        'match $r($t);'
    ]

    results = match(client, database, queries)
    return len(list(results[0]))


def count_owners(client, database):
    queries = [
        'match $t has $a;'
    ]

    results = match(client, database, queries)
    return len(list(results[0]))


def schema_exists(client, database):
    return count_types(client, database) != 0


def data_exists(client, database):
    return count_things(client, database) != 0


def get_barabasi_albert_fit(client, database):
    # Determines the goodness-of-fit of the Barabási–Albert model for the database graph.
    # Returns the graph scale parameter and the coefficient of determination R² for that parameter.
    # It should be noted that R² is not the best measure of goodness-of-fit for log-log graphs.

    queries = [
        ' '.join([
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
    ]

    vertex_degrees = group_aggregate(client, database, queries)[0]
    histogram = dict()

    for degree in vertex_degrees:
        try:
            histogram[degree] += 1
        except KeyError:
            histogram[degree] = 1

    things = count_things(client, database)
    log_k = list(math.log10(k) for k in sorted(histogram))
    log_P = list(math.log10(histogram[k] / things) for k in sorted(histogram))
    poly = polynomial.lin_reg(log_k, log_P)
    log_f = list(polynomial.poly_point(poly, x) for x in log_k)
    R2 = polynomial.coef_det(log_P, log_f)
    scale_parameter = -poly[1]
    return scale_parameter, R2


def get_graph_statistics(client, database):
    # Approximates statistics for the database by assuming it is a Barabási–Albert graph.
    # DOI: 10.1126/science.286.5439.509
    # DOI: 10.48550/arXiv.cond-mat/0407098

    vertices = count_things(client, database)
    edges = count_players(client, database) + count_owners(client, database)
    average_vertex_degree = 2 * edges / vertices
    scale_parameter, coefficient_of_determination = get_barabasi_albert_fit(client, database)
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
