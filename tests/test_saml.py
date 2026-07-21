import pytest


@pytest.mark.asyncio
async def test_saml_metadata_endpoint(client):
    """SAML endpoints are conditionally included based on settings.saml_enabled.
    When saml_enabled is False (default in test), they return 404."""
    response = await client.get("/auth/saml/metadata")
    # Default settings have saml_enabled=False, so these route check returns 404
    assert response.status_code == 404
    assert "SAML not enabled" in response.text


@pytest.mark.asyncio
async def test_saml_login_endpoint(client):
    """When SAML is disabled, login should return 404."""
    response = await client.get("/auth/saml/login")
    assert response.status_code == 404
    assert "SAML not enabled" in response.text


@pytest.mark.asyncio
async def test_saml_acs_endpoint(client):
    """When SAML is disabled, ACS should return 404."""
    response = await client.post("/auth/saml/acs")
    assert response.status_code == 404
    assert "SAML not enabled" in response.text


@pytest.mark.asyncio
async def test_saml_disabled_returns_404(client):
    """All SAML routes return 404 when saml_enabled is False."""
    for method, path in [
        ("GET", "/auth/saml/metadata"),
        ("GET", "/auth/saml/login"),
        ("POST", "/auth/saml/acs"),
    ]:
        if method == "GET":
            response = await client.get(path)
        else:
            response = await client.post(path)
        assert response.status_code == 404, f"{method} {path} should return 404"
        assert "SAML not enabled" in response.text


@pytest.mark.asyncio
async def test_saml_acs_with_invalid_form_data(client):
    """Even with SAML disabled, POST without form data should be handled."""
    response = await client.post(
        "/auth/saml/acs",
        data={"SAMLResponse": "test-response"},
    )
    assert response.status_code == 404
    assert "SAML not enabled" in response.text
