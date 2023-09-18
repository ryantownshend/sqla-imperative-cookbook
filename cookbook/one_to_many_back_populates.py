from __future__ import annotations

from dataclasses import dataclass, field

from rich import print
from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import Session, registry, relationship

mapper_registry = registry()


@dataclass
class User:
    """Notice this is really just a one way relationship.
    User has a list of Addresses, but in the dataclass Address doesn't have a
    reference to the User. In the db this is a foreignkey but bi-directional
    relations can be really messy in the object graph.
    """

    id: int = field(init=False)
    name: str | None = None
    fullname: str | None = None
    nickname: str | None = None
    addresses: list[Address] = field(default_factory=list)


@dataclass
class Address:
    id: int = field(init=False)
    email_address: str | None = None


user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
)

address_table = Table(
    "address",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("email_address", String(50)),
)

user_properties = {
    "addresses": relationship(
        Address,
        back_populates="user",
        order_by=address_table.columns.id,
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
        print(user)

        add1 = session.get(Address, 1)
        print(add1)

    print(address_table.c)
    # sqlalchemy.orm.Bundle.c: ReadOnlyColumnCollection
    # an alias for Bundle.columns

    # print("---")
    # for item in dir(address_table):
    #     print(item)


if __name__ == "__main__":
    run()
