import json
import random
import datetime
import calendar
import uuid
import names as name_generator
import src.utilities as utilities


def generate_uuid():
    return str(uuid.uuid4())


def generate_letter():
    return random.choice('abcdefghijklmnopqrstuvwxyz')


def generate_letters(length, prevent_banned_strings=True):
    letters = ''.join(generate_letter() for i in range(length))

    if prevent_banned_strings:
        with open('generator_data/banned_strings.tsv', 'r') as file:
            banned_strings = file.read().split('\n')

        if any(banned_string in letters for banned_string in banned_strings):
            return generate_letters(length)

    return letters


def generate_date(past_years=10, year=None, month=None, day=None):
    date = datetime.date.today()
    date -= datetime.timedelta(days=random.randint(0, past_years * 365))

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


def generate_name(sep=' ', lower=False):
    name = sep.join(name_generator.get_full_name().split(' '))

    if lower:
        name = name.lower()

    return name


def generate_resolution():
    return str(random.randint(1, 4) * 360) + 'x' + str(random.randint(1, 4) * 360)


def construct_string(constructor):
    string = ''

    for part in constructor.split('&'):
        if part[0] == '<' and part[-1] == '>':
            args = part[1:-1].split('|')
            command = args.pop(0)

            if command == 'uuid':
                generator = generate_uuid
            elif command == 'letter':
                generator = generate_letter
            elif command == 'letters':
                generator = generate_letters
            elif command == 'date':
                generator = generate_date
            elif command == 'name':
                generator = generate_name
            elif command == 'resolution':
                generator = generate_resolution
            else:
                string += part
                continue

            kwargs = {arg.split(':')[0]: utilities.cast_string(arg.split(':')[1]) for arg in args}
            string += generator(**kwargs)
        else:
            string += part

    return string


def load_user_groups(group_type=None, get_abstract_groups=True):
    with open('generator_data/user_groups.json', 'r') as file:
        user_groups = json.load(file)

    if group_type is not None:
        user_groups = list(group for group in user_groups if group['type'] == group_type)

    if not get_abstract_groups:
        user_groups = list(group for group in user_groups if not group['is_abstract'])

    return user_groups


def generate_business_units():
    units = load_user_groups('business_unit', get_abstract_groups=False)
    return list(unit['name'] for unit in [random.choice(units)])


def generate_user_roles():
    roles = load_user_groups('user_role', get_abstract_groups=False)
    return list(role['name'] for role in roles if random.random() < 0.15)


def generate_user_accounts():
    accounts = load_user_groups('user_account', get_abstract_groups=False)
    return list(account['name'] for account in accounts if random.random() < 0.15)


def generate_user(full_name=None):
    if full_name is None:
        full_name = generate_name()

    user = {
        'first_name': full_name.split(' ')[0],
        'last_name': full_name.split(' ')[1],
        'email': '.'.join(name.lower() for name in full_name.split(' ')) + '@vaticle.com',
        'business_unit': generate_business_units(),
        'user_role': generate_user_roles(),
        'user_account': generate_user_accounts(),
        'uuid': generate_uuid()
    }

    return user


def generate_users(count):
    full_names = set()

    while len(full_names) < count:
        full_names.add(generate_name())

    users = list()

    for full_name in full_names:
        users.append(generate_user(full_name))

    return users


def get_user_groups():
    user_groups = load_user_groups()

    for group in user_groups:
        group['uuid'] = generate_uuid()

    for parent_group in user_groups:
        member = list()

        for child_group in user_groups:
            if child_group['name'] in parent_group['member']:
                member.append(child_group['uuid'])

        parent_group['member'] = member

    return user_groups


def generate_subjects(count):
    users = generate_users(count)
    user_groups = get_user_groups()

    for group in user_groups:
        for user in users:
            if group['name'] in user['business_unit'] + user['user_role'] + user['user_account']:
                group['member'].append(user['uuid'])

    return users, user_groups


def load_resource_collections(collection_type=None, get_abstract_collections=True):
    with open('generator_data/resource_collections.json', 'r') as file:
        resource_collections = json.load(file)

    if collection_type is not None:
        resource_collections = list(collection for collection in resource_collections if collection['type'] == collection_type)

    if not get_abstract_collections:
        resource_collections = list(collection for collection in resource_collections if not collection['is_abstract'])

    return resource_collections


def generate_directory():
    collections = load_resource_collections('directory', get_abstract_collections=False)
    return random.choice(collections)


def generate_resource():
    directory = generate_directory()

    resource = {
        'name': construct_string(directory['resource_format']),
        'directory': [directory['name']],
        'uuid': generate_uuid()
    }

    return resource


def generate_resources(count):
    resources = list()

    while len(resources) < count:
        resource = generate_resource()
        resources.append(resource)

    return resources


def get_resource_collections():
    resource_collections = load_resource_collections()

    for collection in resource_collections:
        collection['uuid'] = generate_uuid()

    for parent_collection in resource_collections:
        member = list()

        for child_collection in resource_collections:
            if child_collection['name'] in parent_collection['member']:
                member.append(child_collection['uuid'])

        parent_collection['member'] = member

    return resource_collections


def generate_objects(count):
    resources = generate_resources(count)
    resource_collections = get_resource_collections()

    for collection in resource_collections:
        for resource in resources:
            if collection['name'] in resource['directory']:
                collection['member'].append(resource['uuid'])

    return resources, resource_collections


def get_operations(object_type=None):
    if object_type == 'application':
        operations = [
            {
                'name': 'grant_ownership',
                'object': 'application',
                'parent': ['perform_admin_actions'],
                'uuid': generate_uuid()
            },
            {
                'name': 'grant_permissions',
                'object': 'application',
                'parent': ['perform_admin_actions'],
                'uuid': generate_uuid()
            },
            {
                'name': 'view_user_accounts',
                'object': 'application',
                'parent': ['perform_reads'],
                'uuid': generate_uuid()
            },
            {
                'name': 'create_user_accounts',
                'object': 'application',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'modify_user_accounts',
                'object': 'application',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'delete_user_accounts',
                'object': 'application',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'view_user_contact_details',
                'object': 'application',
                'parent': ['perform_reads'],
                'uuid': generate_uuid()
            },
            {
                'name': 'set_user_account_roles',
                'object': 'application',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'reset_user_account_passwords',
                'object': 'application',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'suspend_user_accounts',
                'object': 'application',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            }
        ]

    elif object_type == 'directory':
        operations = [
            {
                'name': 'grant_ownership',
                'object': 'directory',
                'parent': ['perform_admin_actions'],
                'uuid': generate_uuid()
            },
            {
                'name': 'grant_permissions',
                'object': 'directory',
                'parent': ['perform_admin_actions'],
                'uuid': generate_uuid()
            },
            {
                'name': 'view_files',
                'object': 'directory',
                'parent': ['perform_reads'],
                'uuid': generate_uuid()
            },
            {
                'name': 'create_files',
                'object': 'directory',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'modify_files',
                'object': 'directory',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'delete_files',
                'object': 'directory',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'create_subdirectories',
                'object': 'directory',
                'parent': ['manage_subdirectories'],
                'uuid': generate_uuid()
            },
            {
                'name': 'delete_subdirectories',
                'object': 'directory',
                'parent': ['manage_subdirectories'],
                'uuid': generate_uuid()
            }
        ]

    elif object_type == 'dataset':
        operations = [
            {
                'name': 'grant_ownership',
                'object': 'dataset',
                'parent': ['perform_admin_actions'],
                'uuid': generate_uuid()
            },
            {
                'name': 'grant_permissions',
                'object': 'dataset',
                'parent': ['perform_admin_actions'],
                'uuid': generate_uuid()
            },
            {
                'name': 'read_records',
                'object': 'dataset',
                'parent': ['perform_reads'],
                'uuid': generate_uuid()
            },
            {
                'name': 'create_records',
                'object': 'dataset',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'update_records',
                'object': 'dataset',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'delete_records',
                'object': 'dataset',
                'parent': ['perform_writes'],
                'uuid': generate_uuid()
            },
            {
                'name': 'create_tables',
                'object': 'dataset',
                'parent': ['manage_tables'],
                'uuid': generate_uuid()
            },
            {
                'name': 'drop_tables',
                'object': 'dataset',
                'parent': ['manage_tables'],
                'uuid': generate_uuid()
            }
        ]

    else:
        operations = []

    return operations


def get_operation_sets(operations):
    operation_set_objectnames = set()

    for operation in operations:
        for parent in operation['parent']:
            operation_set_objectnames.add(operation['object'] + '|' + parent)
    
    operation_sets = list()
    
    for objectname in operation_set_objectnames:
        obj = objectname.split('|')[0]
        name = objectname.split('|')[1]
        operation_set = dict()
        operation_set['name'] = name
        operation_set['object'] = obj
        operation_set['member'] = list()
        
        for operation in operations:
            if operation['object'] == obj and name in operation['parent']:
                operation_set['member'].append(operation['uuid'])

        operation_set['uuid'] = generate_uuid()
        operation_sets.append(operation_set)

        for parent_set in operation_sets:
            for child_set in operation_sets:
                if parent_set['object'] != child_set['object']:
                    continue

                if parent_set['name'] == 'perform_writes' and child_set['name'] == 'perform_reads':
                    parent_set['member'].append(child_set['uuid'])
                elif parent_set['name'] == 'manage_subdirectories' and child_set['name'] == 'perform_writes':
                    parent_set['member'].append(child_set['uuid'])
                elif parent_set['name'] == 'manage_tables' and child_set['name'] == 'perform_writes':
                    parent_set['member'].append(child_set['uuid'])
                elif parent_set['name'] == 'perform_admin_actions' and child_set['name'] in ('perform_writes', 'manage_subdirectories', 'manage_tables'):
                    parent_set['member'].append(child_set['uuid'])

    return operation_sets
