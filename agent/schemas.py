from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    url: str
    source_type: Literal[
        "official_docs",
        "official_api_reference",
        "official_auth_docs",
        "official_pricing",
        "official_help",
        "official_blog",
        "github",
        "other"
    ]
    claim: str


class AppResearch(BaseModel):
    app_id: int
    app_name: str
    category: str

    description: str = Field(
        description="One-line description of what the app does."
    )

    auth_methods: List[str] = Field(
        description="Authentication methods supported by the developer/API platform."
    )

    self_serve_status: Literal[
        "self_serve",
        "trial",
        "paid_required",
        "admin_required",
        "partner_gated",
        "contact_sales",
        "unknown"
    ]

    credential_access: str = Field(
        description="How a developer obtains credentials or authorization."
    )

    api_type: List[str] = Field(
        description="Examples: REST, GraphQL, SDK, webhook, CLI."
    )

    api_breadth: Literal[
        "broad",
        "moderate",
        "narrow",
        "unknown"
    ]

    api_capabilities: List[str] = Field(
        description="Major capabilities exposed by the API."
    )

    mcp_available: Literal[
        "yes",
        "no",
        "unclear"
    ]

    mcp_evidence: Optional[str] = None

    agent_ready: Literal[
        "yes",
        "yes_with_setup",
        "limited",
        "no",
        "unclear"
    ]

    main_blocker: str

    buildability_reason: str

    evidence: List[Evidence]

    confidence: Literal[
        "high",
        "medium",
        "low"
    ]

    research_notes: str = ""


class ResearchBatch(BaseModel):
    results: List[AppResearch]