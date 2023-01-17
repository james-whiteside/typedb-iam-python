import json
import datetime
import calendar
import string
import uuid
import copy
import os
from random import Random
import src.utilities as utilities
import src.io_controller as io_controller
from src.io_controller import ProgressBar


def generate_uuid():
    return str(uuid.uuid4())


def generate_letter(rng=Random()):
    return rng.choice(string.ascii_lowercase)


def generate_letters(length, prevent_banned_strings=True, rng=Random()):
    letters = ''.join(generate_letter(rng=rng) for _ in range(length))

    if prevent_banned_strings:
        with open('generator_tables/banned_strings.tsv', 'r') as file:
            banned_strings = file.read().split('\n')

        if any(banned_string in letters for banned_string in banned_strings):
            return generate_letters(length, rng=rng)

    return letters


def generate_date(past_years=10, year=None, month=None, day=None, rng=Random()):
    date = datetime.date.today()
    date -= datetime.timedelta(days=rng.randint(0, past_years * 365))

    if year is not None:
        date = date.replace(year=year)

    if month is not None:
        date = date.replace(month=month)

    if day is not None:
        if day < 0:
            date = date.replace(day=calendar.monthrange(date.year, date.month)[1] + day + 1)
        else:
            date = date.replace(day=day)

    return str(date)


def load_name(name_type, rng=Random()):
    # Name lists taken from: https://github.com/treyhunner/names/
    # Licensed under the MIT License.

    r = rng.uniform(0.0, 90.0)

    with open('generator_tables/' + name_type + '_names.tsv') as file:
        for line in file:
            name, weight, cumulative, rank = line.split('\t')

            if float(cumulative) > r:
                return name


def generate_name(name_type='full', case='title', rng=Random()):
    if name_type == 'male':
        name = load_name('male', rng=rng)
    elif name_type == 'female':
        name = load_name('female', rng=rng)
    elif name_type == 'first':
        gender = rng.choice(('male', 'female'))
        name = load_name(gender, rng=rng)
    elif name_type == 'last':
        name = load_name('last', rng=rng)
    elif name_type == 'full':
        gender = rng.choice(('male', 'female'))
        name = load_name(gender, rng=rng) + ' ' + load_name('last', rng=rng)
    else:
        name = ''

    if case == 'title':
        name = name.title()
    elif case == 'lower':
        name = name.lower()
    elif case == 'upper':
        name = name.upper()

    return name


def generate_resolution(rng=Random()):
    return str(rng.randint(1, 4) * 360) + 'x' + str(rng.randint(1, 4) * 360)


def construct_string(constructor, rng=Random()):
    # Generates a string from a constructor string.
    # A constructor string is formed of any number of parts separated by the '&' character.
    # A constructor part consists either of a raw string, or a generator command.
    # Generator commands are of the form: <command|arg1:val1|arg2:val2|...>
    # The command specifies the generator function to use, which parses the arg-val pairs as kwargs.
    # Each generator returns a string, and each part's string is concatenated to produce the final output.
    # The following are reserved characters: & < > | :
    # Example: constructor="<name>&'s date of birth is &<date|past_years:50>&."

    output = ''

    for part in constructor.split('&'):
        if part[0] == '<' and part[-1] == '>':
            args = part[1:-1].split('|')
            command = args.pop(0)
            kwargs = {arg.split(':')[0]: utilities.cast_string(arg.split(':')[1]) for arg in args}

            if command == 'uuid':
                generator = generate_uuid
            elif command == 'letter':
                generator = generate_letter
                kwargs['rng'] = rng
            elif command == 'letters':
                generator = generate_letters
                kwargs['rng'] = rng
            elif command == 'date':
                generator = generate_date
                kwargs['rng'] = rng
            elif command == 'name':
                generator = generate_name
                kwargs['rng'] = rng
            elif command == 'resolution':
                generator = generate_resolution
                kwargs['rng'] = rng
            else:
                output += part
                continue
            
            output += generator(**kwargs)
        else:
            output += part

    return output


def load_user_groups(group_type='user_group', get_abstract_groups=True):
    with open('generator_tables/user_groups.json', 'r') as file:
        user_groups = json.load(file)

    user_groups = list(group for group in user_groups if group_type in group['type'])

    if not get_abstract_groups:
        user_groups = list(group for group in user_groups if not group['is_abstract'])

    return user_groups


def generate_business_units(rng=Random()):
    units = load_user_groups('business_unit', get_abstract_groups=False)
    return list(unit['name'] for unit in [rng.choice(units)])


def generate_user_roles(rng=Random()):
    roles = load_user_groups('user_role', get_abstract_groups=False)
    return list(role['name'] for role in roles if rng.random() < 0.15)


def generate_user_accounts(rng=Random()):
    accounts = load_user_groups('user_account', get_abstract_groups=False)
    return list(account['name'] for account in accounts if rng.random() < 0.15)


def generate_user(name=None, rng=Random()):
    if name is None:
        name = generate_name(rng=rng)

    user = {
        'name': name,
        'type': ['subject', 'user', 'person'],
        'email': '.'.join(name.lower() for name in name.split(' ')) + '@vaticle.com',
        'business_unit': generate_business_units(rng=rng),
        'user_role': generate_user_roles(rng=rng),
        'user_account': generate_user_accounts(rng=rng),
        'uuid': generate_uuid()
    }

    return user


def generate_users(count, rng=Random()):
    names = set()
    io_controller.out_info('Generating', count, 'names:')

    with ProgressBar(count) as progress_bar:
        while len(names) < count:
            names.add(generate_name(rng=rng))
            progress_bar.set_step(len(names))

    users = list()
    io_controller.out_info('Generating', count, 'users:')

    with ProgressBar(count) as progress_bar:
        for name in sorted(list(names)):
            users.append(generate_user(name, rng=rng))
            progress_bar.increment()

    return users


def get_user_groups():
    user_groups = load_user_groups()

    for group in user_groups:
        group['uuid'] = generate_uuid()

    for parent_group in user_groups:
        member_ids = list()

        for child_group in user_groups:
            if sorted(child_group['type']) == sorted(parent_group['type']) and child_group['name'] in parent_group['member']:
                member_ids.append(child_group['uuid'])

        parent_group['member'] = member_ids

    return user_groups


def generate_subjects(user_count, rng=Random()):
    users = generate_users(user_count, rng=rng)
    user_groups = get_user_groups()
    io_controller.out_info('Assigning', len(users), 'users to', len(user_groups), 'groups:')

    with ProgressBar(len(user_groups) * len(users)) as progress_bar:
        for group in user_groups:
            for user in users:
                if group['name'] in user['business_unit'] + user['user_role'] + user['user_account']:
                    group['member'].append(user['uuid'])

                progress_bar.increment()

    return users + user_groups


def load_resource_collections(collection_type='resource_collection', get_abstract_collections=True):
    with open('generator_tables/resource_collections.json', 'r') as file:
        resource_collections = json.load(file)

    resource_collections = list(collection for collection in resource_collections if collection_type in collection['type'])

    if not get_abstract_collections:
        resource_collections = list(collection for collection in resource_collections if not collection['is_abstract'])

    return resource_collections


def generate_directory(rng=Random()):
    collections = load_resource_collections('directory', get_abstract_collections=False)
    return rng.choice(collections)


def generate_resource(rng=Random()):
    directory = generate_directory(rng=rng)

    resource = {
        'name': construct_string(directory['resource_format'], rng=rng),
        'type': ['object', 'resource', 'file'],
        'parent': [directory['name']],
        'parent_type': 'directory',
        'uuid': generate_uuid()
    }

    return resource


def generate_resources(count, rng=Random()):
    resources = list()
    io_controller.out_info('Generating', count, 'resources:')

    with ProgressBar(count) as progress_bar:
        while len(resources) < count:
            resource = generate_resource(rng=rng)
            resources.append(resource)
            progress_bar.increment()

    return resources


def get_resource_collections():
    resource_collections = load_resource_collections()

    for collection in resource_collections:
        collection['uuid'] = generate_uuid()

    for parent_collection in resource_collections:
        member_ids = list()

        for child_collection in resource_collections:
            if sorted(child_collection['type']) == sorted(parent_collection['type']) and child_collection['name'] in parent_collection['member']:
                member_ids.append(child_collection['uuid'])

        parent_collection['member'] = member_ids

    return resource_collections


def generate_objects(resource_count, rng=Random()):
    resources = generate_resources(resource_count, rng=rng)
    resource_collections = get_resource_collections()
    io_controller.out_info('Assigning', len(resources), 'resources to', len(resource_collections), 'collections:')

    with ProgressBar(len(resources) * len(resource_collections)) as progress_bar:
        for collection in resource_collections:
            for resource in resources:
                if resource['parent_type'] in collection['type'] and collection['name'] in resource['parent']:
                    collection['member'].append(resource['uuid'])

                progress_bar.increment()

    return resources + resource_collections


def load_operations(object_type=None):
    with open('generator_tables/operations.json', 'r') as file:
        operations = json.load(file)

    if object_type is not None:
        operations = list(operation for operation in operations if object_type in operation['object_type'])

    return operations


def load_operation_sets(object_type=None):
    with open('generator_tables/operation_sets.json', 'r') as file:
        operation_sets = json.load(file)

    if object_type is not None:
        operation_sets = list(opset for opset in operation_sets if object_type in opset['object_type'])

    return operation_sets


def get_actions():
    operations = load_operations()
    operation_sets = load_operation_sets()

    for operation in operations:
        operation['uuid'] = generate_uuid()

    for opset in operation_sets:
        opset['uuid'] = generate_uuid()

    for parent_set in operation_sets:
        member_ids = list()

        for operation in operations:
            if any(object_type in operation['object_type'] for object_type in parent_set['object_type']) and operation['name'] in parent_set['member']:
                member_ids.append(operation['uuid'])

        for child_set in operation_sets:
            if any(object_type in child_set['object_type'] for object_type in parent_set['object_type']) and child_set['name'] in parent_set['member']:
                member_ids.append(child_set['uuid'])

        parent_set['member'] = member_ids

    return operations + operation_sets


def load_permissions(subject_type=None, object_type=None):
    with open('generator_tables/permissions.json', 'r') as file:
        permissions = json.load(file)

    if subject_type is not None:
        permissions = list(permission for permission in permissions if subject_type == permission['subject_type'])

    if object_type is not None:
        permissions = list(permission for permission in permissions if object_type == permission['object_type'])

    return permissions


def get_permissions(subjects, objects, actions):
    permissions = load_permissions()
    
    for permission in permissions:
        subject_ids = list()
        object_ids = list()
        action_ids = list()
        
        for subject in subjects:
            if permission['subject_type'] in subject['type'] and subject['name'] in permission['subject']:
                subject_ids.append(subject['uuid'])

        for obj in objects:
            if permission['object_type'] in obj['type'] and obj['name'] in permission['object']:
                object_ids.append(obj['uuid'])

        for action in actions:
            if permission['object_type'] in action['object_type'] and action['name'] in permission['action']:
                action_ids.append(action['uuid'])

        permission['subject'] = subject_ids
        permission['object'] = object_ids
        permission['action'] = action_ids

    return permissions


def get_member_uuids(uuid, item_list):
    for item in item_list:
        try:
            if item['uuid'] == uuid:
                return item['member']
        except KeyError:
            continue

    return list()


def get_nested_member_uuids(uuid, item_list):
    uuids = list()

    for member_uuid in get_member_uuids(uuid, item_list):
        uuids.append(member_uuid)
        uuids += get_nested_member_uuids(member_uuid, item_list)

    return uuids


def get_membership_uuids(uuid, item_list):
    uuids = list()

    for item in item_list:
        try:
            if uuid in item['member']:
                uuids.append(item['uuid'])
        except KeyError:
            continue

    return uuids


def get_nested_membership_uuids(uuid, item_list):
    uuids = list()

    for membership_uuid in get_membership_uuids(uuid, item_list):
        uuids.append(membership_uuid)
        uuids += get_nested_membership_uuids(membership_uuid, item_list)

    return uuids


def get_items(uuids, item_list):
    items = list()

    for item in item_list:
        try:
            if item['uuid'] in uuids:
                items.append(item)
        except KeyError:
            continue

    return items


def get_nested_members(item, item_list):
    member_uuids = get_nested_member_uuids(item['uuid'], item_list)
    return get_items(member_uuids, item_list)


def get_nested_memberships(item, item_list):
    membership_uuids = get_nested_membership_uuids(item['uuid'], item_list)
    return get_items(membership_uuids, item_list)


def assign_group_owner(user_group, item_list, rng=Random()):
    users = list(item for item in item_list if 'user' in item['type'])
    members = get_nested_members(user_group, item_list)
    candidate_owner_uuids = list()

    for member in members:
        if member in users:
            candidate_owner_uuids.append(member['uuid'])

    user_group['owner'] = [rng.choice(candidate_owner_uuids)]


def assign_group_owners(item_list, rng=Random()):
    user_groups = list(item for item in item_list if 'user_group' in item['type'])
    io_controller.out_info('Assigning owners for', len(user_groups), 'groups:')

    with ProgressBar(len(user_groups)) as progress_bar:
        for user_group in user_groups:
            assign_group_owner(user_group, item_list, rng=rng)
            progress_bar.increment()


def assign_object_owner(obj, item_list, rng=Random()):
    permissions = list(item for item in item_list if 'permission' in item['type'])
    membership_uuids = get_nested_membership_uuids(obj['uuid'], item_list) + [obj['uuid']]
    subject_uuids = list()

    for permission in permissions:
        if any(uuid in permission['object'] for uuid in membership_uuids):
            subject_uuids += permission['subject']

    candidate_owner_uuids = list()
    candidate_owner_uuids += subject_uuids

    for uuid in subject_uuids:
        candidate_owner_uuids += get_nested_member_uuids(uuid, item_list)

    obj['owner'] = [rng.choice(candidate_owner_uuids)]


def assign_object_owners(item_list, rng=Random()):
    objects = list(item for item in item_list if 'object' in item['type'])
    io_controller.out_info('Assigning owners for', len(objects), 'objects:')

    with ProgressBar(len(objects)) as progress_bar:
        for obj in objects:
            assign_object_owner(obj, item_list, rng=rng)
            progress_bar.increment()


def assign_owner_permissions(item_list):
    objects = list(item for item in item_list if 'object' in item['type'])
    actions = list(item for item in item_list if 'action' in item['type'])

    owner_permissions_template = [
        {
            'type': ['permission'],
            'subject': list(),
            'subject_type': 'subject',
            'object': list(),
            'object_type': 'object',
            'action': ['manage_ownership']
        }
    ]

    for permission in owner_permissions_template:
        permission_actions = list()

        for action in actions:
            if action['name'] in permission['action']:
                permission_actions.append(action['uuid'])

        permission['action'] = permission_actions

    io_controller.out_info('Assigning owner permissions for', len(objects), 'objects:')

    with ProgressBar(len(objects)) as progress_bar:
        for obj in objects:
            owner_permissions = copy.deepcopy(owner_permissions_template)

            for permission in owner_permissions:
                permission['object'].append(obj['uuid'])
                permission['subject'] += obj['owner']

                item_list.append(permission)

            progress_bar.increment()


def generate_data():
    params = utilities.get_config_params('config.ini', 'data_generation')
    user_count = int(params['user_count'])
    resource_count = int(params['resource_count'])

    io_controller.out_info('Generating data...')

    try:
        rng_seed = int(params['rng_seed'])
        rng = Random(rng_seed)
        io_controller.out_debug('Using seed:', rng_seed)
    except (KeyError, ValueError):
        rng = Random()
        io_controller.out_debug('Using random seed.')

    subjects = generate_subjects(user_count, rng=rng)
    objects = generate_objects(resource_count, rng=rng)
    actions = get_actions()
    permissions = get_permissions(subjects, objects, actions)
    items = subjects + objects + actions + permissions
    assign_group_owners(items, rng=rng)
    assign_object_owners(items, rng=rng)
    assign_owner_permissions(items)
    io_controller.out_info('Data generation complete.')

    data = {
        'user': list(item for item in items if 'user' in item['type']),
        'user_group': list(item for item in items if 'user_group' in item['type']),
        'resource': list(item for item in items if 'resource' in item['type']),
        'resource_collection': list(item for item in items if 'resource_collection' in item['type']),
        'operation': list(item for item in items if 'operation' in item['type']),
        'operation_set': list(item for item in items if 'operation_set' in item['type']),
        'permission': list(item for item in items if 'permission' in item['type'])
    }

    return data


def get_last_auto_save_number():
    if not os.path.exists('data'):
        return 0

    file_names = os.listdir('data')
    auto_save_numbers = [0]

    for name in file_names:
        prefix, _, suffix = name.partition('_')

        if prefix == 'auto' and suffix != '' and all(char in string.digits for char in suffix):
            auto_save_numbers.append(int(suffix))

    return sorted(auto_save_numbers)[-1]


def save_data(data):
    if not os.path.exists('data'):
        os.makedirs('data')

    params = utilities.get_config_params('config.ini', 'data_storage')

    try:
        dataset_name = params['dataset_name']
    except KeyError:
        dataset_name = ''

    if dataset_name == '':
        dataset_name = 'auto_' + str(get_last_auto_save_number() + 1)

    dataset_path = 'data/' + dataset_name

    try:
        os.makedirs(dataset_path)
    except FileExistsError:
        io_controller.out_warning('A dataset with the name', dataset_name, 'already exists.')

        if io_controller.in_input('Overwrite the previous dataset? (Y/N)').lower() == 'y':
            io_controller.out_warning('Overwriting previous dataset.')
        else:
            io_controller.out_warning('Dataset save aborted.')
            return

    for key in data:
        file_path = dataset_path + '/' + key + '.json'

        with open(file_path, 'w') as file:
            json.dump(data[key], file, indent=2)

        io_controller.out_debug(key, 'data saved to', file_path)


def load_data():
    params = utilities.get_config_params('config.ini', 'data_storage')

    try:
        dataset_name = params['dataset_name']
    except KeyError:
        dataset_name = ''

    if dataset_name == '':
        dataset_name = 'auto_' + str(get_last_auto_save_number())

    dataset_path = 'data/' + dataset_name
    data = dict()

    try:
        for file_name in os.listdir(dataset_path):
            key = file_name.rpartition('.')[0]
            file_path = dataset_path + '/' + file_name

            with open(file_path, 'r') as file:
                data[key] = json.load(file)

            io_controller.out_debug(key, 'data loaded from', file_path)

        return data
    except FileNotFoundError:
        io_controller.out_error('No dataset with the name', dataset_name, 'was found.')
        io_controller.out_error('Data should be stored under:', os.getcwd() + '/data')
        return
