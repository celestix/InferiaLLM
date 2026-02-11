from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ScanType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ViolationType(str, Enum):
    """Types of guardrail violations."""

    TOXICITY = "toxicity"
    PII = "pii"
    PROMPT_INJECTION = "prompt_injection"
    CODE_INJECTION = "code_injection"
    SECRETS = "secrets"
    MALICIOUS_URL = "malicious_url"
    BIAS = "bias"
    SENSITIVE_DATA = "sensitive_data"
    IRRELEVANT = "irrelevant"
    BANNED_CONTENT = "banned_content"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    MALICIOUS_CODE = "malicious_code"
    KEYWORD_FILTER = "keyword_filter"
    UNKNOWN = "unknown"
    REFUSAL = "refusal"
    RELEVANCE = "relevance"

    # Llama Guard Specific
    VIOLENT_CRIMES = "violent_crimes"
    NON_VIOLENT_CRIMES = "non_violent_crimes"
    SEX_RELATED_CRIMES = "sex_related_crimes"
    CHILD_EXPLOITATION = "child_exploitation"
    DEFAMATION = "defamation"
    SPECIALIZED_ADVICE = "specialized_advice"
    PRIVACY = "privacy"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    INDISCRIMINATE_WEAPONS = "indiscriminate_weapons"
    HATE = "hate"
    SUICIDE_SELF_HARM = "suicide_self_harm"
    SEXUAL_CONTENT = "sexual_content"
    ELECTIONS = "elections"
    CODE_INTERPRETER_ABUSE = "code_interpreter_abuse"


class Violation(BaseModel):
    """Individual guardrail violation."""

    scanner: str
    violation_type: ViolationType
    score: float = Field(..., ge=0.0, le=1.0)
    details: Optional[str] = None
    detected_content: Optional[str] = None


class GuardrailResult(BaseModel):
    """Result from guardrail scanning."""

    is_valid: bool
    sanitized_text: Optional[str] = None
    risk_score: float = 0.0
    violations: List[Violation] = Field(default_factory=list)
    scan_time_ms: float = 0.0
    actions_taken: List[str] = Field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0

    def get_violations_by_type(self, violation_type: ViolationType) -> List[Violation]:
        """Get all violations of a specific type."""
        return [v for v in self.violations if v.violation_type == violation_type]


class GuardrailConfig(BaseModel):
    """Configuration for guardrail scanners."""

    enabled: bool = True
    log_violations: bool = True
    proceed_on_violation: bool = False

    toxicity_threshold: float = 0.7
    prompt_injection_threshold: float = 0.8
    bias_threshold: float = 0.75

    pii_detection_enabled: bool = True
    pii_anonymize: bool = True
    pii_entities: List[str] = Field(default_factory=list)

    banned_substrings: List[str] = Field(default_factory=list)
    detect_code_injection: bool = True
    detect_secrets: bool = True
    detect_malicious_urls: bool = True

    check_relevance: bool = True
    relevance_threshold: float = 0.5
    check_bias: bool = True

    max_scan_time_seconds: float = 5.0


class GuardrailScanRequest(BaseModel):
    text: str = Field(..., description="Text content to scan")
    scan_type: ScanType = Field(
        ..., description="Type of scan: input (prompt) or output (response)"
    )
    user_id: Optional[str] = Field(None, description="User context ID")
    context: Optional[str] = Field(
        None, description="Original input context (required for output scans)"
    )
    custom_banned_keywords: Optional[List[str]] = Field(
        None, description="Transient list of keywords to ban for this request"
    )
    pii_entities: Optional[List[str]] = Field(
        None,
        description="PII entity types to detect/redact (e.g. EMAIL_ADDRESS, PERSON)",
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Dynamic configuration for scanners (thresholds, enabled toggles)",
    )


class GuardrailScanResponse(BaseModel):
    is_valid: bool
    sanitized_text: Optional[str] = None
    risk_score: float
    violations: List[Any] = []
    scan_time_ms: float
    actions_taken: List[str] = []
