""" Many to Many with multiple foreign keys to the same model.

In this example, QualificationRecord has Person references to two fields:

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
class Person:
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
    student: Person
    instructor: Person
    event: Event
    course: Course
    timestamp: datetime = datetime.utcnow()
    uuid: str | None = None


person_table = Table(
    "person",
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
    Column("student_uuid", String(40), ForeignKey("person.uuid")),
    Column("instructor_uuid", String(40), ForeignKey("person.uuid")),
    Column("event_uuid", String(40), ForeignKey("event.uuid")),
    Column("course_uuid", String(40), ForeignKey("course.uuid")),
    Column("timestamp", DateTime),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)


qualification_record_properties = {
    "student": relationship(
        Person,
        back_populates="qualifications",
        foreign_keys=[qualification_record_table.c.student_uuid],
    ),
    "instructor": relationship(
        Person,
        back_populates="instructed",
        foreign_keys=[qualification_record_table.c.instructor_uuid],
    ),
    "event": relationship(Event),
    "course": relationship(Course),
}

person_properties = {
    "qualifications": relationship(
        QualificationRecord,
        back_populates="student",
        foreign_keys=[qualification_record_table.c.student_uuid],
    ),
    "instructed": relationship(
        QualificationRecord,
        back_populates="instructor",
        foreign_keys=[qualification_record_table.c.instructor_uuid],
    ),
}


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Person,
        person_table,
        properties=person_properties,
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
        student = Person(name="Student")
        instructor = Person(name="Instructor")
        course1 = Course(name="Course1")
        event1 = Event(name="Event1")

        session.add_all([student, instructor, course1, event1])

        session.commit()

        qual1 = QualificationRecord(
            student=student, event=event1, course=course1, instructor=instructor
        )
        session.add(qual1)
        session.commit()

        print(student)

        print("---")
        print(instructor)

        assert len(student.qualifications) == 1
        assert len(student.instructed) == 0
        assert len(instructor.qualifications) == 0
        assert len(instructor.instructed) == 1


if __name__ == "__main__":
    run()
