""" TODO
- https://stackoverflow.com/questions/75078544/sqlalchemy-imperative-mapping-many-to-many-relationship
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rich.console import Console
from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import Session, registry, relationship

console = Console()
mapper_registry = registry()


@dataclass
class Student:
    id: int = field(init=False)
    name: str
    courses: list[Course] = field(default_factory=list)


@dataclass
class Course:
    id: int = field(init=False)
    name: str
    students: list[Student] = field(default_factory=list)


student_table = Table(
    "student",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
)

course_table = Table(
    "course",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
)

assoc_table = Table(
    "course_student_association",
    mapper_registry.metadata,
    Column("student_id", Integer, ForeignKey("student.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("course.id"), primary_key=True),
)


student_properties = {
    "courses": relationship(
        Course,
        secondary=assoc_table,
        back_populates="students",
    ),
}

course_properties = {
    "students": relationship(
        Student,
        secondary=assoc_table,
        back_populates="courses",
    )
}


def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Student,
        student_table,
        properties=student_properties,
    )

    mapper_registry.map_imperatively(
        Course,
        course_table,
        properties=course_properties,
    )


def run() -> None:
    console.print("run")
    engine = create_engine("sqlite://", echo=True)
    start_mappers()
    mapper_registry.metadata.create_all(engine)

    with Session(engine) as session:
        student1 = Student(name="Student1")
        student2 = Student(name="Student2")
        student3 = Student(name="Student3")
        session.add_all([student1, student2, student3])
        course1 = Course(name="Course1")
        course2 = Course(name="Course2")
        session.add_all([course1, course2])

        student1.courses.append(course1)
        student2.courses.append(course1)
        session.commit()

        c1_product = session.get(Course, 1)
        s1_product = session.get(Student, 1)
        s3_product = session.get(Student, 3)

        if c1_product is not None:
            assert c1_product.id is not None

        console.print(c1_product)
        console.print(s1_product)
        if s1_product is not None:
            console.print(s1_product)
            console.print(s1_product.courses)
        console.print(s3_product)


if __name__ == "__main__":
    run()
