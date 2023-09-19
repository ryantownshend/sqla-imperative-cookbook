# sqla-imperative-cookbook

Common patterns pre-cooked for SQLAlchemy Imperative mapping using python dataclasses.

For DDD using Python Dataclasses we will be using `imperative mapping` aka
`Classical` sqlalchemy.

- [python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [sqlalchemy docs on mapping dataclasses](https://docs.sqlalchemy.org/en/14/orm/dataclasses.html#mapping-dataclasses-using-declarative-with-imperative-table)
- [Basic Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)

## Lessons learned

For the purposes of mapping tables to an object graph of dataclasses, database
relationship should generally be one way.

The repository will return our Aggregate object with relationships already
mapped, thus circular relations will pointlessly populate. This concept is
demonstrated in the `many_to_many_example.py` which maps Parent and Child to
each other.

```text
Parent(name='parent 1', id='64e57282-2277-44e3-9166-94babb5b33e8', 
children=[
    Child(name='child 1', id='0a8aedce-f64e-4883-8be1-811f975a5740', parents=[...])])
--- circular silliness ---
Child(name='child 1', id='0a8aedce-f64e-4883-8be1-811f975a5740',
    parents=[Parent(name='parent 1', id='64e57282-2277-44e3-9166-94babb5b33e8', children=[...])])
Parent(name='parent 1', id='64e57282-2277-44e3-9166-94babb5b33e8',
    children=[Child(name='child 1', id='0a8aedce-f64e-4883-8be1-811f975a5740', parents=[...])])
```

For a DDD Aggregate we don't need this reference back to our root object.
The foreign keys in the database are used to populate the object lists as
needed.

The `one_to_many_backref.py` example avoids this.

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
