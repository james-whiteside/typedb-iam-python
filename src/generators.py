import random
import datetime
import calendar
import sys
import uuid
import names as name_generator
import src.utilities as utilities


def generate_uuid():
    return str(uuid.uuid4())


def generate_letter():
    return random.choice('abcdefghijklmnopqrstuvwxyz')


def generate_letter_string(length, prevent_banned_words=True):
    string = ''.join(generate_letter() for i in range(length))

    if prevent_banned_words and any(word in string for word in utilities.get_banned_words('assets/banned_words.txt')):
        return generate_letter_string(length, prevent_banned_words=prevent_banned_words)

    return string


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

    return date


def generate_resolution():
    return str(random.randint(1, 4) * 360) + 'x' + str(random.randint(1, 4) * 360)


def generate_name():
    return name_generator.get_full_name()


def generate_business_units():
    units = list()
    seed_1 = random.random()
    seed_2 = random.random()

    if 0 <= seed_1 < 0.6:
        # engineering

        if 0 <= seed_2 < 0.4:
            units.append('core')
        elif 0.4 <= seed_2 < 0.65:
            units.append('client')
        elif 0.65 <= seed_2 < 0.9:
            units.append('studio')
        else:
            units.append('engineering')

    elif 0.6 <= seed_1 < 0.75:
        # product

        if 0 <= seed_2 < 0.45:
            units.append('research')
        elif 0.45 <= seed_2 < 0.9:
            units.append('documentation')
        else:
            units.append('product')

    elif 0.75 <= seed_1 < 0.85:
        units.append('operations')

    elif 0.85 <= seed_1 < 0.95:
        units.append('people')

    else:
        units.append('executive')

    return units


def generate_user_roles():
    roles = list()
    seed_1 = random.random()
    seed_2 = random.random()
    seed_3 = random.random()
    seed_4 = random.random()
    seed_5 = random.random()

    if 0 <= seed_1 < 0.05:
        roles.append('docs_admin')
    elif 0.05 <= seed_1 < 0.25:
        roles.append('docs_editor')

    if 0 <= seed_2 < 0.05:
        roles.append('web_admin')
    elif 0.05 <= seed_2 < 0.25:
        roles.append('web_editor')

    if 0 <= seed_3 < 0.05:
        roles.append('code_admin')
    elif 0.05 <= seed_3 < 0.25:
        roles.append('code_editor')

    if 0 <= seed_4 < 0.05:
        roles.append('sys_admin')

    if 0 <= seed_5 < 0.1:
        roles.append('manager')

    return roles


def generate_user_accounts(full_name):
    accounts = list()
    accounts.append('.'.join(name.lower() for name in full_name.split(' ')) + '@vaticle.com')
    seed_1 = random.random()
    seed_2 = random.random()
    seed_3 = random.random()

    if 0 <= seed_1 < 0.15:
        accounts.append('webinars@vaticle.com')

    if 0 <= seed_2 < 0.15:
        accounts.append('sales@vaticle.com')

    if 0 <= seed_3 < 0.15:
        accounts.append('careers@vaticle.com')

    return accounts


def generate_user(full_name=None):
    if full_name is None:
        full_name = generate_name()

    user = {
        'first_name': full_name.split(' ')[0],
        'last_name': full_name.split(' ')[1],
        'business_unit': generate_business_units(),
        'user_role': generate_user_roles(),
        'user_account': generate_user_accounts(full_name),
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


def get_user_groups(users):
    user_group_names = set()

    for user in users:
        for unit in user['business_unit']:
            user_group_names.add(unit)

        for role in user['user_role']:
            user_group_names.add(role)

        for account in user['user_account']:
            user_group_names.add(account)

    if any(name in user_group_names for name in ('core', 'client', 'studio')):
        user_group_names.add('engineering')

    if any(name in user_group_names for name in ('research', 'documentation')):
        user_group_names.add('product')

    user_groups = list()

    for name in user_group_names:
        user_group = dict()
        user_group['name'] = name
        user_group['member'] = list()

        for user in users:
            if name in user['business_unit'] + user['user_role'] + user['user_account']:
                user_group['member'].append(user['uuid'])

        user_group['uuid'] = generate_uuid()
        user_groups.append(user_group)

    for parent_group in user_groups:
        if parent_group['name'] == 'engineering':
            for child_group in user_groups:
                if child_group['name'] in ('core', 'client', 'studio'):
                    parent_group['member'].append(child_group['uuid'])

        elif parent_group['name'] == 'product':
            for child_group in user_groups:
                if child_group['name'] in ('research', 'documentation'):
                    parent_group['member'].append(child_group['uuid'])

    return user_groups


def generate_source_project():
    return random.choice(['core', 'client', 'studio', 'web'])


def generate_source_subdir(project=None):
    if project is None:
        project = generate_source_project()

    if project == 'core':

        subdir = random.choice([
            '',
            '/common',
            '/concept',
            '/concurrent',
            '/config',
            '/database',
            '/dependencies',
            '/docs',
            '/encoding',
            '/graph',
            '/logic',
            '/migrator',
            '/pattern',
            '/query',
            '/reasoner',
            '/server',
            '/test',
            '/traversal'
        ])

    elif project == 'client':

        subdir = random.choice([
            '',
            '/api',
            '/common',
            '/concept',
            '/connection',
            '/dependencies',
            '/docs',
            '/logic',
            '/query',
            '/stream',
            '/test'
        ])

    elif project == 'studio':

        subdir = random.choice([
            '',
            '/binary',
            '/config',
            '/dependencies',
            '/docs',
            '/framework',
            '/module',
            '/resources',
            '/service',
            '/test'
        ])

    elif project == 'web':

        subdir = random.choice([
            '',
            '/api',
            '/assets',
            '/common',
            '/config',
            '/pages',
            '/state'
        ])

    else:
        subdir = ''

    return project + '/source' + subdir


def generate_resource_type():
    resource_type = random.choice([
        'engineering_code',
        'research_code',
        'test_data',
        'research_report',
        'documentation_published',
        'documentation_draft',
        'documentation_example',
        'finances_budget',
        'finances_report',
        'finances_invoice',
        'sales_invoice',
        'sales_order',
        'marketing_copy',
        'marketing_asset',
        'recruitment_form_output',
        'recruitment_cv',
        'contact_details'
    ])

    return resource_type


def generate_resource(resource_type=None):
    if resource_type is None:
        resource_type = generate_resource_type()

    resource = dict()

    if resource_type == 'engineering_code':
        resource['path'] = 'engineering/' + generate_source_subdir()
        resource['name'] = generate_letter_string(5) + '.java'

        if resource['path'].split('/')[1] == 'web':
            resource['name'] = generate_letter_string(5) + '.ts'

        try:
            if resource['path'].split('/')[3] == 'assets':
                resource['name'] = generate_letter_string(3) + '_' + generate_resolution() + '.svg'
        except IndexError:
            pass

    elif resource_type == 'research_code':
        resource['path'] = 'product/research/code'
        resource['name'] = generate_letter_string(5) + '.py'

    elif resource_type == 'test_data':
        resource['path'] = 'product/research/test_data'
        resource['name'] = generate_letter_string(5) + '_' + generate_letter_string(5) + '.tsv'

    elif resource_type == 'research_report':

        resource['path'] = 'product/research/reports'
        resource['name'] = generate_letter_string(7) + str(generate_date()) + '.pdf'

    elif resource_type == 'documentation_published':
        resource['path'] = 'product/documentation/published'
        resource['name'] = generate_letter_string(7) + '.md'

    elif resource_type == 'documentation_draft':
        resource['path'] = 'product/documentation/drafts'
        resource['name'] = generate_letter_string(7) + '.md'

    elif resource_type == 'documentation_example':
        resource['path'] = 'product/documentation/examples'
        resource['name'] = generate_letter_string(5) + '.tql'

    elif resource_type == 'finances_budget':
        resource['path'] = 'operations/finances/budgets'
        resource['name'] = 'budget_' + str(generate_date(day=1)) + '.xlsx'

    elif resource_type == 'finances_report':
        resource['path'] = 'operations/finances/reports'
        resource['name'] = 'report_' + str(generate_date(day=-1)) + '.xlsx'

    elif resource_type == 'finances_invoice':
        resource['path'] = 'operations/finances/invoices'
        resource['name'] = 'invoice_' + str(generate_date()) + '.pdf'

    elif resource_type == 'sales_invoice':
        resource['path'] = 'operations/sales/invoices'
        resource['name'] = 'invoice_' + str(generate_date()) + '.pdf'

    elif resource_type == 'sales_order':
        resource['path'] = 'operations/sales/orders'
        resource['name'] = 'order_' + str(generate_date()) + '.xlsx'

    elif resource_type == 'marketing_copy':
        resource['path'] = 'operations/marketing/copy'
        resource['name'] = generate_letter_string(7) + '.docx'

    elif resource_type == 'marketing_asset':
        resource['path'] = 'operations/marketing/assets'
        resource['name'] = generate_letter_string(3) + '_' + generate_resolution() + '.png'

    elif resource_type == 'recruitment_form_output':
        resource['path'] = 'people/recruitment/form_outputs'
        resource['name'] = '_'.join(generate_name().split(' ')) + '_' + str(generate_date(past_years=1)) + '.xlsx'

    elif resource_type == 'recruitment_cv':
        resource['path'] = 'people/recruitment/cvs'
        resource['name'] = '_'.join(generate_name().split(' ')) + '.pdf'

    elif resource_type == 'contact_details':
        resource['path'] = 'people/contact_details'
        resource['name'] = '_'.join(generate_name().split(' ')) + '.xlsx'

    resource['uuid'] = generate_uuid()
    return resource


def generate_resources(count):
    resources = list()

    while len(resources) < count:
        resource = generate_resource()
        resources.append(resource)

    return resources


def get_resource_collections(resources):
    resource_collection_names = set()

    for resource in resources:
        directories = resource['path'].split('/')

        for i in range(len(directories)):
            directory = '/'.join(directories[0:i+1])
            resource_collection_names.add(directory)

    resource_collections = list()

    for name in resource_collection_names:
        resource_collection = dict()
        resource_collection['name'] = name
        resource_collection['member'] = list()

        for resource in resources:
            if resource['path'] == name:
                resource_collection['member'].append(resource['uuid'])

        resource_collection['uuid'] = generate_uuid()
        resource_collections.append(resource_collection)

    for parent_collection in resource_collections:
        for child_collection in resource_collections:
            if parent_collection['uuid'] == child_collection['uuid']:
                continue

            if '/'.join(child_collection['name'].split('/')[:-1]) == parent_collection['name']:
                parent_collection['member'].append(child_collection['uuid'])

    return resource_collections


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
