"""
Mock Government Verification Adapters — DEMO/SANDBOX MODE

⚠️  IMPORTANT: All data returned by these adapters is SIMULATED.
    These adapters do NOT connect to real government systems.
    Real adapters are pluggable replacements for production use.
    Every response is labeled: authorization_context="MOCK_SANDBOX"

Mock scenarios supported:
    GST_ACTIVE, GST_CANCELLED, GST_CONFLICT, UNAVAILABLE, NOT_FOUND
    UDYAM_VERIFIED, MCA_VERIFIED, PAN_MATCH, BLACKLIST_CLEAR, BLACKLIST_FLAGGED
"""
import random
from datetime import UTC, datetime, date
from typing import Optional

from app.engines.verification_engine.base import (
    VerificationProvider,
    VerificationResult,
    VerificationStatus,
)


# ── Mock Data Registry ─────────────────────────────────────────────────────────

MOCK_GST_REGISTRY: dict[str, dict] = {
    "27AABCS1429B1Z5": {
        "gstin": "27AABCS1429B1Z5",
        "trade_name": "Stellar Systems Private Limited",
        "legal_name": "Stellar Systems Private Limited",
        "status": "ACTIVE",
        "registration_date": "2015-04-01",
        "state": "Maharashtra",
        "state_code": "27",
        "taxpayer_type": "Regular",
        "business_nature": ["Manufacturing", "Services"],
        "address": "Plot 42, MIDC, Andheri East, Mumbai - 400093",
        "pan": "AABCS1429B",
        "annual_aggregate_turnover": "ABOVE_5CR",
    },
    "07AADCB2230M1Z3": {
        "gstin": "07AADCB2230M1Z3",
        "trade_name": "BuildCraft Infrastructure Ltd",
        "legal_name": "BuildCraft Infrastructure Limited",
        "status": "CANCELLED",  # ← GST CONFLICT scenario
        "cancellation_date": "2023-08-15",
        "cancellation_reason": "Voluntary Cancellation",
        "state": "Delhi",
        "pan": "AADCB2230M",
    },
    "29AABCT1332L1Z8": {
        "gstin": "29AABCT1332L1Z8",
        "trade_name": "TechFabricators Bangalore",
        "legal_name": "TechFabricators Private Limited",
        "status": "ACTIVE",
        "registration_date": "2018-07-12",
        "state": "Karnataka",
        "pan": "AABCT1332L",
    },
    # Network scenario — shared directors
    "27AAKCM6743P1ZR": {
        "gstin": "27AAKCM6743P1ZR",
        "trade_name": "AlphaTech Solutions",
        "legal_name": "AlphaTech Solutions Pvt Ltd",
        "status": "ACTIVE",
        "state": "Maharashtra",
        "pan": "AAKCM6743P",
    },
    "27AAKDB7721Q1ZS": {
        "gstin": "27AAKDB7721Q1ZS",
        "trade_name": "BetaCore Industries",
        "legal_name": "BetaCore Industries Pvt Ltd",
        "status": "ACTIVE",
        "state": "Maharashtra",
        "pan": "AAKDB7721Q",
    },
}

MOCK_UDYAM_REGISTRY: dict[str, dict] = {
    "UDYAM-MH-10-0012345": {
        "udyam_number": "UDYAM-MH-10-0012345",
        "enterprise_name": "Stellar Systems Private Limited",
        "category": "SMALL",
        "pan": "AABCS1429B",
        "date_of_commencement": "2015-04-01",
        "nic_code": "26909",
        "district": "Mumbai",
        "state": "Maharashtra",
        "status": "ACTIVE",
    },
    "UDYAM-KA-05-0078901": {
        "udyam_number": "UDYAM-KA-05-0078901",
        "enterprise_name": "TechFabricators Private Limited",
        "category": "MICRO",
        "pan": "AABCT1332L",
        "status": "ACTIVE",
        "state": "Karnataka",
    },
}

MOCK_PAN_REGISTRY: dict[str, dict] = {
    "AABCS1429B": {"pan": "AABCS1429B", "name": "STELLAR SYSTEMS PRIVATE LIMITED", "status": "ACTIVE", "type": "COMPANY"},
    "AADCB2230M": {"pan": "AADCB2230M", "name": "BUILDCRAFT INFRASTRUCTURE LIMITED", "status": "ACTIVE", "type": "COMPANY"},
    "AABCT1332L": {"pan": "AABCT1332L", "name": "TECHFABRICATORS PRIVATE LIMITED", "status": "ACTIVE", "type": "COMPANY"},
    "AAKCM6743P": {"pan": "AAKCM6743P", "name": "ALPHATECH SOLUTIONS PVT LTD", "status": "ACTIVE", "type": "COMPANY"},
    "AAKDB7721Q": {"pan": "AAKDB7721Q", "name": "BETACORE INDUSTRIES PVT LTD", "status": "ACTIVE", "type": "COMPANY"},
}

MOCK_BLACKLIST_REGISTRY: dict[str, dict] = {
    "AADCB2230M": {
        "identifier": "AADCB2230M",
        "is_blacklisted": False,
        "source": "MCA_DEBARRED_LIST",
        "checked_at": datetime.now(UTC).isoformat(),
    },
    "BLACKLISTED_PAN_001": {
        "identifier": "BLACKLISTED_PAN_001",
        "is_blacklisted": True,
        "reason": "Debarment order dated 2023-01-15",
        "debarment_period_from": "2023-01-15",
        "debarment_period_until": "2026-01-15",
        "authority": "Department of Expenditure",
        "order_reference": "DoE/DEB/2023/001",
        "source": "DEBARRED_VENDOR_LIST",
    },
}


# ── Mock GST Adapter ───────────────────────────────────────────────────────────

class MockGSTProvider(VerificationProvider):
    provider_name = "GST"
    is_mock = True

    async def verify(self, identifier: str, scenario: Optional[str] = None, **kwargs) -> VerificationResult:
        gstin = identifier.upper().strip()

        # Scenario D: GST CONFLICT — document says ACTIVE, authority says CANCELLED
        if scenario == "D" or gstin == "07AADCB2230M1Z3":
            data = MOCK_GST_REGISTRY.get(gstin, {})
            data_copy = dict(data)
            # Simulate: document claimed ACTIVE, but registry says CANCELLED
            return VerificationResult(
                source="GST_MOCK_ADAPTER",
                provider="GST",
                queried_identifier=gstin,
                returned_identifier=gstin,
                status=VerificationStatus.CONFLICT,
                data={**data_copy, "_conflict": "Document claims status=ACTIVE but registry returns CANCELLED"},
                checked_at=datetime.now(UTC),
                source_reference="https://www.gst.gov.in/ [MOCK]",
                authorization_context="MOCK_SANDBOX",
                confidence=0.95,
                conflict_details=(
                    "Document states GST status as ACTIVE. "
                    "Mock GST registry returned status: CANCELLED (Cancellation date: 2023-08-15). "
                    "This constitutes a verification conflict requiring manual review."
                ),
                is_mock=True,
                is_demo=True,
            )

        # Scenario E: API UNAVAILABLE
        if scenario == "E":
            return self._make_unavailable(gstin, "GST API returned HTTP 503. Retry scheduled.")

        # Normal lookup
        data = MOCK_GST_REGISTRY.get(gstin)
        if data:
            return VerificationResult(
                source="GST_MOCK_ADAPTER",
                provider="GST",
                queried_identifier=gstin,
                returned_identifier=data["gstin"],
                status=VerificationStatus.VERIFIED,
                data=data,
                checked_at=datetime.now(UTC),
                source_reference="https://www.gst.gov.in/ [MOCK]",
                authorization_context="MOCK_SANDBOX",
                confidence=0.98,
                is_mock=True,
                is_demo=True,
            )

        return VerificationResult(
            source="GST_MOCK_ADAPTER",
            provider="GST",
            queried_identifier=gstin,
            returned_identifier=None,
            status=VerificationStatus.NOT_FOUND,
            data=None,
            checked_at=datetime.now(UTC),
            source_reference="https://www.gst.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.0,
            error_code="NOT_FOUND",
            is_mock=True,
            is_demo=True,
        )


class MockUdyamProvider(VerificationProvider):
    provider_name = "UDYAM"
    is_mock = True

    async def verify(self, identifier: str, scenario: Optional[str] = None, **kwargs) -> VerificationResult:
        udyam = identifier.upper().strip()
        if scenario == "E":
            return self._make_unavailable(udyam, "Udyam portal API unavailable.")

        data = MOCK_UDYAM_REGISTRY.get(udyam)
        if data:
            return VerificationResult(
                source="UDYAM_MOCK_ADAPTER",
                provider="UDYAM",
                queried_identifier=udyam,
                returned_identifier=data["udyam_number"],
                status=VerificationStatus.VERIFIED,
                data=data,
                checked_at=datetime.now(UTC),
                source_reference="https://udyamregistration.gov.in/ [MOCK]",
                authorization_context="MOCK_SANDBOX",
                confidence=0.97,
                is_mock=True,
                is_demo=True,
            )
        return VerificationResult(
            source="UDYAM_MOCK_ADAPTER",
            provider="UDYAM",
            queried_identifier=udyam,
            returned_identifier=None,
            status=VerificationStatus.NOT_FOUND,
            data=None,
            checked_at=datetime.now(UTC),
            source_reference="https://udyamregistration.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.0,
            is_mock=True,
            is_demo=True,
        )


class MockMCAProvider(VerificationProvider):
    provider_name = "MCA"
    is_mock = True

    async def verify(self, identifier: str, scenario: Optional[str] = None, **kwargs) -> VerificationResult:
        cin = identifier.upper().strip()
        # Simulate basic MCA response
        data = {
            "cin": cin,
            "company_name": kwargs.get("company_name", "UNKNOWN COMPANY"),
            "status": "ACTIVE",
            "incorporation_date": "2015-01-01",
            "registered_office": kwargs.get("address", "Unknown"),
            "class_of_company": "PRIVATE",
            "authorised_capital": 10000000,
            "paid_up_capital": 5000000,
        }
        if scenario == "E":
            return self._make_unavailable(cin, "MCA21 portal timeout.")
        return VerificationResult(
            source="MCA_MOCK_ADAPTER",
            provider="MCA",
            queried_identifier=cin,
            returned_identifier=cin,
            status=VerificationStatus.VERIFIED,
            data=data,
            checked_at=datetime.now(UTC),
            source_reference="https://www.mca.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.92,
            is_mock=True,
            is_demo=True,
        )


class MockPANProvider(VerificationProvider):
    provider_name = "PAN"
    is_mock = True

    async def verify(self, identifier: str, expected_name: Optional[str] = None, **kwargs) -> VerificationResult:
        pan = identifier.upper().strip()
        data = MOCK_PAN_REGISTRY.get(pan)
        if data:
            status = VerificationStatus.VERIFIED
            conflict = None
            if expected_name and expected_name.upper() not in data["name"].upper():
                status = VerificationStatus.CONFLICT
                conflict = f"Expected name '{expected_name}' does not match registered name '{data['name']}'"
            return VerificationResult(
                source="PAN_MOCK_ADAPTER",
                provider="PAN",
                queried_identifier=pan,
                returned_identifier=pan,
                status=status,
                data=data,
                checked_at=datetime.now(UTC),
                source_reference="https://incometaxindiaefiling.gov.in/ [MOCK]",
                authorization_context="MOCK_SANDBOX",
                confidence=0.99,
                conflict_details=conflict,
                is_mock=True,
                is_demo=True,
            )
        return VerificationResult(
            source="PAN_MOCK_ADAPTER",
            provider="PAN",
            queried_identifier=pan,
            returned_identifier=None,
            status=VerificationStatus.NOT_FOUND,
            data=None,
            checked_at=datetime.now(UTC),
            source_reference="https://incometaxindiaefiling.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.0,
            is_mock=True,
            is_demo=True,
        )


class MockBlacklistProvider(VerificationProvider):
    provider_name = "BLACKLIST"
    is_mock = True

    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        data = MOCK_BLACKLIST_REGISTRY.get(identifier.upper())
        if data and data.get("is_blacklisted"):
            return VerificationResult(
                source="BLACKLIST_MOCK_ADAPTER",
                provider="BLACKLIST",
                queried_identifier=identifier,
                returned_identifier=identifier,
                status=VerificationStatus.CONFLICT,
                data=data,
                checked_at=datetime.now(UTC),
                source_reference="DoE Debarred Vendor List [MOCK]",
                authorization_context="MOCK_SANDBOX",
                confidence=0.99,
                conflict_details=f"Entity appears on debarment list: {data.get('reason', 'No reason provided')}",
                is_mock=True,
                is_demo=True,
            )
        return VerificationResult(
            source="BLACKLIST_MOCK_ADAPTER",
            provider="BLACKLIST",
            queried_identifier=identifier,
            returned_identifier=identifier,
            status=VerificationStatus.VERIFIED,
            data={"is_blacklisted": False, "checked_against": ["DoE_DEBARRED", "MCA_DISQUALIFIED", "CBI_WANTED"]},
            checked_at=datetime.now(UTC),
            source_reference="DoE Debarred Vendor List [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.95,
            is_mock=True,
            is_demo=True,
        )


class MockEPFOProvider(VerificationProvider):
    provider_name = "EPFO"
    is_mock = True

    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        return VerificationResult(
            source="EPFO_MOCK_ADAPTER",
            provider="EPFO",
            queried_identifier=identifier,
            returned_identifier=identifier,
            status=VerificationStatus.VERIFIED,
            data={
                "establishment_id": identifier,
                "status": "ACTIVE",
                "employee_count": random.randint(10, 500),
                "compliance_status": "COMPLIANT",
            },
            checked_at=datetime.now(UTC),
            source_reference="https://www.epfindia.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.85,
            is_mock=True,
            is_demo=True,
        )


class MockESICProvider(VerificationProvider):
    provider_name = "ESIC"
    is_mock = True

    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        return VerificationResult(
            source="ESIC_MOCK_ADAPTER",
            provider="ESIC",
            queried_identifier=identifier,
            returned_identifier=identifier,
            status=VerificationStatus.VERIFIED,
            data={"employer_code": identifier, "status": "ACTIVE", "compliance": "COMPLIANT"},
            checked_at=datetime.now(UTC),
            source_reference="https://www.esic.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.85,
            is_mock=True,
            is_demo=True,
        )


class MockDigiLockerProvider(VerificationProvider):
    provider_name = "DIGILOCKER"
    is_mock = True

    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        return self._make_unauthorized(identifier)


class MockBISProvider(VerificationProvider):
    provider_name = "BIS"
    is_mock = True

    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        return VerificationResult(
            source="BIS_MOCK_ADAPTER",
            provider="BIS",
            queried_identifier=identifier,
            returned_identifier=identifier,
            status=VerificationStatus.VERIFIED,
            data={"license_number": identifier, "status": "VALID", "product_category": kwargs.get("category")},
            checked_at=datetime.now(UTC),
            source_reference="https://www.bis.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.88,
            is_mock=True,
            is_demo=True,
        )


class MockGeMProvider(VerificationProvider):
    provider_name = "GEM"
    is_mock = True

    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        return VerificationResult(
            source="GEM_MOCK_ADAPTER",
            provider="GEM",
            queried_identifier=identifier,
            returned_identifier=identifier,
            status=VerificationStatus.VERIFIED,
            data={"seller_id": identifier, "status": "ACTIVE", "categories": []},
            checked_at=datetime.now(UTC),
            source_reference="https://gem.gov.in/ [MOCK]",
            authorization_context="MOCK_SANDBOX",
            confidence=0.90,
            is_mock=True,
            is_demo=True,
        )
