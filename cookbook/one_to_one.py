from __future__ import annotations

from dataclasses import dataclass, field

from rich import print
from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import Session, registry, relationship

mapper_registry = registry()


@dataclass
class Soldier:
    id: int = field(init=False)
    name: str
    rank: Rank


@dataclass
class Rank:
    id: int = field(init=False)
    name: str
    acronym: str


soldier_table = Table(
    "soldier",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("rank_id", ForeignKey("rank.id")),
)

rank_table = Table(
    "rank",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("acronym", String(50)),
)

soldier_properties = {
    "rank": relationship(Rank),
}


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Soldier,
        soldier_table,
        properties=soldier_properties,
    )

    mapper_registry.map_imperatively(
        Rank,
        rank_table,
    )


def run() -> None:
    print("run")
    engine = create_engine("sqlite://", echo=True)
    start_mappers()
    mapper_registry.metadata.create_all(engine)

    with Session(engine) as session:
        rank1 = Rank(name="Private", acronym="PVT")
        rank2 = Rank(name="Corporal", acronym="CPL")
        rank3 = Rank(name="Sergeant", acronym="SGT")
        soldier1 = Soldier(name="Soldier1", rank=rank1)
        session.add_all([rank1, rank2, rank3, soldier1])
        session.commit()

        s1_product = session.get(Soldier, 1)
        print(s1_product)


if __name__ == "__main__":
    run()
