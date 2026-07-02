from pydantic import BaseModel
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


class OutboxItem(DraftEmail):
    id: int
    status: str = "Saved to Demo Outbox - Not Sent"


class StatusUpdate(BaseModel):
    status: str


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
    organization_type: str
    website: str
    general_contact_email: Optional[str] = None
    phone_number: str = ""
    program_area: str
    fit_score: int
    why_it_may_be_relevant: str
    suggested_outreach_angle: str
    source_note: str


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
