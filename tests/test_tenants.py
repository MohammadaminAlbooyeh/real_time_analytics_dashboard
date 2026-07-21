import pytest
from uuid import uuid4
from backend.services.tenant_service import TenantService
from backend.models.tenant import Tenant


@pytest.mark.asyncio
async def test_create_tenant(db_session):
    service = TenantService(db_session)
    tenant = await service.create_tenant(name="Acme Corp", domain="acme.com")
    assert tenant.id is not None
    assert tenant.name == "Acme Corp"
    assert tenant.domain == "acme.com"
    assert tenant.is_active is True


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    service = TenantService(db_session)
    created = await service.create_tenant(name="Test Corp", domain="test.com")

    found = await service.get_by_id(created.id)
    assert found is not None
    assert found.name == "Test Corp"
    assert found.domain == "test.com"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    service = TenantService(db_session)
    result = await service.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_by_domain(db_session):
    service = TenantService(db_session)
    await service.create_tenant(name="Domain Co", domain="domainco.com")

    found = await service.get_by_domain("domainco.com")
    assert found is not None
    assert found.name == "Domain Co"


@pytest.mark.asyncio
async def test_get_by_domain_not_found(db_session):
    service = TenantService(db_session)
    result = await service.get_by_domain("nonexistent.com")
    assert result is None


@pytest.mark.asyncio
async def test_list_tenants(db_session):
    service = TenantService(db_session)
    await service.create_tenant(name="Alpha", domain="alpha.com")
    await service.create_tenant(name="Beta", domain="beta.com")
    await service.create_tenant(name="Gamma", domain="gamma.com")

    tenants = await service.list_tenants()
    assert len(tenants) == 3


@pytest.mark.asyncio
async def test_list_tenants_with_pagination(db_session):
    service = TenantService(db_session)
    for i in range(5):
        await service.create_tenant(name=f"Company {i}", domain=f"company{i}.com")

    tenants = await service.list_tenants(skip=1, limit=2)
    assert len(tenants) == 2


@pytest.mark.asyncio
async def test_update_tenant(db_session):
    service = TenantService(db_session)
    created = await service.create_tenant(name="Old Name", domain="old.com")

    updated = await service.update_tenant(created.id, name="New Name")
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.domain == "old.com"  # unchanged


@pytest.mark.asyncio
async def test_update_tenant_not_found(db_session):
    service = TenantService(db_session)
    result = await service.update_tenant(uuid4(), name="Noop")
    assert result is None


@pytest.mark.asyncio
async def test_delete_tenant(db_session):
    service = TenantService(db_session)
    created = await service.create_tenant(name="Delete Me", domain="delete.com")

    deleted = await service.delete_tenant(created.id)
    assert deleted is True

    found = await service.get_by_id(created.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_tenant_not_found(db_session):
    service = TenantService(db_session)
    result = await service.delete_tenant(uuid4())
    assert result is False


@pytest.mark.asyncio
async def test_create_duplicate_tenant_name(db_session):
    service = TenantService(db_session)
    await service.create_tenant(name="Duplicate", domain="first.com")

    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        await service.create_tenant(name="Duplicate", domain="second.com")
        await db_session.flush()
