import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from backend.models.user import User
from backend.api.dependencies import get_admin_user


@pytest.fixture
def admin_user():
    """Create a mock admin user for dependency override."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = "admin@example.com"
    user.username = "admin"
    user.is_admin = True
    user.is_active = True
    user.tenant_id = None
    return user


@pytest.mark.asyncio
async def test_create_tenant_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    payload = {
        "name": "API Tenant",
        "domain": "api-tenant.com",
    }
    response = await client.post("/api/v1/admin/tenants", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "API Tenant"
    assert data["domain"] == "api-tenant.com"
    assert "id" in data

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_list_tenants_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    await client.post("/api/v1/admin/tenants", json={
        "name": "List Tenant", "domain": "list.com"
    })

    response = await client.get("/api/v1/admin/tenants")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_create_tenant_duplicate_domain_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    payload = {"name": "Unique", "domain": "unique.com"}
    await client.post("/api/v1/admin/tenants", json=payload)
    response = await client.post("/api/v1/admin/tenants", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.text

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_create_retention_policy_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    payload = {
        "metric_id": str(uuid4()),
        "retention_days": 45,
    }
    response = await client.post("/api/v1/admin/retention-policies", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["retention_days"] == 45
    assert data["enabled"] is True
    assert "id" in data

    app.dependency_overrides.pop(get_admin_user, None)
@pytest.mark.asyncio
async def test_list_retention_policies_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    await client.post("/api/v1/admin/retention-policies", json={
        "retention_days": 30,
    })

    response = await client.get("/api/v1/admin/retention-policies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_generate_compliance_report_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    response = await client.post("/api/v1/admin/compliance/reports/gdpr")
    assert response.status_code == 200
    data = response.json()
    assert data["report_type"] == "gdpr"
    assert data["status"] == "generated"
    assert "id" in data

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_generate_soc2_report_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    response = await client.post("/api/v1/admin/compliance/reports/soc2")
    assert response.status_code == 200
    data = response.json()
    assert data["report_type"] == "soc2"
    assert data["status"] == "generated"

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_list_compliance_reports_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    await client.post("/api/v1/admin/compliance/reports/gdpr")

    response = await client.get("/api/v1/admin/compliance/reports")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_encryption_key_creation_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    response = await client.post(
        "/api/v1/admin/encryption/keys?name=test-key&passphrase=secret123"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-key"
    assert data["algorithm"] == "AES-256-GCM"
    assert "id" in data

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_list_encryption_keys_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    await client.post(
        "/api/v1/admin/encryption/keys?name=list-key&passphrase=pass123"
    )

    response = await client.get("/api/v1/admin/encryption/keys")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    app.dependency_overrides.pop(get_admin_user, None)


@pytest.mark.asyncio
async def test_rotate_encryption_key_via_api(client, admin_user):
    from backend.main import app
    app.dependency_overrides[get_admin_user] = lambda: admin_user

    create_resp = await client.post(
        "/api/v1/admin/encryption/keys?name=rotate-key&passphrase=oldpass"
    )
    key_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/v1/admin/encryption/keys/{key_id}/rotate?new_passphrase=newpass"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rotated"
    assert data["id"] != key_id

    app.dependency_overrides.pop(get_admin_user, None)

