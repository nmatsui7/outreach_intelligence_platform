from typing import List, Dict, Any
from .base import CRMConnector


class SalesforceConnector(CRMConnector):
    """
    Future connector stub.

    Intended role:
    - Read accounts/contacts from Salesforce
    - Push notes, tasks, and status updates back to Salesforce
    - Keep AI services independent from the CRM vendor

    This demo intentionally does not include authentication or real API calls.
    """

    def list_organizations(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Salesforce integration is a future enhancement.")

    def get_organization(self, organization_id: int) -> Dict[str, Any] | None:
        raise NotImplementedError("Salesforce integration is a future enhancement.")

    def update_status(self, organization_id: int, status: str) -> Dict[str, Any] | None:
        raise NotImplementedError("Salesforce integration is a future enhancement.")

    def add_organization(self, organization: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Salesforce integration is a future enhancement.")
