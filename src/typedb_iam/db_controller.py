import math
import itertools
import copy
from typedb.client import TypeDB, TransactionType
from typedb.common.exception import TypeDBClientException
from typedb.logic.rule import _Rule
import src.polynomial as polynomial
import src.io_controller as io_controller
from src.io_controller import ProgressBar


def client():
    return TypeDB.core_client(address=TypeDB.DEFAULT_ADDRESS)


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


def define(session, queries, display_progress=False):
    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().define(query=query)
                transaction.commit()

            progress_bar.increment()


def undefine(session, queries, display_progress=False):
    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().undefine(query=query)
                transaction.commit()

            progress_bar.increment()


def match(session, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                result = transaction.query().match(query=query)
                results.append(unpack_result(result))

            progress_bar.increment()

    return results


def get_proofs(transaction, concept_map):
    explainables = dict()
    explainables.update(concept_map.explainables().relations())
    explainables.update(concept_map.explainables().attributes())
    explainables.update(concept_map.explainables().ownerships())

    for explainable in copy.copy(explainables):
        if not concept_map.get(explainable).is_inferred():
            del explainables[explainable]

    base_facts = set(concept for concept in concept_map.concepts() if not concept.is_inferred())

    if len(explainables) == 0:
        return [base_facts]

    proofs_of_explainables = list()

    for explainable in explainables.values():  # AND (cartesian product)
        explanations = transaction.query().explain(explainable)
        proofs_of_explainable = list()

        for explanation in explanations:  # OR (union)
            rule = explanation.rule()
            condition = explanation.condition()
            proofs_of_condition = get_proofs(transaction, condition)

            for proof_of_condition in proofs_of_condition:
                proof_of_explainable = proof_of_condition | {rule}
                proofs_of_explainable.append(proof_of_explainable)

        proofs_of_explainables.append(proofs_of_explainable)

    proofs_of_concept_map = list()

    for proof_set in itertools.product(*proofs_of_explainables):
        proof_of_concept_map = set.union(*proof_set) | base_facts
        proofs_of_concept_map.append(proof_of_concept_map)

    proofs_of_concept_map = set(frozenset(proof) for proof in proofs_of_concept_map)

    for reference_proof in copy.copy(proofs_of_concept_map):
        for test_proof in copy.copy(proofs_of_concept_map):
            if reference_proof < test_proof:
                try:
                    proofs_of_concept_map.remove(test_proof)
                except ValueError:
                    pass

    proofs_of_concept_map = list(set(proof) for proof in proofs_of_concept_map)

    return proofs_of_concept_map


def decode_proofs(transaction, proofs):
    outputs = list()

    for proof in proofs:
        output = list()
        type_counts = dict()
        bindings = dict()

        for item in proof:
            if type(item) is _Rule:
                continue
            else:
                item_type = str(item.get_type().get_label())

                if item_type not in type_counts:
                    type_counts[item_type] = 1
                else:
                    type_counts[item_type] += 1

                if item.is_attribute():
                    attribute_value = item.get_value()

                    if type(attribute_value) is str:
                        attribute_value = '"' + str(attribute_value) + '"'
                    else:
                        attribute_value = str(attribute_value)

                    binding = attribute_value
                else:
                    binding = '$' + item_type + '-' + str(type_counts[item_type])

                bindings[item] = binding

        for item in proof:
            if type(item) is _Rule:
                output.append('rule: ' + str(item.get_label()))
            elif item.is_entity():
                attributes = list(item.as_remote(transaction).get_has())
                entity_binding = bindings[item]
                entity_type = str(item.get_type().get_label())
                entity_attributes = str()

                for attribute in attributes:
                    try:
                        entity_attributes += ', has ' + str(attribute.get_type().get_label()) + ' ' + bindings[attribute]
                    except KeyError:
                        continue

                output.append(entity_binding + ' ' + 'isa' + ' ' + entity_type + entity_attributes + ';')

            elif item.is_relation():
                roles = item.as_remote(transaction).get_players_by_role_type()
                attributes = list(item.as_remote(transaction).get_has())
                relation_binding = bindings[item]
                relation_type = str(item.get_type().get_label())
                relation_roleplayers = list()
                relation_attributes = str()

                for role in roles:
                    for roleplayer in roles[role]:
                        try:
                            relation_roleplayer = str(role.get_label()).split(':')[1] + ': ' + bindings[roleplayer]
                            relation_roleplayers.append(relation_roleplayer)
                        except KeyError:
                            continue

                for attribute in attributes:
                    try:
                        relation_attributes += ', has attribute ' + bindings[attribute]
                    except KeyError:
                        continue

                output.append(relation_binding + ' (' + ', '.join(relation_roleplayers) + ') isa ' + relation_type + ';')

            elif item.is_attribute():
                continue
            else:
                io_controller.out_error('Thing is not an entity, relation, or attribute.')

        output.sort()
        outputs.append(output)

    return outputs


def prove(session, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                result = transaction.query().match(query=query)
                result_proofs = list()

                for concept_map in result:
                    proofs = get_proofs(transaction, concept_map)
                    result_proofs.append(decode_proofs(transaction, proofs))

                results.append(result_proofs)

            progress_bar.increment()

    return results


def get(session, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                result = transaction.query().match(query=query)
                results.append(decode_result(result))

            progress_bar.increment()

    return results


def insert(session, queries, display_progress=False):
    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().insert(query=query)
                transaction.commit()

            progress_bar.increment()


def update(session, queries, display_progress=False):
    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().update(query=query)
                transaction.commit()

            progress_bar.increment()


def delete(session, queries, display_progress=False):
    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.WRITE) as transaction:
                transaction.query().delete(query=query)
                transaction.commit()

            progress_bar.increment()


def group(session, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                result = transaction.query().match_group(query=query)
                results.append(decode_result(result))

            progress_bar.increment()

    return results


def aggregate(session, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                result = transaction.query().match_aggregate(query=query)
                results.append(decode_result(result))

            progress_bar.increment()

    return results


def group_aggregate(session, queries, display_progress=False):
    results = list()

    with ProgressBar(len(queries), display=display_progress) as progress_bar:
        for query in queries:
            with session.transaction(transaction_type=TransactionType.READ) as transaction:
                result = transaction.query().match_group_aggregate(query=query)
                output = list()

                for item in result:
                    output.append(item.numeric().as_int())

                results.append(output)

            progress_bar.increment()

    return results


def count_types(session, supertype='thing'):
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
        results = match(session, queries)
    except TypeDBClientException as exception:
        io_controller.out_exception(exception)
        return

    return len(list(results[0])) + modifier


def count_things(session, thing_type='thing'):
    queries = [
        'match $t isa ' + thing_type + ';'
    ]

    results = match(session, queries)
    return len(list(results[0]))


def count_players(session):
    queries = [
        'match $r($t);'
    ]

    results = match(session, queries)
    return len(list(results[0]))


def count_owners(session):
    queries = [
        'match $t has $a;'
    ]

    results = match(session, queries)
    return len(list(results[0]))


def schema_exists(session):
    return count_types(session) != 0


def data_exists(session):
    return count_things(session) != 0


def get_barabasi_albert_fit(session):
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

    vertex_degrees = group_aggregate(session, queries)[0]
    histogram = dict()

    for degree in vertex_degrees:
        try:
            histogram[degree] += 1
        except KeyError:
            histogram[degree] = 1

    things = count_things(session)
    log_k = list(math.log10(k) for k in sorted(histogram))
    log_P = list(math.log10(histogram[k] / things) for k in sorted(histogram))
    poly = polynomial.lin_reg(log_k, log_P)
    log_f = list(polynomial.poly_point(poly, x) for x in log_k)
    R2 = polynomial.coef_det(log_P, log_f)
    scale_parameter = -poly[1]
    return scale_parameter, R2


def get_graph_statistics(session):
    # Approximates statistics for the database by assuming it is a Barabási–Albert graph.
    # DOI: 10.1126/science.286.5439.509
    # DOI: 10.48550/arXiv.cond-mat/0407098

    vertices = count_things(session)
    edges = count_players(session) + count_owners(session)
    average_vertex_degree = 2 * edges / vertices
    scale_parameter, coefficient_of_determination = get_barabasi_albert_fit(session)
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
