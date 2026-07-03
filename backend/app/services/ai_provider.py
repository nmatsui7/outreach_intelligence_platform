import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import ai_mock
from .interaction_summaries import get_summaries_for_org

logger = logging.getLogger(__name__)

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

_llm_available = False
try:
    from tools.llm import call_llm, call_llm_json
    _llm_available = True
except ImportError:
    logger.warning("tools.llm not available; local_llm provider will fall back to mock")


class AiProvider:
    """Abstract AI provider — all methods return the same shapes as ai_mock.py"""

    def summarize_organization(self, org: dict) -> dict: ...
    def discover_opportunities(self, org: dict) -> dict: ...
    def generate_next_best_email(
        self,
        org: dict,
        interactions: list,
        ai_summary: dict,
        outbox_entries: list,
        extra_context: Optional[dict] = None,
    ) -> dict: ...
    def derive_status_from_interactions(self, interactions: list, current_status: str) -> str: ...
    def generate_readiness_assessment(self, org: dict, interactions: list, opportunities: dict) -> dict: ...
    def meeting_brief(self, org: dict) -> dict: ...
    def summarize_notes(self, notes: str) -> dict: ...
    def summarize_interaction_notes(self, notes: str, interaction_type: str) -> dict: ...
    def generate_knowledge_summary(self, org: dict, interactions: list) -> dict: ...


class MockProvider(AiProvider):
    """Delegates directly to ai_mock.py — no external calls."""

    def summarize_organization(self, org: dict) -> dict:
        return ai_mock.summarize_organization(org)

    def discover_opportunities(self, org: dict) -> dict:
        return ai_mock.discover_opportunities(org)

    def generate_next_best_email(
        self,
        org: dict,
        interactions: list,
        ai_summary: dict,
        outbox_entries: list,
        extra_context: Optional[dict] = None,
    ) -> dict:
        return ai_mock.generate_next_best_email(org, interactions, ai_summary, outbox_entries)

    def derive_status_from_interactions(self, interactions: list, current_status: str) -> str:
        return ai_mock.derive_status_from_interactions(interactions, current_status)

    def generate_readiness_assessment(self, org: dict, interactions: list, opportunities: dict) -> dict:
        return ai_mock.generate_readiness_assessment(org, interactions, opportunities)

    def meeting_brief(self, org: dict) -> dict:
        return ai_mock.meeting_brief(org)

    def summarize_notes(self, notes: str) -> dict:
        return ai_mock.summarize_notes(notes)

    def summarize_interaction_notes(self, notes: str, interaction_type: str) -> dict:
        return ai_mock.summarize_interaction_notes(notes, interaction_type)

    def generate_knowledge_summary(self, org: dict, interactions: list) -> dict:
        return ai_mock.generate_knowledge_summary(org, interactions)


class LocalLlmProvider(AiProvider):
    """Calls local LLM via tools/llm.py with mock fallback on failure."""

    def _call_json(self, system: str, user: str, fallback: callable) -> dict:
        if not _llm_available:
            logger.warning("tools.llm not available — falling back to mock")
            return fallback()
        try:
            result = call_llm_json(system, user)
            if isinstance(result, dict) and result:
                return result
            logger.warning("LLM returned empty or non-dict — falling back to mock")
        except Exception as e:
            logger.warning(f"LLM call failed: {e} — falling back to mock")
        return fallback()

    def summarize_organization(self, org: dict) -> dict:
        def fallback() -> dict:
            return ai_mock.summarize_organization(org)
        system = (
            "You are an AI outreach assistant. Given an organization profile, "
            "return a JSON object with these keys: "
            "summary (str), outreach_priority (High|Medium|Low), "
            "ai_readiness_score (int 0-100), why_it_matters (list[str]), "
            "recommended_questions (list[str]). "
            "Be concise. Return ONLY valid JSON."
        )
        user = json.dumps({k: v for k, v in org.items() if k in (
            "name", "category", "status", "pain_points", "mission_notes"
        )})
        return self._call_json(system, user, fallback)

    def discover_opportunities(self, org: dict) -> dict:
        def fallback() -> dict:
            return ai_mock.discover_opportunities(org)
        system = (
            "You are an AI adoption consultant. Given an organization profile, "
            "suggest 3 practical AI-assisted workflow opportunities. "
            "Return a JSON object with key 'opportunities' containing a list of objects, "
            "each with: name (str), benefit (str), effort (Low|Medium|High), "
            "human_review_note (str). "
            "Return ONLY valid JSON."
        )
        user = json.dumps({k: v for k, v in org.items() if k in (
            "name", "category", "pain_points", "mission_notes"
        )})
        return self._call_json(system, user, fallback)

    def generate_next_best_email(
        self,
        org: dict,
        interactions: list,
        ai_summary: dict,
        outbox_entries: list,
        extra_context: Optional[dict] = None,
    ) -> dict:
        def fallback() -> dict:
            return ai_mock.generate_next_best_email(org, interactions, ai_summary, outbox_entries)

        ctx = extra_context or {}

        system = (
            "You are an AI outreach assistant. Generate a context-aware outreach email "
            "for an organization. Use the provided context to craft a relevant, "
            "personalized email. The email must be review-only — it will be saved to "
            "a draft queue for human review before any action is taken. "
            "Return a JSON object with these exact keys: "
            "subject (str), body (str), tone (str), "
            "reasoning_summary (str), "
            "human_review_notes (list[str]), "
            "missing_context (list[str]), "
            "suggested_edits (list[str]). "
            "Return ONLY valid JSON."
        )

        payload = {
            "organization": {
                "name": org.get("name"),
                "category": org.get("category"),
                "status": org.get("status"),
                "pain_points": org.get("pain_points", []),
                "mission_notes": org.get("mission_notes", ""),
                "contact_name": org.get("contact_name"),
                "contact_email": org.get("contact_email"),
            },
            "interaction_count": len(interactions),
            "recent_interactions": [
                {"date": i.get("date"), "title": i.get("title"),
                 "type": i.get("interaction_type"), "outcome": i.get("outcome"),
                 "notes": (i.get("notes") or "")[:300]}
                for i in (interactions[-5:] if interactions else [])
            ],
            "ai_readiness_score": ai_summary.get("ai_readiness_score"),
            "outreach_priority": ai_summary.get("outreach_priority"),
            "ai_readiness_level": ctx.get("readiness_level"),
            "outreach_recommendation": {
                "priority": ctx.get("outreach_priority"),
                "next_action": ctx.get("recommended_next_action"),
                "follow_up_date": ctx.get("recommended_follow_up_date"),
                "collaboration_angles": ctx.get("collaboration_angles", []),
                "risks": ctx.get("risks_or_concerns", []),
                "missing_info": ctx.get("missing_information", []),
            } if ctx.get("recommended_next_action") else None,
            "workflow_intelligence_notes": ctx.get("workflow_summaries", []),
            "discovery_opportunities": ctx.get("opportunities", []),
            "follow_up_tasks": ctx.get("follow_up_tasks", []),
            "adoption_risks": ctx.get("adoption_risks", []),
            "candidate_source_notes": ctx.get("candidate_source_notes", {}),
            "previous_drafts": [
                {"subject": d.get("subject"), "status": d.get("status"),
                 "human_review_notes": d.get("human_review_notes")}
                for d in outbox_entries[-5:]
            ] if outbox_entries else [],
        }

        return self._call_json(system, json.dumps(payload), fallback)

    def derive_status_from_interactions(self, interactions: list, current_status: str) -> str:
        return ai_mock.derive_status_from_interactions(interactions, current_status)

    def generate_readiness_assessment(self, org: dict, interactions: list, opportunities: dict) -> dict:
        def fallback() -> dict:
            return ai_mock.generate_readiness_assessment(org, interactions, opportunities)
        system = (
            "You are an AI readiness assessment consultant. Given an organization "
            "profile, interactions, and opportunities, score 6 categories (each 0-20 "
            "or 0-10) and produce an overall assessment. "
            "Return a JSON object with keys: "
            "total_score (int), overall_level (Low|Moderate|High), "
            "category_scores (dict), gaps (list[str]), risks_or_concerns (list[str]), "
            "suggested_questions (list[str]). "
            "Return ONLY valid JSON."
        )
        user = json.dumps({
            "organization": {k: v for k, v in org.items() if k in (
                "name", "category", "status", "pain_points"
            )},
            "interaction_count": len(interactions),
            "opportunity_count": len(opportunities.get("opportunities", [])),
        })
        return self._call_json(system, user, fallback)

    def meeting_brief(self, org: dict) -> dict:
        def fallback() -> dict:
            return ai_mock.meeting_brief(org)
        system = (
            "You are an AI meeting preparation assistant. Given an organization profile, "
            "produce a meeting brief. "
            "Return a JSON object with keys: "
            "brief (str), discussion_topics (list[str]), desired_outcome (str). "
            "Return ONLY valid JSON."
        )
        user = json.dumps({k: v for k, v in org.items() if k in (
            "name", "category", "mission_notes", "pain_points"
        )})
        return self._call_json(system, user, fallback)

    def summarize_notes(self, notes: str) -> dict:
        def fallback() -> dict:
            return ai_mock.summarize_notes(notes)
        system = (
            "You are an AI meeting note summarizer. Given raw meeting notes, "
            "extract structured information. "
            "Return a JSON object with keys: "
            "summary (str), decisions (list[str]), action_items (list[str]), "
            "risks (list[str]), tags (list[str]), "
            "follow_up_recommendation (str). "
            "Return ONLY valid JSON."
        )
        user = notes[:4000] if len(notes) > 4000 else notes
        return self._call_json(system, user, fallback)

    def summarize_interaction_notes(self, notes: str, interaction_type: str) -> dict:
        def fallback() -> dict:
            return ai_mock.summarize_interaction_notes(notes, interaction_type)
        system = (
            "You are an AI workflow analyst. Given interaction notes and type, "
            "extract structured knowledge. "
            "Return a JSON object with keys: "
            "summary (str), interaction_type (str), "
            "discussion_points (list[str]), decisions (list[str]), "
            "action_items (list[str]), risks (list[str]), "
            "lessons (list[dict]), insights (list[dict]), "
            "workflow_fields (dict), tags (list[str]), "
            "follow_up_recommendation (str). "
            "Return ONLY valid JSON."
        )
        user = json.dumps({
            "interaction_type": interaction_type,
            "notes": notes[:4000] if len(notes) > 4000 else notes,
        })
        return self._call_json(system, user, fallback)

    def generate_knowledge_summary(self, org: dict, interactions: list) -> dict:
        def fallback() -> dict:
            return ai_mock.generate_knowledge_summary(org, interactions)
        system = (
            "You are an AI knowledge analyst. Given organization data and "
            "interaction history, produce a comprehensive knowledge summary. "
            "Return a JSON object with keys: "
            "relationship_status (str), main_interests (list[str]), "
            "lessons (list[dict]), insights (list[dict]), "
            "workflow_fields (dict), tags (list[str]), "
            "recommended_actions (list[str]). "
            "Return ONLY valid JSON."
        )
        user = json.dumps({
            "organization": {k: v for k, v in org.items() if k in (
                "name", "category", "status", "pain_points", "mission_notes"
            )},
            "interactions": [
                {"date": i.get("date"), "title": i.get("title"),
                 "type": i.get("interaction_type"), "outcome": i.get("outcome")}
                for i in interactions
            ],
        })
        return self._call_json(system, user, fallback)


class OpenAiProvider(AiProvider):
    """Placeholder for future OpenAI integration. Falls back to mock."""

    def summarize_organization(self, org: dict) -> dict:
        return ai_mock.summarize_organization(org)

    def discover_opportunities(self, org: dict) -> dict:
        return ai_mock.discover_opportunities(org)

    def generate_next_best_email(
        self,
        org: dict,
        interactions: list,
        ai_summary: dict,
        outbox_entries: list,
        extra_context: Optional[dict] = None,
    ) -> dict:
        return ai_mock.generate_next_best_email(org, interactions, ai_summary, outbox_entries)

    def derive_status_from_interactions(self, interactions: list, current_status: str) -> str:
        return ai_mock.derive_status_from_interactions(interactions, current_status)

    def generate_readiness_assessment(self, org: dict, interactions: list, opportunities: dict) -> dict:
        return ai_mock.generate_readiness_assessment(org, interactions, opportunities)

    def meeting_brief(self, org: dict) -> dict:
        return ai_mock.meeting_brief(org)

    def summarize_notes(self, notes: str) -> dict:
        return ai_mock.summarize_notes(notes)

    def summarize_interaction_notes(self, notes: str, interaction_type: str) -> dict:
        return ai_mock.summarize_interaction_notes(notes, interaction_type)

    def generate_knowledge_summary(self, org: dict, interactions: list) -> dict:
        return ai_mock.generate_knowledge_summary(org, interactions)


_provider: Optional[AiProvider] = None


def get_ai_provider() -> AiProvider:
    global _provider
    if _provider is not None:
        return _provider
    mode = os.environ.get("AI_PROVIDER", "mock")
    if mode == "local_llm":
        _provider = LocalLlmProvider()
    elif mode == "openai":
        _provider = OpenAiProvider()
    else:
        _provider = MockProvider()
    logger.info(f"AI provider set to: {type(_provider).__name__}")
    return _provider
