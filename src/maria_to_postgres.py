import os

import dotenv
from pyspark import SparkConf
from pyspark.sql import DataFrame, SparkSession

from .schema import orig_schema
from .utils import logger as _logger
from .utils.pyspark_utils import JDBCConnectionConfig

# Load dotenv
dotenv.load_dotenv(dotenv.find_dotenv())

# Configure logger
logger = _logger.get_default_logger(__name__)

conf = SparkConf()
conf.set("spark.jars", "jdbc_driver/mysql-connector-java-8.0.28.jar,jdbc_driver/postgresql-42.3.3.jar")

spark = SparkSession.builder.config(conf=conf).appName("data_preparation").master("local[*]").getOrCreate()


def read_table_from_maria_db(table_name: str, connection_config: JDBCConnectionConfig) -> DataFrame:
    """Read a given table from MariaDB as a spark dataframe."""
    # Connection to source database is given in
    # https://relational.fit.cvut.cz/dataset/Stats.
    return spark.read.jdbc(
        url=f"jdbc:mysql://{connection_config.hostname}:{connection_config.port}/{connection_config.db_name}",
        table=table_name,
        properties={
            "user": connection_config.username,
            "password": connection_config.password,
            "driver": "com.mysql.cj.jdbc.Driver",
            "fetchsize": "10000",
        },
    )


def write_df_to_postgres(df: DataFrame, table_name: str, connection_config: JDBCConnectionConfig) -> None:
    """Write the dataframe to Postgres."""
    df.write.jdbc(
        url=f"jdbc:postgresql://{connection_config.hostname}:{connection_config.port}/{connection_config.db_name}",
        table=table_name,
        mode="overwrite",
        properties={
            "user": connection_config.username,
            "password": connection_config.password,
            "driver": "org.postgresql.Driver",
            "batchsize": "10000",
        },  # type: ignore
    )


def main() -> None:
    """Main entry point."""
    logger.info("Initializing task to copy tables in stats database from MariaDB to Postgres.")

    source_db_config = JDBCConnectionConfig(
        hostname="relational.fit.cvut.cz", port="3306", username="guest", password="relational", db_name="stats"
    )
    destination_db_config = JDBCConnectionConfig(
        hostname=os.environ["POSTGRES_HOSTNAME"],
        port=os.environ["POSTGRES_PORT"],
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        db_name=os.environ["POSTGRES_DATABASE"],
    )

    for table_name in orig_schema.table_names:
        logger.info("Copying table (%s) from MariaDB to Postgres.", table_name)

        df = read_table_from_maria_db(table_name, source_db_config)
        write_df_to_postgres(df, table_name, destination_db_config)

        logger.info("Finish copying table (%s) from MariaDB to Postgres.", table_name)

    logger.info("Finish copying all tables in stats database from MariaDB to Postgres.")


if __name__ == "__main__":
    main()
