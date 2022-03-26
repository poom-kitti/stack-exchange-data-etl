"""A module containing connector class to connect with Postgres database
through using sqlalchemy. The underlying driver used is psycopg2.
"""
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator, Mapping, Sequence, Union

import sqlalchemy as sa
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session
from sqlalchemy.schema import MetaData

from . import logger as _logger

logger = _logger.get_default_logger(__name__)


@dataclass
class SQLAlchemyConnectionConfig:
    """A configuration class for making connection to database using SQLAlchemy."""

    db_type: str  # postgres / mssql
    hostname: str
    port: int
    username: str
    password: str
    db_name: str
    query: Mapping[str, Union[str, Sequence[str]]] = field(default_factory=dict)

    @classmethod
    def create_mssql_config(cls, hostname: str, username: str, password: str, db_name: str, port: int = 1433):
        """Create SQLAlchemy configuration to connect with MS SQL (SQL Server)."""
        db_type = "mssql"
        query = {"driver": "ODBC Driver 17 for SQL Server"}
        return cls(db_type, hostname, port, username, password, db_name, query)

    @classmethod
    def create_postgres_config(cls, hostname: str, username: str, password: str, db_name: str, port: int = 5432):
        """Create SQLAlchemy configuration to connect with Postgres."""
        db_type = "postgres"
        return cls(db_type, hostname, port, username, password, db_name)


def connect_to_db(connection_config: SQLAlchemyConnectionConfig) -> Engine:
    """Create a sqlalchemy engine to connect with the database.
    The underlying drivers are as follow:
        - Postgres: psycopg2
        - MS SQL: pyodbc
    """
    if connection_config.db_type not in ("postgres", "mssql"):
        logger.error("Invalid `db_type` (%s). Must either be 'postgres' or 'mssql'.", connection_config.db_type)
        raise ValueError(f"`db_type` ({connection_config.db_type}) is not 'postgres' or 'mssql'.")

    logger.info("Making connection to %s database.", connection_config.db_type)

    driver_name = "postgresql+psycopg2" if connection_config.db_type == "postgres" else "mssql+pyodbc"

    connection_url = URL.create(
        drivername=driver_name,
        host=connection_config.hostname,
        port=connection_config.port,
        username=connection_config.username,
        password=connection_config.password,
        database=connection_config.db_name,
        query=connection_config.query,
    )

    return sa.create_engine(connection_url)


class SQLAlchemyConnector:
    """A class using sqlalchemy to connect to Postgres or MS SQL database. Provide
    logging and methods to execute SQL statements.

    Attributes:
        engine: The SQLAlchemy engine that connects to the database.
        metadata: The metadata holding information on the tables.
    """

    def __init__(self, connection_config: SQLAlchemyConnectionConfig, metadata: MetaData):
        self.engine = connect_to_db(connection_config)
        self.metadata = metadata

    def create_all_tables(self) -> None:
        """Create all tables defined in the metadata in the database.

        If any table is already presented in the database, skip creating that
        table.
        """
        logger.info("Creating in database according to metadata.")
        self.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        """Drop all tables defined in the metadata in the database.

        If any table is not presented in the database, skip dropping that
        table.
        """
        logger.info("Dropping tables in database according to metadata.")
        self.metadata.drop_all(self.engine)

    def close(self) -> None:
        """Close the engine connection with the database."""
        logger.info("Closing engine connection to database.")

        self.engine.dispose()

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Get the session to interact with the database."""
        with Session(self.engine) as session, session.begin():
            try:
                yield session
            finally:
                session.commit()
