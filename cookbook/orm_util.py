from dataclasses import dataclass  # noqa

from sqlalchemy import Table
from sqlalchemy.orm import registry

mapper_registry = registry()


@dataclass
class TableMapping:
    dataclass: dataclass  # type: ignore[valid-type]
    table: Table
    properties: dict | None = None

    def __str__(self) -> str:
        return f"{self.dataclass}: {self.table}"
