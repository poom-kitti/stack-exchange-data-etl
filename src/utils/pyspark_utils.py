"""This module contains utiltiy functions for pyspark application."""
from dataclasses import dataclass
from typing import Dict, Optional

import tzlocal
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType

from . import datetime_utils as dt_utils
from . import logger as _logger

# Initiate logger
logger = _logger.get_default_logger(__name__)

MYSQL_DRIVER = "com.mysql.cj.jdbc.Driver"
POSTGRES_DRIVER = "org.postgresql.Driver"
MSSQL_DRIVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"


@dataclass
class JDBCConnectionConfig:
    """A data class to contain information to connect to a JDBC database."""

    db_type: str
    hostname: str
    port: str
    user: str
    password: str
    db_name: str
    driver: str

    @classmethod
    def create_mysql_config(cls, hostname: str, user: str, password: str, db_name: str, port: str = "3306"):
        """Create JDBC configuration to connect with MySQL database."""
        return cls(
            db_type="mysql",
            hostname=hostname,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
            driver=MYSQL_DRIVER,
        )

    @classmethod
    def create_postgres_config(cls, hostname: str, user: str, password: str, db_name: str, port: str = "5432"):
        """Create JDBC configuration to connect with Postgres database."""
        return cls(
            db_type="postgresql",
            hostname=hostname,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
            driver=POSTGRES_DRIVER,
        )

    @classmethod
    def create_mssql_config(cls, hostname: str, user: str, password: str, db_name: str, port: str = "5432"):
        """Create JDBC configuration to connect with MS SQL database."""
        return cls(
            db_type="sqlserver",
            hostname=hostname,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
            driver=MSSQL_DRIVER,
        )


def rename_columns(df: DataFrame, column_names_mapping: Dict[str, str]) -> DataFrame:
    """Rename the columns in the given dataframe with new column names.

    Args:
        df: The dataframe to perform renaming on.

        column_names_mapping: The mapping between old column name and new column name.
        Should be in format of {"old_column_name": "new_column_name"}.
    """
    for old_col_name, new_col_name in column_names_mapping.items():
        df = df.withColumnRenamed(old_col_name, new_col_name)

    return df


def from_datetime_to_timestamp(df: DataFrame, *cols: str) -> DataFrame:
    """Converts the datetime (timezone unaware) columns to correct UTC timestamp.

    Spark reads datetime and assume it is in the timezone of the system that is running
    the spark application. However, the timezone should be UTC, so time must be added
    or removed to move it back to the correct time.

    Example:
    The database keeps the data as `2020-01-01 09:00:00` which is in `UTC` timezone.
    If the system is `Asia/Bangkok` (+07:00), then Spark will assume that `2020-01-01 09:00:00`
    is in `Asia/Bangkok` timezone. So, to get the correct time, 7 hours must be added
    such that the final time in dataframe is `2020-01-01 16:00:00`.
    """
    # Find seconds difference of system timezone from UTC.
    # Positive if time is after UTC; otherwise, negative.
    seconds_from_utc = dt_utils.seconds_from_utc(tzlocal.get_localzone_name())

    for col in cols:
        df = df.withColumn(col, (F.unix_timestamp(col) + seconds_from_utc).cast(TimestampType()))

    return df


def read_db_table(
    spark: SparkSession,
    jdbc_config: JDBCConnectionConfig,
    table_name: str,
    additional_options: Optional[Dict[str, str]] = None,
) -> DataFrame:
    """Read a table from a database using JDBC driver. Options that are not 'url',
    'dbtable', 'driver', 'user', or 'password' should be passed through
    the additional_options argument.

    Args:
        spark: The spark session to perform the reading.

        jdbc_config: The connection detail to connect with teh database.

        table_name: The table to read from the database.

        additional_options: Additional options to provide for reading.
        Should be in the format of {"property_name": "value"}.
    """
    logger.info("Reading dataframe from table (%s) in database.", table_name)

    jdbc_uri = f"jdbc:{jdbc_config.db_type.lower()}://{jdbc_config.hostname}:{jdbc_config.port}/{jdbc_config.db_name}"

    read_properties = {
        "user": jdbc_config.user,
        "password": jdbc_config.password,
        "driver": jdbc_config.driver,
    }

    if additional_options is not None:
        # If additional_options contains same key as read_properties,
        # read_properties takes priority
        temp = additional_options.copy()
        temp.update(read_properties)
        read_properties = temp

    return spark.read.jdbc(jdbc_uri, table_name, properties=read_properties)


def write_df_to_db_table(
    df: DataFrame,
    jdbc_config: JDBCConnectionConfig,
    table_name: str,
    save_mode: str = "append",
    additional_options: Optional[Dict[str, str]] = None,
):
    """Write the given dataframe to a database table using JDBC driver. Options that are
    not 'url', 'dbtable', 'driver', 'user', or 'password' should be passed through
    the additional_options argument.

    Args:
        df: The dataframe to write to the table.

        jdbc_config: The connection detail to connect with teh database.

        table_name: The table to write to in the database.

        save_mode: The mode to write the dataframe to table. Default is `append`.

        additional_options: Additional options to provide for writing.
        Should be in the format of {"property_name": "value"}.
    """
    logger.info("Writing dataframe to table (%s) in database.", table_name)

    jdbc_uri = f"jdbc:{jdbc_config.db_type}://{jdbc_config.hostname}:{jdbc_config.port}/{jdbc_config.db_name}"

    write_properties = {
        "user": jdbc_config.user,
        "password": jdbc_config.password,
        "driver": jdbc_config.driver,
    }

    if additional_options is not None:
        # If additional_options contains same key as write_properties,
        # write_properties takes priority
        temp = additional_options.copy()
        temp.update(write_properties)
        write_properties = temp

    df.write.jdbc(
        url=jdbc_uri,
        table=table_name,
        mode=save_mode,
        properties=write_properties,
    )
