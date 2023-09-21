# sqla-imperative-cookbook

Common patterns pre-cooked for SQLAlchemy Imperative mapping using python dataclasses.

For DDD using Python Dataclasses we will be using `imperative mapping` aka
`Classical` sqlalchemy.

Most of the SQLAlchemy documentation is focused on the "Declarative" mapping
approach, so I have built these examples as a reference and sandbox.

## Docs and articles

- [python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [sqlalchemy docs on mapping dataclasses](https://docs.sqlalchemy.org/en/14/orm/dataclasses.html#mapping-dataclasses-using-imperative-mapping)
- [Basic Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)

## Object modeling concept

The modeling is done in three pieces.

- dataclass: pure python dataclass object
- table definition: SQLAlchmeny Table definition
- properties: properties for columns in the Table definition

The three pieces are brought together in the 
`mapper_registry.map_imperatively` function to manage the database.

### Dataclass

```python
@dataclass
class User:
    name: str | None = None
    fullname: str | None = None
    nickname: str | None = None
    addresses: list[Address] = field(default_factory=list)
    uuid: str | None = None
```

### Table Definition

```python
user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
    Column("uuid", String(40), primary_key=True, default=lambda: str(uuid.uuid4())),
)
```

### Properties

```python
user_properties = {
    "addresses": relationship(  # references the "addresses" list on the dataclass
        Address,
        back_populates="user",  # reference to the "user" relationship property
        order_by=address_table.columns.uuid,
    ),
}
```

## The cookbook examples

Each of the cookbook examples is self-contained and executable.

```shell
poetry run python one_to_one.py
```

Any ide which can handle a pyproject.toml should be able to run them as well.

### one_to_one.py

`Soldier has a Rank`.

Simple ForeignKey relations between two objects

```python
"rank": relationship(Rank)
```

### one_to_many_backref.py

`User has a list of Addresses`.

Properties on User set up the "backref" connection to the addresses.

```python
user_properties = {
    "addresses": relationship(
        Address, backref="user", order_by=address_table.columns.id
    ),
}
```

### one_to_many_back_populates.py

`User has a list of Addresses`.

Similar effect as `backref` but requiring both sides be defined in the properties
for each table.

Additionally this example uses UUID4 strings as primary keys instead of Integers.

```python
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
```

### many_to_many_association_table.py

`Students have Courses, and Courses have Students`.

Student and Course objects both have lists of their related objects.
This "association" is managed with an additional table definition, which is
referenced as the "secondary" argument in the properties for each table.

```python
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
```

### many_to_many_multiple_keys.py

`Person can be either Student or Instructor on a QualificationRecord`.

Many to Many mapping between Student and Course with a join object
QualificationRecord acting as association table.

Student has a list of QualificationRecord as "qualifications", and a list of
QualificationRecord as "instructed".

With two keys mapping back to one object we have to take additional steps to
ensure clarity.

The `foreign_keys` argument to `relationship` takes a reference to the specific
table and column.

Notice how the `back_populates` arguments map to each other.

```python
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
```

`foreign_keys` expects a list of columns

- `qualification_record_table` is the Table definition,
- `c` is an alias for the `columns` property
- `instructor_uuid` is the specific column for the foreign key

### generic_relationship_example.py

todo

## lazy relationship settings

`relationship.lazy` parameter of `relationship()`

common values for this parameter include

- select
- joined
- subquery
- selectin

Documented in <https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.lazy>

## Relationship API

<https://docs.sqlalchemy.org/en/20/orm/relationship_api.html>

Some commonly seen arguments :

secondary
: For a many-to-many relationship, specifies the intermediary table, and is
typically an instance of `Table`. In less common circumstances, the argument may
also be specified as an `Alias` construct, or even a `Join` construct.
`relationship.secondary` may also be passed as a callable function which is
evaluated at mapper initialization time. When using Declarative, it may also be
a string argument noting the name of a Table that is present in the MetaData
collection associated with the parent-mapped Table.  # noqa

backref
: A reference to a string relationship name, or a `backref()` construct, which
will be used to automatically generate a new `relationship()` on the related
class, which then refers to this one using a bi-directional
`relationship.back_populates` configuration.
: In modern Python, explicit use of `relationship()` with
`relationship.back_populates` should be preferred, as it is more robust in
terms of mapper configuration as well as more conceptually straightforward.
It also integrates with new PEP 484 typing features introduced in SQLAlchemy 2.0
which is not possible with dynamically generated attributes.

back_populates
: Indicates the name of a `relationship()` on the related class that will be
synchronized with this one. It is usually expected that the `relationship()` on
the related class also refer to this one. This allows objects on both sides of
each `relationship()` to synchronize in-Python state changes and also provides
directives to the unit of work flush process how changes along these
relationships should be persisted.
