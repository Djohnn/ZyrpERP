import pytest

from tenancy.capabilities import role_allows


@pytest.mark.parametrize(
    ('role', 'capability', 'allowed'),
    [
        ('admin', 'users.manage', True),
        ('manager', 'users.manage', False),
        ('manager', 'organization.read', True),
        ('operator', 'organization.read', False),
    ],
)
def test_role_capability_matrix(role, capability, allowed):
    assert role_allows(role, capability) is allowed
