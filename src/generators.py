import json
import random
import datetime
import calendar
import uuid
import copy
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
    # Generates a string from a constructor string.
    # A constructor string is formed of any number of parts separated by the '&' character.
    # A constructor part consists either of a raw string, or a generator command.
    # Generator commands are of the form: <command|arg1:val1|arg2:val2|...>
    # The command specifies the generator function to use, which parses the arg-val pairs as kwargs.
    # Each generator returns a string, and each part's string is concatenated to produce the final output.
    # The following are reserved characters: & < > | :
    # Example: constructor="<name>&'s date of birth is &<date|past_years:50>&."

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


def load_user_groups(group_type='user_group', get_abstract_groups=True):
    with open('generator_data/user_groups.json', 'r') as file:
        user_groups = json.load(file)

    user_groups = list(group for group in user_groups if group_type in group['type'])

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


def generate_user(name=None):
    if name is None:
        name = generate_name()

    user = {
        'name': name,
        'type': ['subject', 'user', 'person'],
        'email': '.'.join(name.lower() for name in name.split(' ')) + '@vaticle.com',
        'business_unit': generate_business_units(),
        'user_role': generate_user_roles(),
        'user_account': generate_user_accounts(),
        'uuid': generate_uuid()
    }

    return user


def generate_users(count):
    names = set()

    while len(names) < count:
        names.add(generate_name())

    users = list()

    for name in names:
        users.append(generate_user(name))

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


def generate_subjects(user_count):
    users = generate_users(user_count)
    user_groups = get_user_groups()

    for group in user_groups:
        for user in users:
            if group['name'] in user['business_unit'] + user['user_role'] + user['user_account']:
                group['member'].append(user['uuid'])

    return users + user_groups


def load_resource_collections(collection_type='resource_collection', get_abstract_collections=True):
    with open('generator_data/resource_collections.json', 'r') as file:
        resource_collections = json.load(file)

    resource_collections = list(collection for collection in resource_collections if collection_type in collection['type'])

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
        'type': ['object', 'resource', 'file'],
        'parent': [directory['name']],
        'parent_type': 'directory',
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
        member_ids = list()

        for child_collection in resource_collections:
            if sorted(child_collection['type']) == sorted(parent_collection['type']) and child_collection['name'] in parent_collection['member']:
                member_ids.append(child_collection['uuid'])

        parent_collection['member'] = member_ids

    return resource_collections


def generate_objects(resource_count):
    resources = generate_resources(resource_count)
    resource_collections = get_resource_collections()

    for collection in resource_collections:
        for resource in resources:
            if resource['parent_type'] in collection['type'] and collection['name'] in resource['parent']:
                collection['member'].append(resource['uuid'])

    return resources + resource_collections


def load_operations(object_type=None):
    with open('generator_data/operations.json', 'r') as file:
        operations = json.load(file)

    if object_type is not None:
        operations = list(operation for operation in operations if operation['object_type'] == object_type)

    return operations


def load_operation_sets(object_type=None):
    with open('generator_data/operation_sets.json', 'r') as file:
        operation_sets = json.load(file)

    if object_type is not None:
        operation_sets = list(opset for opset in operation_sets if opset['object_type'] == object_type)

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
            if operation['object_type'] == parent_set['object_type'] and operation['name'] in parent_set['member']:
                member_ids.append(operation['uuid'])

        for child_set in operation_sets:
            if child_set['object_type'] == parent_set['object_type'] and child_set['name'] in parent_set['member']:
                member_ids.append(child_set['uuid'])

        parent_set['member'] = member_ids

    return operations + operation_sets


def load_permissions(subject_type=None, object_type=None):
    with open('generator_data/permissions.json', 'r') as file:
        permissions = json.load(file)

    if subject_type is not None:
        permissions = list(permission for permission in permissions if subject_type in permission['subject_type'])

    if object_type is not None:
        permissions = list(permission for permission in permissions if object_type in permission['object_type'])

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
            if action['object_type'] == permission['object_type'] and action['name'] in permission['action']:
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


def assign_group_owner(user_group, item_list):
    users = list(item for item in item_list if 'user' in item['type'])
    members = get_nested_members(user_group, item_list)
    candidate_owner_uuids = list()

    for member in members:
        if member in users:
            candidate_owner_uuids.append(member['uuid'])

    user_group['owner'] = [random.choice(candidate_owner_uuids)]


def assign_group_owners(item_list):
    user_groups = list(item for item in item_list if 'user_group' in item['type'])

    for user_group in user_groups:
        assign_group_owner(user_group, item_list)


def assign_object_owner(obj, item_list):
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

    obj['owner'] = [random.choice(candidate_owner_uuids)]


def assign_object_owners(item_list):
    objects = list(item for item in item_list if 'object' in item['type'])

    for obj in objects:
        assign_object_owner(obj, item_list)


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

    for obj in objects:
        owner_permissions = copy.deepcopy(owner_permissions_template)

        for permission in owner_permissions:
            permission['object'].append(obj['uuid'])
            permission['subject'] += obj['owner']

            item_list.append(permission)


def generate_data(user_count, resource_count):
    subjects = generate_subjects(user_count)
    objects = generate_objects(resource_count)
    actions = get_actions()
    permissions = get_permissions(subjects, objects, actions)
    items = subjects + objects + actions + permissions
    assign_group_owners(items)
    assign_object_owners(items)
    assign_owner_permissions(items)

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
