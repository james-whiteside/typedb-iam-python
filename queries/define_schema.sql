CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(256),
    last_name VARCHAR(256),
    email_address VARCHAR(256)
);

CREATE TABLE user_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    owner_id INT REFERENCES users(id)
);

CREATE TABLE user_group_hierarchy (
    parent_user_group INT REFERENCES user_group(id),
    child_user_group INT REFERENCES user_group(id)
);

CREATE TABLE user_group_membership (
    group_id INT REFERENCES user_group(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE business_unit (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    business_owner INT REFERENCES users(id)
);

CREATE TABLE business_unit_hierarchy (
    parent_business_unit INT REFERENCES business_unit(id),
    child_business_unit INT REFERENCES business_unit(id)
);

ALTER TABLE users
ADD COLUMN business_unit_id INT REFERENCES business_unit(id);

CREATE TABLE user_role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    owner_id INT REFERENCES users(id)
);

CREATE TABLE user_role_hierarchy (
    parent_user_role INT REFERENCES user_role(id),
    child_user_role INT REFERENCES user_role(id)
);

CREATE TABLE user_role_membership (
    user_role_id INT REFERENCES user_role(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE user_account (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256)
);

CREATE TABLE user_account_mapping (
    user_account_id INT REFERENCES user_account(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE directory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    business_unit_id INT REFERENCES business_unit(id),
    business_owner INT REFERENCES users(id)
);

CREATE TABLE directory_hierarchy (
    parent_directory INT REFERENCES directory(id),
    child_directory INT REFERENCES directory(id)
);

CREATE TABLE directory_resource (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    directory_id INT REFERENCES directory(id),
    owner_id INT REFERENCES users(id)
);

CREATE TABLE entitlement (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256)
);

CREATE TABLE entitlement_hierarchy (
    parent_entitlement INT REFERENCES entitlement(id),
    child_entitlement INT REFERENCES entitlement(id)
);

CREATE TABLE directory_entitlement (
    entitlement_id INT REFERENCES entitlement(id),
    resource_id INT REFERENCES directory_resource(id)
);

CREATE TABLE user_direct_entitlement (
    user_id INT REFERENCES users(id),
    entitlement_id INT REFERENCES entitlement(id)
);

CREATE TABLE user_role_entitlement (
    user_role_id INT REFERENCES user_role(id),
    entitlement_id INT REFERENCES entitlement(id)
);

CREATE TABLE user_account_entitlement (
    user_account_id INT REFERENCES user_account(id),
    entitlement_id INT REFERENCES entitlement(id)
);