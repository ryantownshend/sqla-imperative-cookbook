from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from rich import print
from sqlalchemy import Column, ForeignKey, String, Table, create_engine
from sqlalchemy.orm import Session, registry, relationship

mapper_registry = registry()


@dataclass
class User:
    """Notice this is really just a one way relationship.
    User has a list of Addresses, but in the dataclass Address doesn't have a
    reference to the User. In the db this is a foreignkey but bi-directional
    relations can be really messy in the object graph.
    """

    name: str | None = None
    fullname: str | None = None
    nickname: str | None = None
    addresses: list[Address] = field(default_factory=list)
    # uuid maps to a generated UUID key in the orm
    uuid: str | None = None


@dataclass
class Address:
    email_address: str | None = None
    uuid: str | None = None


user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
    # With a new object we generate a UUID4
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)

address_table = Table(
    "address",
    mapper_registry.metadata,
    Column("user_id", String(40), ForeignKey("user.uuid")),
    Column("email_address", String(50)),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)

user_properties = {
    "addresses": relationship(
        Address,
        back_populates="user",
        order_by=address_table.columns.uuid,
    ),
}


address_properties = {
    "user": relationship(
        User,
        back_populates="addresses",
    ),
}


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        User,
        user_table,
        properties=user_properties,
    )

    mapper_registry.map_imperatively(
        Address,
        address_table,
        properties=address_properties,
    )


def run() -> None:
    print("run")
    engine = create_engine("sqlite://", echo=True)
    start_mappers()
    mapper_registry.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(name="name", fullname="fullname", nickname="nickname")
        session.add(user)

        user.addresses.append(Address(email_address="email1"))
        user.addresses.append(Address(email_address="email2"))
        user.addresses.append(Address(email_address="email3"))
        user.addresses.append(Address(email_address="email4"))

        session.commit()

        assert user.uuid is not None
        assert len(user.addresses) == 4

        print(user)

        print(address_table.c.uuid)


if __name__ == "__main__":
    run()
