from typing import List, Dict, Any
from .base import CRMConnector


class HubSpotConnector(CRMConnector):
    """Future HubSpot connector stub. No real API calls in this demo."""

    def list_organizations(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("HubSpot integration is a future enhancement.")

    def get_organization(self, organization_id: int) -> Dict[str, Any] | None:
        raise NotImplementedError("HubSpot integration is a future enhancement.")

    def update_status(self, organization_id: int, status: str) -> Dict[str, Any] | None:
        raise NotImplementedError("HubSpot integration is a future enhancement.")

    def add_organization(self, organization: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("HubSpot integration is a future enhancement.")
