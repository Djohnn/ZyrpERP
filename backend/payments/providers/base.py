from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class IntentResult:
    reference: str
    status: str
    amount: Decimal


@dataclass(frozen=True)
class TransactionResult:
    reference: str
    status: str
    amount: Decimal
    fee: Decimal = Decimal('0.00')


class PaymentProvider(ABC):
    @abstractmethod
    def create_intent(self, *, amount, idempotency_key): ...

    @abstractmethod
    def capture(self, intent_reference, amount): ...

    @abstractmethod
    def cancel(self, intent_reference): ...

    @abstractmethod
    def refund(self, transaction_reference, amount): ...

    @abstractmethod
    def verify_signature(self, payload, signature): ...
