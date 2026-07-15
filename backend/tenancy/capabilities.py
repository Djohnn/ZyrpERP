ROLE_CAPABILITIES = {
    'admin': frozenset({
        'organization.manage', 'organization.read', 'users.manage', 'users.read',
        'catalog.view', 'catalog.manage', 'pricing.view', 'pricing.manage',
    }),
    'manager': frozenset({
        'organization.read', 'users.read',
        'catalog.view', 'catalog.manage', 'pricing.view', 'pricing.manage',
    }),
    'operator': frozenset({
        'catalog.view', 'pricing.view',
    }),
}


def role_allows(role, capability):
    return capability in ROLE_CAPABILITIES.get(role, frozenset())
