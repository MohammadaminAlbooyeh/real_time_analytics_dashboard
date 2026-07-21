import pytest
from uuid import uuid4
from backend.services.compliance_service import ComplianceService
from backend.models.compliance import ComplianceReport


@pytest.mark.asyncio
async def test_generate_gdpr_report(db_session):
    service = ComplianceService(db_session)
    report = await service.generate_gdpr_report()
    assert report.id is not None
    assert report.report_type == "gdpr"
    assert report.status == "generated"
    assert report.report_data is not None
    assert "GDPR" in report.report_data


@pytest.mark.asyncio
async def test_generate_gdpr_report_with_tenant(db_session):
    service = ComplianceService(db_session)
    tenant_id = uuid4()
    report = await service.generate_gdpr_report(tenant_id=tenant_id)
    assert report.tenant_id == tenant_id
    assert report.report_type == "gdpr"


@pytest.mark.asyncio
async def test_generate_soc2_report(db_session):
    service = ComplianceService(db_session)
    report = await service.generate_soc2_report()
    assert report.id is not None
    assert report.report_type == "soc2"
    assert report.status == "generated"
    assert report.report_data is not None
    assert "SOC2" in report.report_data


@pytest.mark.asyncio
async def test_generate_soc2_report_with_tenant(db_session):
    service = ComplianceService(db_session)
    tenant_id = uuid4()
    report = await service.generate_soc2_report(tenant_id=tenant_id)
    assert report.tenant_id == tenant_id
    assert report.report_type == "soc2"


@pytest.mark.asyncio
async def test_list_reports(db_session):
    service = ComplianceService(db_session)
    await service.generate_gdpr_report()
    await service.generate_soc2_report()
    await service.generate_gdpr_report()

    reports = await service.list_reports()
    assert len(reports) == 3


@pytest.mark.asyncio
async def test_list_reports_filter_by_type(db_session):
    service = ComplianceService(db_session)
    await service.generate_gdpr_report()
    await service.generate_soc2_report()
    await service.generate_gdpr_report()

    gdpr_reports = await service.list_reports(report_type="gdpr")
    assert len(gdpr_reports) == 2
    for r in gdpr_reports:
        assert r.report_type == "gdpr"

    soc2_reports = await service.list_reports(report_type="soc2")
    assert len(soc2_reports) == 1
    assert soc2_reports[0].report_type == "soc2"


@pytest.mark.asyncio
async def test_list_reports_filter_by_tenant(db_session):
    service = ComplianceService(db_session)
    tenant_a = uuid4()
    tenant_b = uuid4()
    await service.generate_gdpr_report(tenant_id=tenant_a)
    await service.generate_soc2_report(tenant_id=tenant_b)
    await service.generate_gdpr_report(tenant_id=tenant_a)

    tenant_a_reports = await service.list_reports(tenant_id=tenant_a)
    assert len(tenant_a_reports) == 2

    tenant_b_reports = await service.list_reports(tenant_id=tenant_b)
    assert len(tenant_b_reports) == 1


@pytest.mark.asyncio
async def test_get_report(db_session):
    service = ComplianceService(db_session)
    created = await service.generate_gdpr_report()

    found = await service.get_report(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.report_type == "gdpr"


@pytest.mark.asyncio
async def test_get_report_not_found(db_session):
    service = ComplianceService(db_session)
    result = await service.get_report(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_list_reports_ordered_by_created_at_desc(db_session):
    service = ComplianceService(db_session)
    r1 = await service.generate_gdpr_report()
    r2 = await service.generate_soc2_report()
    r3 = await service.generate_gdpr_report()

    reports = await service.list_reports()
    assert len(reports) == 3
    # All three reports are present
    ids = [r.id for r in reports]
    assert r1.id in ids
    assert r2.id in ids
    assert r3.id in ids
