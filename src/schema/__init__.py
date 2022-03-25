"""SQLAlchemy table schema definitions."""

import dataclasses
from abc import ABC
from typing import ClassVar, List, Mapping

from pyspark.sql import DataFrame
from sqlalchemy.schema import Column, Constraint, MetaData, SchemaItem, Table


class AlchemyTable(ABC):
    """A base class for all tables.

    Table classes should be data classes and extend this base class.
    Table classes itself represent the schema of a table.
    """

    table_name: ClassVar[str]
    table_constraints: ClassVar[List[Constraint]] = []
    table_config: ClassVar[Mapping] = {}

    @classmethod
    def bind_to_metadata(cls, metadata: MetaData) -> Table:
        """Bind the table to given metadata."""
        columns = [Column(**field.metadata) for field in dataclasses.fields(cls)]

        args: List[SchemaItem] = columns + cls.table_constraints  # type: ignore

        return Table(cls.table_name, metadata, *args, **cls.table_config)

    @classmethod
    def column_names(cls) -> List[str]:
        """The list of column names of this table"""

        return [field.metadata.get("name") for field in dataclasses.fields(cls)]

    @classmethod
    def select_from(cls, df: DataFrame) -> DataFrame:
        """Select only the columns that related to the table from the given
        dataframe `df`.
        """
        return df.select(*cls.column_names())
