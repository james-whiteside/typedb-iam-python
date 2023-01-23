CREATE TABLE users (
    email_address VARCHAR(256),
    first_name VARCHAR(256),
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(256)
);

CREATE TABLE business_unit (
    business_owner INT REFERENCES users(id),
    id SERIAL PRIMARY KEY,
    name VARCHAR(256)
);

ALTER TABLE users
ADD COLUMN business_unit_id INT REFERENCES business_unit(id);

CREATE TABLE business_unit_hierarchy (
    parent_business_unit INT REFERENCES business_unit(id),
    child_business_unit INT REFERENCES business_unit(id)
);

CREATE TABLE roleset (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256)
);

CREATE TABLE roleset_hierarchy (
    parent_roleset INT REFERENCES roleset(id),
    child_roleset INT REFERENCES roleset(id)
);

CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    owner_id INT REFERENCES users(id),
    roleset_id INT REFERENCES roleset(id)
);

CREATE TABLE user_role_membership (
    role_id INT REFERENCES role(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE account (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256)
);

CREATE TABLE user_account_mapping (
    account_id INT REFERENCES account(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE directory (
    business_owner INT REFERENCES users(id),
    business_unit_id INT REFERENCES business_unit(id),
    id SERIAL PRIMARY KEY,
    name VARCHAR(256)
);

CREATE TABLE directory_hierarchy (
    parent_directory INT REFERENCES directory(id),
    child_directory INT REFERENCES directory(id)
);

CREATE TABLE directory_resource (
    directory_id INT REFERENCES directory(id),
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
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
    entitlement_id INT REFERENCES entitlement(id),
    user_id INT REFERENCES users(id)
);

CREATE TABLE role_entitlement (
    entitlement_id INT REFERENCES entitlement(id),
    role_id INT REFERENCES role(id)
);

CREATE TABLE account_entitlement (
    account_id INT REFERENCES account(id),
    entitlement_id INT REFERENCES entitlement(id)
);