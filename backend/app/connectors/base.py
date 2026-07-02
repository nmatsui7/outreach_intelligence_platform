from abc import ABC, abstractmethod
from typing import List, Dict, Any


class CRMConnector(ABC):
    """Common interface for demo CRM storage and future external CRMs."""

    @abstractmethod
    def list_organizations(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_organization(self, organization_id: int) -> Dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, organization_id: int, status: str) -> Dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def add_organization(self, organization: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_org(self, organization_id: int, updates: Dict[str, Any]) -> Dict[str, Any] | None:
        raise NotImplementedError
