from typing import Any, Dict, List


MOCK_CANDIDATES = [
    {
        "organization_name": "Kitchener Public Library",
        "organization_type": "Public library",
        "website": "https://www.kpl.org",
        "general_contact_email": "askkpl@kpl.org",
        "phone_number": "(519) 555-0178",
        "program_area": "Digital literacy and community learning",
        "keywords": ["library", "digital literacy", "community", "workshop", "learning"],
    },
    {
        "organization_name": "Idea Exchange",
        "organization_type": "Public library and cultural hub",
        "website": "https://ideaexchange.org",
        "general_contact_email": "info@ideaexchange.org",
        "phone_number": "519-555-0213",
        "program_area": "Learning programs, makerspaces, and public workshops",
        "keywords": ["library", "makerspace", "workshop", "learning", "community"],
    },
    {
        "organization_name": "YW Kitchener-Waterloo",
        "organization_type": "Community nonprofit",
        "website": "https://ywkw.ca",
        "general_contact_email": "info@ywkw.ca",
        "phone_number": "+1 519 555 0237",
        "program_area": "Community services, housing, and youth programs",
        "keywords": ["nonprofit", "community", "youth", "support", "programs"],
    },
    {
        "organization_name": "Volunteer Waterloo Region",
        "organization_type": "Volunteer and nonprofit support organization",
        "website": "https://www.volunteerwr.ca",
        "general_contact_email": "info@volunteerwr.ca",
        "phone_number": "519-555-0132 ext. 204",
        "program_area": "Volunteer coordination and nonprofit capacity building",
        "keywords": ["nonprofit", "volunteer", "capacity", "coordination", "community"],
    },
    {
        "organization_name": "House of Friendship",
        "organization_type": "Social services nonprofit",
        "website": "https://houseoffriendship.org",
        "general_contact_email": "info@houseoffriendship.org",
        "phone_number": "(519) 555-0341",
        "program_area": "Community support, food, housing, and addiction services",
        "keywords": ["nonprofit", "social services", "community", "support", "housing"],
    },
    {
        "organization_name": "Capacity Canada",
        "organization_type": "Nonprofit capacity-building organization",
        "website": "https://capacitycanada.ca",
        "general_contact_email": "info@capacitycanada.ca",
        "phone_number": "519-555-0425",
        "program_area": "Governance, strategy, and nonprofit leadership support",
        "keywords": ["nonprofit", "capacity", "governance", "strategy", "leadership"],
    },
    {
        "organization_name": "Waterloo Region Small Business Centre",
        "organization_type": "Business support organization",
        "website": "https://www.waterlooregionsmallbusiness.com",
        "general_contact_email": "smallbusiness@waterloo.ca",
        "phone_number": "+1 519 555 0512",
        "program_area": "Small business advisory services and workshops",
        "keywords": ["business", "workshop", "advisory", "entrepreneurship", "support"],
    },
    {
        "organization_name": "Social Venture Partners Waterloo Region",
        "organization_type": "Philanthropy and nonprofit support network",
        "website": "https://www.socialventurepartners.org/waterloo-region",
        "general_contact_email": "info@svpwr.org",
        "phone_number": "(519) 555-0698",
        "program_area": "Nonprofit capacity building and social impact support",
        "keywords": ["nonprofit", "capacity", "social impact", "philanthropy", "strategy"],
    },
    {
        "organization_name": "Rare Charitable Research Reserve",
        "organization_type": "Environmental nonprofit",
        "website": "https://raresites.org",
        "general_contact_email": "rare@raresites.org",
        "phone_number": "(519) 555-0874",
        "program_area": "Environmental education, conservation, and research",
        "keywords": ["environment", "education", "research", "community", "workshop"],
    },
    {
        "organization_name": "Waterloo Region Community Foundation",
        "organization_type": "Community foundation",
        "website": "https://www.wrcf.ca",
        "general_contact_email": "info@wrcf.ca",
        "phone_number": "519-555-0962",
        "program_area": "Community funding, knowledge sharing, and social impact",
        "keywords": ["community", "funding", "nonprofit", "social impact", "knowledge"],
    },
]


def _score_candidate(theme_words: set[str], candidate: Dict[str, Any]) -> int:
    candidate_text = " ".join(
        [
            candidate["organization_name"],
            candidate["organization_type"],
            candidate["program_area"],
            " ".join(candidate["keywords"]),
        ]
    ).lower()
    matches = sum(1 for word in theme_words if word in candidate_text)
    return min(95, 68 + matches * 7 + min(len(theme_words), 5))


def discover_research_candidates(research_theme: str) -> Dict[str, Any]:
    theme = research_theme.strip() or "practical AI adoption support"
    theme_words = {word for word in theme.lower().replace("/", " ").split() if len(word) > 3}

    candidates = []
    for candidate in MOCK_CANDIDATES:
        fit_score = _score_candidate(theme_words, candidate)
        candidates.append(
            {
                "organization_name": candidate["organization_name"],
                "organization_type": candidate["organization_type"],
                "website": candidate["website"],
                "general_contact_email": candidate["general_contact_email"],
                "phone_number": candidate.get("phone_number", ""),
                "program_area": candidate["program_area"],
                "fit_score": fit_score,
                "why_it_may_be_relevant": (
                    f"{candidate['organization_name']} works in {candidate['program_area'].lower()}, "
                    f"which may connect to the research theme: {theme}."
                ),
                "suggested_outreach_angle": (
                    "Ask whether a small, human-reviewed AI workflow pilot could support "
                    "program planning, documentation, knowledge access, or follow-up coordination."
                ),
                "source_note": "Mock local candidate list for demo review only; not web-scraped.",
            }
        )

    candidates.sort(key=lambda row: row["fit_score"], reverse=True)
    return {"research_theme": theme, "candidates": candidates[:8]}
