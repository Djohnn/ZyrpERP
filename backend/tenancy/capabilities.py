ROLE_CAPABILITIES = {
    'admin': frozenset({
        'organization.manage', 'organization.read', 'users.manage', 'users.read',
        'catalog.view', 'catalog.manage', 'pricing.view', 'pricing.manage',
        'inventory.view', 'inventory.receive', 'inventory.issue',
        'inventory.transfer', 'inventory.adjust', 'inventory.locations.manage',
        'sales.view', 'sales.sell', 'sales.cash.manage',
        'purchasing.view', 'purchasing.manage',
    }),
    'manager': frozenset({
        'organization.read', 'users.read',
        'catalog.view', 'catalog.manage', 'pricing.view', 'pricing.manage',
        'inventory.view', 'inventory.receive', 'inventory.issue',
        'inventory.transfer', 'inventory.adjust', 'inventory.locations.manage',
        'sales.view', 'sales.sell', 'sales.cash.manage',
        'purchasing.view', 'purchasing.manage',
    }),
    'operator': frozenset({
        'catalog.view', 'pricing.view',
        'inventory.view', 'inventory.receive', 'inventory.issue',
        'sales.view', 'sales.sell', 'sales.cash.manage',
    }),
}


def role_allows(role, capability):
    return capability in ROLE_CAPABILITIES.get(role, frozenset())
