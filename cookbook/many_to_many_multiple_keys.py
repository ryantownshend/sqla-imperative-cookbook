""" Many to Many with multiple foreign keys to the same model.

In this example, QualificationRecord has Player references to two fields:

- "student"
- "instructor"

We get this functional with use of the relationship foreign_keys argument


- https://stackoverflow.com/questions/75078544/sqlalchemy-imperative-mapping-many-to-many-relationship


"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from rich import print
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import Session, registry, relationship

mapper_registry = registry()


@dataclass
class Player:
    name: str
    qualifications: list[QualificationRecord] = field(default_factory=list)
    instructed: list[QualificationRecord] = field(default_factory=list)
    uuid: str | None = None


@dataclass
class Event:
    name: str
    uuid: str | None = None


@dataclass
class Course:
    name: str
    uuid: str | None = None


@dataclass
class QualificationRecord:
    player: Player
    instructor: Player
    event: Event
    course: Course
    timestamp: datetime = datetime.utcnow()
    uuid: str | None = None


player_table = Table(
    "player",
    mapper_registry.metadata,
    Column("name", String(50)),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)

event_table = Table(
    "event",
    mapper_registry.metadata,
    Column("name", String(50)),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)

course_table = Table(
    "course",
    mapper_registry.metadata,
    Column("name", String(50)),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)


qualification_record_table = Table(
    "qualification_record",
    mapper_registry.metadata,
    Column("player_uuid", String(40), ForeignKey("player.uuid")),
    Column("instructor_uuid", String(40), ForeignKey("player.uuid")),
    Column("event_uuid", String(40), ForeignKey("event.uuid")),
    Column("course_uuid", String(40), ForeignKey("course.uuid")),
    Column("timestamp", DateTime),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)


qualification_record_properties = {
    "player": relationship(
        Player,
        back_populates="qualifications",
        foreign_keys=[qualification_record_table.c.player_uuid],
    ),
    "instructor": relationship(
        Player,
        back_populates="instructed",
        foreign_keys=[qualification_record_table.c.instructor_uuid],
    ),
    "event": relationship(Event),
    "course": relationship(Course),
}

player_properties = {
    "qualifications": relationship(
        QualificationRecord,
        back_populates="player",
        foreign_keys=[qualification_record_table.c.player_uuid],
    ),
    "instructed": relationship(
        QualificationRecord,
        back_populates="instructor",
        foreign_keys=[qualification_record_table.c.instructor_uuid],
    ),
}


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Player,
        player_table,
        properties=player_properties,
    )

    mapper_registry.map_imperatively(
        Event,
        event_table,
    )

    mapper_registry.map_imperatively(
        Course,
        course_table,
    )

    mapper_registry.map_imperatively(
        QualificationRecord,
        qualification_record_table,
        properties=qualification_record_properties,
    )


def run() -> None:
    print("run")
    engine = create_engine("sqlite://", echo=True)
    start_mappers()
    mapper_registry.metadata.create_all(engine)

    with Session(engine) as session:
        player1 = Player(name="Student")
        player2 = Player(name="Instructor")
        course1 = Course(name="Course1")
        event1 = Event(name="Event1")

        session.add_all([player1, player2, course1, event1])

        session.commit()

        qual1 = QualificationRecord(
            player=player1, event=event1, course=course1, instructor=player2
        )
        session.add(qual1)
        session.commit()

        print(player1)

        print("---")
        print(player2)


if __name__ == "__main__":
    run()
