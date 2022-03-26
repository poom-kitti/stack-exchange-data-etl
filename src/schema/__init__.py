"""This module contains the initialization of SQLAlchemy ORM base classes."""
from typing import List, Type

from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import MetaData, Table


class SABase:
    """Base class for SQL Alchemy table that contains useful utility functions.

    Should never be directly inherited when creating new `Base` class for a
    database. Import `Base` instead.
    """

    __tablename__: str
    __table__: Table
    metadata: MetaData

    @classmethod
    def get_column_names(cls) -> List[str]:
        """Get the column names of this table."""
        return cls.__table__.columns.keys()

    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name of this table."""
        return cls.__tablename__


Base: Type[SABase] = declarative_base(cls=SABase, name="Base")
