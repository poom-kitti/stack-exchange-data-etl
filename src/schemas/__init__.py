"""This module contains the initialization of SQLAlchemy ORM base classes."""
from typing import List, Type

from pyspark.sql import DataFrame
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

    @classmethod
    def select_from_df(cls, df: DataFrame) -> DataFrame:
        """Select only the columns needed by the table from the given dataframe."""
        return df.select(cls.get_column_names())


Base: Type[SABase] = declarative_base(cls=SABase, name="Base")
