import src.io_controller as io_controller
from src.io_controller import ProgressBar
import src.db_connector as db_connector
import src.db_controller as db_controller
import src.data_builder as data_builder


def load_users():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    users = data['user']
    io_controller.out_info('Loading', len(users), 'users:')

    with ProgressBar(len(users)) as progress_bar:
        for user in users:
            name = user['name']
            email = user['email']
            query = 'insert $p isa person, has name "' + name + '", has email "' + email + '";'
            db_controller.insert(query, database)
            progress_bar.increment()


def load_user_groups():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    users = data['user']
    user_groups = data['user_group']
    subjects = users + user_groups
    group_membership_count = 0
    group_ownership_count = 0
    io_controller.out_info('Loading', len(user_groups), 'user groups:')

    with ProgressBar(len(user_groups)) as progress_bar:
        for group in user_groups:
            name = group['name']
            group_types = group['type']
            group_membership_count += len(group['member'])
            group_ownership_count += len(group['owner'])

            if 'business_unit' in group_types:
                group_type = 'business-unit'
            elif 'user_role' in group_types:
                group_type = 'user-role'
            elif 'user_account' in group_types:
                group_type = 'user-account'

            query = 'insert $g isa ' + group_type + ', has name "' + name + '";'
            db_controller.insert(query, database)
            progress_bar.increment()

    io_controller.out_info('Loading', group_membership_count, 'group memberships:')

    with ProgressBar(len(user_groups)) as progress_bar:
        for group in user_groups:
            group_name = group['name']

            for subject in subjects:
                if subject['uuid'] in group['member']:
                    member_name = subject['name']

                    query = ' '.join([
                        'match',
                        '$g isa user-group, has name "' + group_name + '";',
                        '$s isa subject, has name "' + member_name + '";',
                        'insert',
                        '$m (user-group: $g, group-member: $s) isa group-membership;'
                    ])

                    db_controller.insert(query, database)

            progress_bar.increment()

    io_controller.out_info('Loading', group_ownership_count, 'group ownerships:')

    with ProgressBar(len(user_groups)) as progress_bar:
        for group in user_groups:
            group_name = group['name']

            for subject in subjects:
                if subject['uuid'] in group['owner']:
                    owner_name = subject['name']

                    query = ' '.join([
                        'match',
                        '$g isa user-group, has name "' + group_name + '";',
                        '$s isa subject, has name "' + owner_name + '";',
                        'insert',
                        '$o (owned-group: $g, group-owner: $s) isa group-ownership;'
                    ])

                    db_controller.insert(query, database)

            progress_bar.increment()


def load_subjects():
    load_users()
    load_user_groups()


def load_resources():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    resources = data['resource']
    subjects = data['user'] + data['user_group']
    resource_ownership_count = 0
    io_controller.out_info('Loading', len(resources), 'resources:')
    
    with ProgressBar(len(resources)) as progress_bar:
        for resource in resources:
            name = resource['name']
            resource_ownership_count += len(resource['owner'])
            query = 'insert $f isa file, has name "' + name + '";'
            db_controller.insert(query, database)
            progress_bar.increment()
    
    io_controller.out_info('Loading', resource_ownership_count, 'resource ownerships:')
    
    with ProgressBar(len(resources)) as progress_bar:
        for resource in resources:
            resource_name = resource['name']
            
            for subject in subjects:
                if subject['uuid'] in resource['owner']:
                    owner_name = subject['name']
                    
                    query = ' '.join([
                        'match',
                        '$r isa resource, has name "' + resource_name + '";',
                        '$s isa subject, has name "' + owner_name + '";',
                        'insert',
                        '$o (owned-object: $r, object-owner: $s) isa object-ownership;'
                    ])
                    
                    db_controller.insert(query, database)
            
            progress_bar.increment()


def load_resource_collections():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    resources = data['resource']
    resource_collections = data['resource_collection']
    objects = resources + resource_collections
    subjects = data['user'] + data['user_group']
    collection_membership_count = 0
    collection_ownership_count = 0
    io_controller.out_info('Loading', len(resource_collections), 'resource collections:')
    
    with ProgressBar(len(resource_collections)) as progress_bar:
        for collection in resource_collections:
            name = collection['name']
            collection_membership_count += len(collection['member'])
            collection_ownership_count += len(collection['owner'])
            query = 'insert $d isa directory, has name "' + name + '";'
            db_controller.insert(query, database)
            progress_bar.increment()

    io_controller.out_info('Loading', collection_membership_count, 'collection memberships:')

    with ProgressBar(len(resource_collections)) as progress_bar:
        for collection in resource_collections:
            collection_name = collection['name']

            for obj in objects:
                if obj['uuid'] in collection['member']:
                    member_name = obj['name']

                    query = ' '.join([
                        'match',
                        '$c isa resource-collection, has name "' + collection_name + '";',
                        '$o isa object, has name "' + member_name + '";',
                        'insert',
                        '$m (resource-collection: $c, collection-member: $o) isa collection-membership;'
                    ])

                    db_controller.insert(query, database)

            progress_bar.increment()

    io_controller.out_info('Loading', collection_ownership_count, 'collection ownerships:')

    with ProgressBar(len(resource_collections)) as progress_bar:
        for collection in resource_collections:
            collection_name = collection['name']

            for subject in subjects:
                if subject['uuid'] in collection['owner']:
                    owner_name = subject['name']

                    query = ' '.join([
                        'match',
                        '$c isa resource-collection, has name "' + collection_name + '";',
                        '$s isa subject, has name "' + owner_name + '";',
                        'insert',
                        '$o (owned-object: $c, object-owner: $s) isa object-ownership;'
                    ])

                    db_controller.insert(query, database)

            progress_bar.increment()


def load_objects():
    load_resources()
    load_resource_collections()


def load_operations():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    operations = data['operation']
    objects = data['resource'] + data['resource_collection']
    io_controller.out_info('Loading', len(operations), 'operations:')

    with ProgressBar(len(operations)) as progress_bar:
        for operation in operations:
            name = operation['name']
            query = 'insert $o isa operation, has name "' + name + '";'
            db_controller.insert(query, database)
            progress_bar.increment()

    io_controller.out_info('Loading up to', len(operations) * len(objects), 'potential accesses:')

    with ProgressBar(len(operations)) as progress_bar:
        for operation in operations:
            operation_name = operation['name']
            object_type = operation['object_type']

            for obj in objects:
                if object_type in obj['type']:
                    object_name = obj['name']

                    query = ' '.join([
                        'match',
                        '$ob isa ' + object_type.replace('_', '-') + ', has name "' + object_name + '";',
                        '$op isa operation, has name "' + operation_name + '";',
                        'insert',
                        '$a (accessed-object: $ob, valid-action: $op) isa access;'
                    ])

            progress_bar.increment()


def load_operation_sets():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    operations = data['operation']
    operation_sets = data['operation_set']
    actions = operations + operation_sets
    objects = data['resource'] + data['resource_collection']
    set_membership_count = 0
    io_controller.out_info('Loading', len(operation_sets), 'operation sets:')

    with ProgressBar(len(operation_sets)) as progress_bar:
        for opset in operation_sets:
            name = opset['name']
            set_membership_count += len(opset['member'])
            query = 'insert $s isa operation-set, has name "' + name + '";'
            db_controller.insert(query, database)
            progress_bar.increment()

    io_controller.out_info('Loading', set_membership_count, 'set memberships:')

    with ProgressBar(len(operation_sets)) as progress_bar:
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

                    db_controller.insert(query, database)

            progress_bar.increment()

    io_controller.out_info('Loading up to', len(operation_sets) * len(objects), 'potential accesses:')

    with ProgressBar(len(operation_sets)) as progress_bar:
        for opset in operation_sets:
            set_name = opset['name']
            object_type = opset['object_type']

            for obj in objects:
                if object_type in obj['type']:
                    object_name = obj['name']

                    query = ' '.join([
                        'match',
                        '$o isa object, has name "' + object_name + '";',
                        '$s isa operation-set, has name "' + set_name + '";',
                        'insert',
                        '$a (accessed-object: $o, valid-action: $s) isa access;'
                    ])

                    db_controller.insert(query, database)

            progress_bar.increment()


def load_actions():
    load_operations()
    load_operation_sets()


def load_permissions():
    database = db_connector.get_database_name()
    data = data_builder.load_data()
    permissions = data['permission']
    subjects = data['user'] + data['user_group']
    objects = data['resource'] + data['resource_collection']
    actions = data['operation'] + data['operation_set']
    io_controller.out_info('Loading', len(permissions), 'permissions:')

    with ProgressBar(len(permissions)) as progress_bar:
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

                                    query = ' '.join([
                                        'match',
                                        '$s isa ' + subject_type.replace('_', '-') + ', has name "' + subject_name + '";',
                                        '$o isa ' + object_type.replace('_', '-') + ', has name "' + object_name + '";',
                                        '$a isa action, has name "' + action_name + '";',
                                        '$ac (accessed-object: $o, valid-action: $a) isa access;',
                                        'insert',
                                        '$p (permitted-subject: $s, permitted-access: $ac) isa permission;'
                                    ])

                                    db_controller.insert(query, database)

            progress_bar.increment()


def load_data():
    load_subjects()
    load_objects()
    load_actions()
    load_permissions()
