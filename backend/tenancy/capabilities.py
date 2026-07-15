ROLE_CAPABILITIES = {
    'admin': frozenset({
        'organization.manage', 'organization.read', 'users.manage', 'users.read',
    }),
    'manager': frozenset({'organization.read', 'users.read'}),
    'operator': frozenset(),
}


def role_allows(role, capability):
    return capability in ROLE_CAPABILITIES.get(role, frozenset())
