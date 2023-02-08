import src.io_controller as io_controller
import src.typedb_iam.db_controller as db_controller
import src.data_generation as data_generation


def load_users(session):
    data = data_generation.load_data()
    users = data['user']
    queries = list()

    for user in users:
        name = user['name']
        email = user['email']
        query = 'insert $p isa person, has name "' + name + '", has email "' + email + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(users), 'users:')
    db_controller.insert(session, queries, display_progress=True)


def load_user_groups(session):
    data = data_generation.load_data()
    users = data['user']
    user_groups = data['user_group']
    subjects = users + user_groups
    group_membership_count = 0
    group_ownership_count = 0
    queries = list()

    for group in user_groups:
        name = group['name']
        group_types = group['type']
        group_membership_count += len(group['member'])
        group_ownership_count += len(group['owner'])

        if 'business_unit' in group_types:
            group_type = 'business-unit'
            identifier_type = 'name'
        elif 'user_role' in group_types:
            group_type = 'user-role'
            identifier_type = 'name'
        elif 'user_account' in group_types:
            group_type = 'user-account'
            identifier_type = 'email'
        else:
            io_controller.out_fatal('Invalid group types:', group_types)
            io_controller.kill()

        query = 'insert $g isa ' + group_type + ', has ' + identifier_type + ' "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(user_groups), 'user groups:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for group in user_groups:
        group_name = group['name']

        if 'user_account' in group['type']:
            group_identifier = 'email'
        else:
            group_identifier = 'name'

        for subject in subjects:
            if subject['uuid'] in group['member']:
                member_name = subject['name']

                if 'user_account' in subject['type']:
                    subject_identifier = 'email'
                else:
                    subject_identifier = 'name'

                query = ' '.join([
                    'match',
                    '$g isa user-group, has ' + group_identifier + ' "' + group_name + '";',
                    '$s isa subject, has ' + subject_identifier + ' "' + member_name + '";',
                    'insert',
                    '$m (user-group: $g, group-member: $s) isa group-membership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', group_membership_count, 'group memberships:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for group in user_groups:
        group_name = group['name']

        if 'user_account' in group['type']:
            group_identifier = 'email'
        else:
            group_identifier = 'name'


        for subject in subjects:
            if subject['uuid'] in group['owner']:
                owner_name = subject['name']

                if 'user_account' in subject['type']:
                    owner_identifier = 'email'
                else:
                    owner_identifier = 'name'

                query = ' '.join([
                    'match',
                    '$g isa user-group, has ' + group_identifier + ' "' + group_name + '";',
                    '$s isa subject, has ' + owner_identifier + ' "' + owner_name + '";',
                    'insert',
                    '$o (owned-group: $g, group-owner: $s) isa group-ownership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', group_ownership_count, 'group ownerships:')
    db_controller.insert(session, queries, display_progress=True)


def load_subjects(session):
    load_users(session)
    load_user_groups(session)


def load_resources(session):
    data = data_generation.load_data()
    resources = data['resource']
    subjects = data['user'] + data['user_group']
    resource_ownership_count = 0
    queries = list()

    for resource in resources:
        name = resource['name']
        resource_ownership_count += len(resource['owner'])
        query = 'insert $f isa file, has filepath "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(resources), 'resources:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for resource in resources:
        resource_name = resource['name']

        for subject in subjects:
            if subject['uuid'] in resource['owner']:
                owner_name = subject['name']

                if 'user_account' in subject['type']:
                    owner_identifier = 'email'
                else:
                    owner_identifier = 'name'

                query = ' '.join([
                    'match',
                    '$r isa resource, has filepath "' + resource_name + '";',
                    '$s isa subject, has ' + owner_identifier + ' "' + owner_name + '";',
                    'insert',
                    '$o (owned-object: $r, object-owner: $s) isa object-ownership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', resource_ownership_count, 'resource ownerships:')
    db_controller.insert(session, queries, display_progress=True)


def load_resource_collections(session):
    data = data_generation.load_data()
    resources = data['resource']
    resource_collections = data['resource_collection']
    objects = resources + resource_collections
    subjects = data['user'] + data['user_group']
    collection_membership_count = 0
    collection_ownership_count = 0
    queries = list()

    for collection in resource_collections:
        name = collection['name']
        collection_membership_count += len(collection['member'])
        collection_ownership_count += len(collection['owner'])
        query = 'insert $d isa directory, has filepath "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(resource_collections), 'resource collections:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for collection in resource_collections:
        collection_name = collection['name']

        for obj in objects:
            if obj['uuid'] in collection['member']:
                member_name = obj['name']

                query = ' '.join([
                    'match',
                    '$c isa resource-collection, has filepath "' + collection_name + '";',
                    '$o isa object, has filepath "' + member_name + '";',
                    'insert',
                    '$m (resource-collection: $c, collection-member: $o) isa collection-membership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', collection_membership_count, 'collection memberships:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for collection in resource_collections:
        collection_name = collection['name']

        for subject in subjects:
            if subject['uuid'] in collection['owner']:
                owner_name = subject['name']

                if 'user_account' in subject['type']:
                    owner_identifier = 'email'
                else:
                    owner_identifier = 'name'

                query = ' '.join([
                    'match',
                    '$c isa resource-collection, has filepath "' + collection_name + '";',
                    '$s isa subject, has ' + owner_identifier + ' "' + owner_name + '";',
                    'insert',
                    '$o (owned-object: $c, object-owner: $s) isa object-ownership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', collection_ownership_count, 'collection ownerships:')
    db_controller.insert(session, queries, display_progress=True)


def load_objects(session):
    load_resources(session)
    load_resource_collections(session)


def load_operations(session):
    data = data_generation.load_data()
    operations = data['operation']
    objects = data['resource'] + data['resource_collection']
    queries = list()

    for operation in operations:
        name = operation['name']
        query = 'insert $o isa operation, has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(operations), 'operations:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for operation in operations:
        operation_name = operation['name']

        for obj in objects:
            object_types = list(object_type for object_type in obj['type'] if object_type in operation['object_type'])

            if len(object_types) != 0:
                object_name = obj['name']
                object_type = object_types[0]

                query = ' '.join([
                    'match',
                    '$ob isa ' + object_type.replace('_', '-') + ', has filepath "' + object_name + '";',
                    '$op isa operation, has name "' + operation_name + '";',
                    'insert',
                    '$a (accessed-object: $ob, valid-action: $op) isa access;'
                ])

                queries.append(query)

    io_controller.out_info('Loading up to', len(operations) * len(objects), 'potential accesses:')
    db_controller.insert(session, queries, display_progress=True)


def load_operation_sets(session):
    data = data_generation.load_data()
    operations = data['operation']
    operation_sets = data['operation_set']
    actions = operations + operation_sets
    objects = data['resource'] + data['resource_collection']
    set_membership_count = 0
    queries = list()

    for opset in operation_sets:
        name = opset['name']
        set_membership_count += len(opset['member'])
        query = 'insert $s isa operation-set, has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(operation_sets), 'operation sets:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for opset in operation_sets:
        set_name = opset['name']

        for action in actions:
            if action['uuid'] in opset['member']:
                member_name = action['name']

                query = ' '.join([
                    'match',
                    '$s isa operation-set, has name "' + set_name + '";',
                    '$a isa action, has name "' + member_name + '";',
                    'insert'
                    '$m (operation-set: $s, set-member: $a) isa set-membership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', set_membership_count, 'set memberships:')
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for opset in operation_sets:
        set_name = opset['name']

        for obj in objects:
            object_types = list(object_type for object_type in obj['type'] if object_type in opset['object_type'])

            if len(object_types) != 0:
                object_name = obj['name']
                object_type = object_types[0]

                query = ' '.join([
                    'match',
                    '$o isa ' + object_type.replace('_', '-') + ', has filepath "' + object_name + '";',
                    '$s isa operation-set, has name "' + set_name + '";',
                    'insert',
                    '$a (accessed-object: $o, valid-action: $s) isa access;'
                ])

                queries.append(query)

    io_controller.out_info('Loading up to', len(operation_sets) * len(objects), 'potential accesses:')
    db_controller.insert(session, queries, display_progress=True)


def load_actions(session):
    load_operations(session)
    load_operation_sets(session)


def load_permissions(session):
    data = data_generation.load_data()
    permissions = data['permission']
    subjects = data['user'] + data['user_group']
    objects = data['resource'] + data['resource_collection']
    actions = data['operation'] + data['operation_set']
    queries = list()

    for permission in permissions:
        subject_type = permission['subject_type']
        object_type = permission['object_type']

        for subject in subjects:
            if subject['uuid'] in permission['subject']:
                for obj in objects:
                    if obj['uuid'] in permission['object']:
                        for action in actions:
                            if action['uuid'] in permission['action']:
                                subject_name = subject['name']
                                object_name = obj['name']
                                action_name = action['name']

                                if 'user_account' in subject['type']:
                                    identifier_type = 'email'
                                else:
                                    identifier_type = 'name'

                                query = ' '.join([
                                    'match',
                                    '$s isa ' + subject_type.replace('_', '-') + ', has ' + identifier_type + ' "' + subject_name + '";',
                                    '$o isa ' + object_type.replace('_', '-') + ', has filepath "' + object_name + '";',
                                    '$a isa action, has name "' + action_name + '";',
                                    '$ac (accessed-object: $o, valid-action: $a) isa access;',
                                    'insert',
                                    '$p (permitted-subject: $s, permitted-access: $ac) isa permission;'
                                ])

                                queries.append(query)

    io_controller.out_info('Loading', len(permissions), 'permissions:')
    db_controller.insert(session, queries, display_progress=True)


def load_data(session):
    load_subjects(session)
    load_objects(session)
    load_actions(session)
    load_permissions(session)
