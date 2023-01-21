from dataclasses import dataclass
from uuid import UUID


@dataclass
class ValueObject:
    uuid: UUID
    data: str
    id: int = None
