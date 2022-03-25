"""A module containing connector class to connect with Postgres database
through using sqlalchemy. The underlying driver used is psycopg2.
"""
from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional, Union, Sequence

import sqlalchemy as sa
from sqlalchemy.engine import URL, CursorResult, Engine, Row
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.sql.expression import ClauseElement

from ..schema import AlchemyTable
from . import logger as _logger

logger = _logger.get_default_logger(__name__)


@dataclass
class SQLAlchemyConnectionConfig:
    db_type: str  # postgres / mssql
    hostname: str
    port: int
    username: str
    password: str
    db_name: str
    query: Mapping[str, Union[str, Sequence[str]]] = field(default_factory=dict)

    @classmethod
    def create_mssql_config(cls, hostname: str, username: str, password: str, db_name: str, port: int = 1433):
        db_type = "mssql"
        query = {"driver": "ODBC Driver 17 for SQL Server"}
        return cls(db_type, hostname, port, username, password, db_name, query)

    @classmethod
    def create_postgres_config(cls, hostname: str, username: str, password: str, db_name: str, port: int = 5432):
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
    """

    def __init__(self, connection_config: SQLAlchemyConnectionConfig):
        self.engine = connect_to_db(connection_config)
        self.metadata = MetaData(bind=self.engine)

    def close(self):
        """Close the engine connection with the postgres database."""
        logger.info("Closing engine connection to postgres.")

        self.engine.dispose()

    def add_table_schema(self, table: AlchemyTable) -> Table:
        """Add the table schema to the class metadata.

        Args:
            table_name: The name of the table.

            *cols: The column
        """
        return table.bind_to_metadata(self.metadata)

    def get_table_schema_from_db(self, table_name: str, extend_existing: bool = True) -> Table:
        """Get the schema of an existing table from the database and add it to the class metadata.

        Args:
            table_name: The name of the table in the database to get the schema of.

            extend_existing: A flag to indicate whether to extend (add additional arguments)
                the table schema if it already existed in the metadata. If set to True,
                newly retrieved schema from database may potentially overwrite existing columns
                and options of the table in metadata.

        Raises:
            SQLAlchemyError: If unable to get the table schema.
        """
        logger.info("Getting schema of table (%s).", table_name)

        try:
            return sa.Table(table_name, self.metadata, autoload_with=self.engine, extend_existing=extend_existing)
        except SQLAlchemyError as error:
            logger.exception("Unable to get schema of table (%s).", table_name)
            raise error

    def get_table(self, table_name: str) -> Table:
        """Get the table from the class metadata.

        Raises:
            ValueError: If the `table_name` does not exists the class metadata.
        """
        tables: Dict[str, Table] = self.metadata.tables

        if table_name not in tables:
            logger.error("Table name (%s) does not exists in the metadata.", self.metadata)
            raise ValueError(f"`table_name` ({table_name}) does not exist in metadata.")

        return tables[table_name]

    def create_tables(self) -> None:
        """Create all the tables present in the class metadata. If any table already exists in the database,
        then the creation of that table will be skipped.
        """
        self.metadata.create_all(self.engine, checkfirst=True)

    def execute_one(self, sql_stmt: ClauseElement):
        """Execute a single sql statement as transaction."""
        logger.info("Executing a single SQL statement as transaction.")
        try:
            # Running as a transaction
            with self.engine.begin() as conn:
                conn.execute(sql_stmt)
        except SQLAlchemyError as error:
            logger.exception("Unable to execute the SQL statement.")
            raise error

    def fetch_one(self, sql_stmt: ClauseElement) -> Optional[Row]:
        """Fetch a single row from the result of the SQL statement."""
        logger.info("Fetching a single row from result of SQL statement.")
        try:
            # Running as a transaction
            with self.engine.begin() as conn:
                res: CursorResult = conn.execute(sql_stmt)
                return res.first()
        except SQLAlchemyError as error:
            logger.exception("Unable to execute the SQL statement.")
            raise error
