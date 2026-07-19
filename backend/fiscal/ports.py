from abc import ABC, abstractmethod
from typing import NamedTuple

from fiscal.models import FiscalDocument, FiscalEmitter


class EmitResult(NamedTuple):
    provider_document_id: str
    raw_response: dict


class QueryResult(NamedTuple):
    status: str
    protocol: str | None
    xml_url: str | None
    pdf_url: str | None
    error_reason: str | None


class CancelResult(NamedTuple):
    success: bool
    protocol: str | None


class FiscalProvider(ABC):
    @abstractmethod
    def emit(
        self,
        tenant,
        emitter: FiscalEmitter,
        document: FiscalDocument,
        items: list,
        payments: list,
    ) -> EmitResult: ...

    @abstractmethod
    def query(self, tenant, provider_document_id: str) -> QueryResult: ...

    @abstractmethod
    def cancel(self, tenant, provider_document_id: str) -> CancelResult: ...
