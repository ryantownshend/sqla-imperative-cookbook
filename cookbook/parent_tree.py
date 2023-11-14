"""
- https://docs.sqlalchemy.org/en/20/orm/self_referential.html
- https://docs.sqlalchemy.org/en/20/_modules/examples/adjacency_list/adjacency_list.html
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rich import print
from rich.console import Console
from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import Session, registry, relationship

console = Console()
mapper_registry = registry()


@dataclass
class Node:
    name: str
    id: int = field(init=False)
    parent: Node | None = None
    children: list[Node] = field(default_factory=list)


node_table = Table(
    "node",
    mapper_registry.metadata,
    Column("name", String(50)),
    Column("id", Integer, primary_key=True),
    Column("parent_id", Integer, ForeignKey("node.id")),
)

node_properties = {
    "children": relationship(Node, back_populates="parent"),
    "parent": relationship(Node, remote_side=[node_table.columns.id], back_populates="children"),
}


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Node,
        node_table,
        properties=node_properties,
    )


def run() -> None:
    print("run")
    engine = create_engine("sqlite://", echo=True)
    start_mappers()
    mapper_registry.metadata.create_all(engine)

    with Session(engine) as session:
        print("gak")
        node = Node(name="root")
        node1 = Node(name="node1", parent=node)
        node2 = Node(name="node2", parent=node)

        session.add_all([node, node1, node2])
        session.commit()

        console.print(node)


if __name__ == "__main__":
    run()
