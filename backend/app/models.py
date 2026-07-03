from pydantic import BaseModel, Field
from typing import List, Optional


class Organization(BaseModel):
    id: int
    name: str
    category: str
    website: str
    contact_name: str
    contact_email: str
    phone_number: str = ""
    status: str
    mission_notes: str
    pain_points: List[str]
    last_interaction: str


class DraftRequest(BaseModel):
    organization_id: int
    outreach_goal: str = "Explore practical AI adoption opportunities"


class DraftEmail(BaseModel):
    to: str
    subject: str
    body: str
    organization_id: int
    recipient_name: str = ""
    recipient_role: str = ""
    recipient_email_optional: str = ""
    draft_type: str = "follow_up"
    source_interaction_id: int | None = None
    source_note_summary_id: int | None = None
    status: str = "needs_review"
    human_review_notes: str = ""


class OutboxItem(DraftEmail):
    id: int
    status: str = "Saved to Demo Outbox - Not Sent"


class StatusUpdate(BaseModel):
    status: str


class OutboxUpdate(BaseModel):
    status: str | None = None
    human_review_notes: str | None = None
    recipient_name: str | None = None
    recipient_role: str | None = None
    recipient_email_optional: str | None = None
    draft_type: str | None = None


class MeetingNotesRequest(BaseModel):
    organization_id: int
    notes: str


class ResearchDiscoverRequest(BaseModel):
    research_theme: str


class ResearchIntakeRequest(BaseModel):
    organization_name: str
    website: str = ""
    general_contact_email: Optional[str] = None
    phone_number: str = ""
    organization_type: str = ""
    program_area: str = ""
    description: str = ""
    why_it_may_benefit: str = ""
    suggested_outreach_angle: str = ""
    source_url: str = ""
    notes: str = ""


class ResearchCandidate(BaseModel):
    organization_name: str
    organization_type: str = ""
    website: str = ""
    general_contact_email: Optional[str] = None
    phone_number: str = ""
    program_area: str = ""
    fit_score: int = 0
    why_it_may_be_relevant: str = ""
    suggested_outreach_angle: str = ""
    source_note: str = ""
    source_type: str = ""
    source_name: str = ""
    source_url: str = ""
    source_notes: str = ""
    why_user_selected_this_candidate: str = ""
    suggested_first_discovery_question: str = ""
    likely_workflow_pain_points: List[str] = Field(default_factory=list)
    possible_ai_support_areas: List[str] = Field(default_factory=list)
    required_human_review: List[str] = Field(default_factory=list)
    required_knowledge_sources: List[str] = Field(default_factory=list)
    adoption_risk_notes: List[str] = Field(default_factory=list)
    suggested_discovery_questions: List[str] = Field(default_factory=list)


class ResearchApproveRequest(BaseModel):
    candidate: ResearchCandidate


class InteractionCreate(BaseModel):
    organization_id: int
    interaction_type: str
    date: str
    title: str
    notes: str
    outcome: str = ""
    next_action: str = ""
    follow_up_date: str = ""
    tags: List[str] = []


class Interaction(InteractionCreate):
    id: int


class InteractionUpdate(BaseModel):
    interaction_type: str | None = None
    date: str | None = None
    title: str | None = None
    notes: str | None = None
    outcome: str | None = None
    next_action: str | None = None
    follow_up_date: str | None = None
    tags: List[str] | None = None


class OrgUpdate(BaseModel):
    contact_name: str | None = None
    contact_email: str | None = None
    phone_number: str | None = None
    website: str | None = None


class AttachmentMetadata(BaseModel):
    attachment_id: str
    original_filename: str
    stored_filename: str
    mime_type: str
    size_bytes: int
    uploaded_at: str


class AdoptionPlanCreate(BaseModel):
    organization_id: int
    summary: str = ""
    recommended_starting_point: str = ""
    selected_pilot_id: int | None = None
    roadmap_steps: List[dict] = []
    training_recommendations: List[dict] = []
    success_metrics: List[dict] = []
    change_management_notes: List[str] = []
    human_review_model: str = ""
    risk_summary: str = ""


class PilotPlanCreate(BaseModel):
    organization_id: int
    workflow_opportunity_id: int | None = None
    title: str = ""
    problem_statement: str = ""
    current_process: str = ""
    proposed_ai_assisted_process: str = ""
    scope_limit: str = ""
    required_knowledge_sources: List[str] = []
    human_review_checkpoints: List[str] = []
    participating_roles: List[str] = []
    risks: List[str] = []
    success_metrics: List[str] = []
    stop_or_revise_criteria: List[str] = []
    status: str = "Draft"


class PilotPlanUpdate(BaseModel):
    title: str | None = None
    problem_statement: str | None = None
    current_process: str | None = None
    proposed_ai_assisted_process: str | None = None
    scope_limit: str | None = None
    required_knowledge_sources: List[str] | None = None
    human_review_checkpoints: List[str] | None = None
    participating_roles: List[str] | None = None
    risks: List[str] | None = None
    success_metrics: List[str] | None = None
    stop_or_revise_criteria: List[str] | None = None
    status: str | None = None


class SuccessMetricCreate(BaseModel):
    organization_id: int
    pilot_id: int | None = None
    name: str = ""
    baseline: str = ""
    target: str = ""
    measurement_method: str = ""
    review_frequency: str = ""
    status: str = "Proposed"


class SuccessMetricUpdate(BaseModel):
    name: str | None = None
    baseline: str | None = None
    target: str | None = None
    measurement_method: str | None = None
    review_frequency: str | None = None
    status: str | None = None
