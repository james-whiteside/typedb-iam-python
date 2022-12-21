import random
import datetime
import calendar
import sys

import names as name_generator


def generate_letter():
    return random.choice('abcdefghijklmnopqrstuvwxyz')


def generate_letter_string(length):
    return ''.join(generate_letter() for i in range(length))


def generate_name():
    return name_generator.get_full_name()


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


def generate_business_units():
    units = list()
    seed_1 = random.random()
    seed_2 = random.random()

    if 0 <= seed_1 < 0.6:
        units.append('engineering')

        if 0 <= seed_2 < 0.4:
            units.append('core')
        elif 0.4 <= seed_2 < 0.7:
            units.append('client')
        else:
            units.append('studio')

    elif 0.6 <= seed_1 < 0.75:
        units.append('product')

        if 0 <= seed_2 < 0.5:
            units.append('research')
        else:
            units.append('documentation')

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
        'user_account': generate_user_accounts(full_name)
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


def generate_resolution():
    return str(random.randint(1, 4) * 360) + 'x' + str(random.randint(1, 4) * 360)


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

        if resource['path'].split('/')[3] == 'assets':
            resource['name'] = generate_letter_string(3) + '_' + generate_resolution() + '.svg'

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
        resource['path'] = '/product/documentation/examples'
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

    return resource


def generate_resources(count):
    resources = list()

    while len(resources) < count:
        resource = generate_resource()
        resources.append(resource)

    return resources


def generate_actions(collection_type):
    if collection_type == 'application':

        actions = [
            'grant_ownership',
            'grant_permissions',
            'view_user_accounts',
            'create_user_accounts',
            'modify_user_accounts',
            'delete_user_accounts',
            'view_user_contact_details',
            'set_user_account_roles',
            'reset_user_account_passwords',
            'suspend_user_accounts'
        ]

    elif collection_type == 'directory':

        actions = [
            'grant_ownership',
            'grant_permissions',
            'view_files',
            'create_files',
            'modify_files',
            'delete_files',
            'create_subdirectories',
            'delete_subdirectories'
        ]

    elif collection_type == 'dataset':

        actions = [
            'grant_ownership',
            'grant_permissions',
            'read_records',
            'create_records',
            'update_records',
            'delete_records',
            'create_tables',
            'drop_tables'
        ]

    else:
        actions = []

    return actions
