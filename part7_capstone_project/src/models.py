from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CompanyAnalysis(BaseModel):
    """
    Structured output for LLM company analysis focused on developer tools.
    
    This model captures key business and technical characteristics of a 
    developer tool or company, used during the analysis phase of research.
    """
    
    pricing_model: str = Field(
        description="Business model of the product. Valid values: Free, Freemium, Paid, Enterprise, Unknown"
    )
    
    is_open_source: Optional[bool] = Field(
        default=None,
        description="Whether the product is open source (True) or proprietary (False). None if unknown."
    )
    
    tech_stack: List[str] = Field(
        default_factory=list,
        description="List of technologies, frameworks, or languages the tool is built with (e.g., Python, React, PostgreSQL)"
    )
    
    description: str = Field(
        default="",
        description="Brief summary of what the tool does and its main value proposition"
    )
    
    api_available: Optional[bool] = Field(
        default=None,
        description="Whether the product offers an API for programmatic access. None if unknown."
    )
    
    language_support: List[str] = Field(
        default_factory=list,
        description="Programming languages supported by the tool (e.g., Python, JavaScript, Go)"
    )
    
    integration_capabilities: List[str] = Field(
        default_factory=list,
        description="Third-party integrations or platforms the tool connects with (e.g., GitHub, Slack, AWS)"
    )


class CompanyInfo(BaseModel):
    """
    Comprehensive structured information about a developer tool or company.
    
    This is the primary data model used to store complete information about
    a company or tool after research and analysis is complete. Extends
    CompanyAnalysis with additional identification and competitive information.
    """
    
    name: str = Field(
        description="Official name of the company or product"
    )
    
    description: str = Field(
        description="Detailed description of the company/product, its purpose, and key features"
    )
    
    website: str = Field(
        description="Official website URL (e.g., https://example.com)"
    )
    
    pricing_model: Optional[str] = Field(
        default=None,
        description="Business model: Free, Freemium, Paid, Enterprise, or Unknown"
    )
    
    is_open_source: Optional[bool] = Field(
        default=None,
        description="True if open source, False if proprietary, None if unknown"
    )
    
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Technologies used to build the product (e.g., Python, React, Kubernetes)"
    )
    
    competitors: List[str] = Field(
        default_factory=list,
        description="List of competing products or companies in the same space"
    )
    
    # Developer-specific fields
    api_available: Optional[bool] = Field(
        default=None,
        description="Whether a programmatic API is available for developers"
    )
    
    language_support: List[str] = Field(
        default_factory=list,
        description="Programming languages the tool supports (e.g., Python, JavaScript, TypeScript)"
    )
    
    integration_capabilities: List[str] = Field(
        default_factory=list,
        description="External services and platforms that can integrate with this tool"
    )
    
    developer_experience_rating: Optional[str] = Field(
        default=None,
        description="Subjective rating of developer experience: Poor, Good, or Excellent"
    )


class ResearchState(BaseModel):
    """
    State object for the research agent workflow.
    
    This model represents the state that flows through the LangGraph agent,
    accumulating information as the agent progresses through different nodes
    (search, extraction, analysis, etc.).
    """
    
    query: str = Field(
        description="The original user query or research question (e.g., 'best CI/CD tools for Python')"
    )
    
    extracted_tools: List[str] = Field(
        default_factory=list,
        description="List of tool/company names extracted from search results or articles"
    )
    
    companies: List[CompanyInfo] = Field(
        default_factory=list,
        description="Fully researched and analyzed company/tool information objects"
    )
    
    search_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Raw search results from web searches or API calls, stored as dictionaries"
    )
    
    analysis: Optional[str] = Field(
        default=None,
        description="Final synthesis or comparative analysis of all researched tools/companies"
    )