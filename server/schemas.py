from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


GSTIN_PATTERN = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
PAN_PATTERN = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"


class ApplicabilityStatus(str, Enum):
    APPLICABLE = "Applicable"
    MORE_INFO_REQUIRED = "More Info Required"
    NOT_RELEVANT = "Not Relevant"


class BusinessProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    business_type: str = Field(min_length=1, max_length=100, alias="businessType")
    industry: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    employees: int = Field(ge=0)
    turnover: str = Field(min_length=1, max_length=50)
    activity: str = Field(min_length=10, max_length=1000)
    operations: str = Field(min_length=1, max_length=20)
    gstin: Optional[str] = None
    pan: Optional[str] = None

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().upper()
        if not value:
            return None
        import re

        if not re.fullmatch(GSTIN_PATTERN, value):
            raise ValueError("Invalid GSTIN format")
        return value

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().upper()
        if not value:
            return None
        import re

        if not re.fullmatch(PAN_PATTERN, value):
            raise ValueError("Invalid PAN format")
        return value


class RegistrationAssessment(BaseModel):
    name: str
    issuing_authority: Optional[str] = None
    portal_routing_note: Optional[str] = None
    status: ApplicabilityStatus
    why_relevant: str
    required_documents: list[str]
    information_still_required: list[str]
    official_links: list[str]
    source_reference_url: Optional[str] = None
    source_reference_date: Optional[str] = None
    verification_notes: list[str]


class ActionItem(BaseModel):
    step: int
    title: str
    detail: str


class DataSourceLog(BaseModel):
    source_type: str
    source_name: str
    status: str
    message: str


class ActionResult(BaseModel):
    name: str
    status: str
    message: str
    artifact_url: Optional[str] = None
    artifact_mime_type: Optional[str] = None
    artifact_content: Optional[str] = None
    artifact_base64: Optional[str] = None
    artifact_filename: Optional[str] = None


class BusinessSetupReport(BaseModel):
    profile_summary: str
    potential_registrations: list[RegistrationAssessment]
    information_still_required: list[str]
    suggested_sequence: list[ActionItem]
    gst_verification: Optional[dict] = None
    pan_verification: Optional[dict] = None
    data_sources: list[DataSourceLog] = Field(default_factory=list)
    action_results: list[ActionResult] = Field(default_factory=list)
    disclaimer: str
