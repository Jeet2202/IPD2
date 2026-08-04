"""
Unit tests for Privacy, Consent Management, Data Export, and Account Deletion workflows.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest

from app.privacy.models import DataExport, PrivacyRequest, UserConsent
from app.privacy.schemas import (
    ConsentItem,
    ConsentType,
    ConsentUpdateRequest,
    ExportFormat,
    PrivacyRequestStatus,
    PrivacyRequestType,
)
from app.privacy.service import (
    ConsentService,
    DataExportService,
    DataRetentionService,
    PrivacyService,
)


@pytest.mark.asyncio
async def test_update_user_consents():
    """Verify updating user consents logs compliance event and updates DB."""
    user_id = "user_priv_100"
    req = ConsentUpdateRequest(
        consents=[
            ConsentItem(consent_type=ConsentType.MARKETING, is_granted=True),
            ConsentItem(consent_type=ConsentType.ANALYTICS, is_granted=False),
        ]
    )

    fake_c1 = UserConsent.model_construct(user_id=user_id, consent_type=ConsentType.MARKETING, is_granted=True)
    fake_c2 = UserConsent.model_construct(user_id=user_id, consent_type=ConsentType.ANALYTICS, is_granted=False)

    with patch("app.privacy.repository.UserConsentRepository.upsert_consent", new_callable=AsyncMock, side_effect=[fake_c1, fake_c2]), \
         patch("app.privacy.service.ComplianceService.log_compliance_event", new_callable=AsyncMock) as mock_comp:

        res = await ConsentService.update_user_consents(user_id, req)
        assert len(res) == 2
        mock_comp.assert_called_once()


@pytest.mark.asyncio
async def test_account_deletion_grace_period_lifecycle():
    """Verify account deletion request starts 30-day grace period and cancellation restores clean state."""
    user_id = "user_priv_200"

    fake_request = PrivacyRequest.model_construct(
        request_id="preq_999",
        user_id=user_id,
        request_type=PrivacyRequestType.ACCOUNT_DELETION,
        status=PrivacyRequestStatus.PENDING_GRACE_PERIOD,
        grace_period_days=30,
    )

    fake_cancelled = PrivacyRequest.model_construct(
        request_id="preq_999",
        user_id=user_id,
        request_type=PrivacyRequestType.ACCOUNT_DELETION,
        status=PrivacyRequestStatus.CANCELLED,
        grace_period_days=30,
    )

    # 1. Request deletion
    with patch("app.privacy.repository.PrivacyRequestRepository.get_active_deletion_request", new_callable=AsyncMock, return_value=None), \
         patch("app.privacy.repository.PrivacyRequestRepository.create_request", new_callable=AsyncMock, return_value=fake_request), \
         patch("app.privacy.service.ComplianceService.log_compliance_event", new_callable=AsyncMock):

        del_req = await PrivacyService.request_account_deletion(user_id, reason="Testing deletion")
        assert del_req.request_id == "preq_999"
        assert del_req.status == PrivacyRequestStatus.PENDING_GRACE_PERIOD

    # 2. Cancel deletion request
    with patch("app.privacy.repository.PrivacyRequestRepository.get_active_deletion_request", new_callable=AsyncMock, return_value=fake_request), \
         patch("app.privacy.repository.PrivacyRequestRepository.update_request", new_callable=AsyncMock, return_value=fake_cancelled), \
         patch("app.privacy.service.ComplianceService.log_compliance_event", new_callable=AsyncMock):

        cancel_req = await PrivacyService.cancel_account_deletion(user_id)
        assert cancel_req.status == PrivacyRequestStatus.CANCELLED


@pytest.mark.asyncio
async def test_data_export_generation():
    """Verify JSON and CSV data export generation."""
    user_id = "user_priv_300"
    aggregated_data = {
        "personal_info": {"user_id": user_id, "email": "test@kaamsetu.com", "full_name": "Test User"},
        "booking_history_count": 5,
        "review_history_count": 2,
    }

    now = datetime.now(timezone.utc)
    fake_export_json = DataExport.model_construct(
        export_id="exp_json_1",
        user_id=user_id,
        format=ExportFormat.JSON,
        file_content="{}",
        status="ready",
        created_at=now,
        expires_at=now,
    )
    fake_export_csv = DataExport.model_construct(
        export_id="exp_csv_1",
        user_id=user_id,
        format=ExportFormat.CSV,
        file_content="Field,Value",
        status="ready",
        created_at=now,
        expires_at=now,
    )

    with patch("app.privacy.service.DataAccessService.get_aggregated_personal_data", new_callable=AsyncMock, return_value=aggregated_data), \
         patch("app.privacy.repository.DataExportRepository.create_export", new_callable=AsyncMock, side_effect=[fake_export_json, fake_export_csv]), \
         patch("app.privacy.service.ComplianceService.log_compliance_event", new_callable=AsyncMock):

        json_export = await DataExportService.generate_data_export(user_id, ExportFormat.JSON)
        assert json_export.export_id == "exp_json_1"

        csv_export = await DataExportService.generate_data_export(user_id, ExportFormat.CSV)
        assert csv_export.export_id == "exp_csv_1"
