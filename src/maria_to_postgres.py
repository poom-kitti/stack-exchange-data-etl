import os

import dotenv
import pyspark.sql.functions as F
from pyspark import SparkConf
from pyspark.sql import DataFrame, SparkSession

from .schema import orig_schema
from .utils import logger as _logger

# Load dotenv
dotenv.load_dotenv(dotenv.find_dotenv())

# Configure logger
logger = _logger.get_default_logger(__name__)

conf = SparkConf()
conf.set("spark.jars", "jdbc_driver/mysql-connector-java-8.0.28.jar,jdbc_driver/postgresql-42.3.3.jar")

spark = SparkSession.builder.config(conf=conf).appName("data_preparation").master("local[*]").getOrCreate()


def read_table_from_maria_db(spark: SparkSession, table_name: str) -> DataFrame:
    """Read a given table from MariaDB as a spark dataframe."""
    # Connection to source database is given in
    # https://relational.fit.cvut.cz/dataset/Stats.
    return spark.read.jdbc(
        url="jdbc:mysql://relational.fit.cvut.cz:3306/stats",
        table=table_name,
        properties={
            "user": "guest",
            "password": "relational",
            "driver": "com.mysql.cj.jdbc.Driver",
            "fetchsize": "10000",
        },
    )


def write_df_to_postgres(df: DataFrame, table_name: str) -> None:
    """Write the dataframe to Postgres."""
    df.write.jdbc(
        url=f"jdbc:postgresql://{os.getenv('POSTGRES_HOSTNAME')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DATABASE')}",
        table=table_name,
        mode="overwrite",
        properties={
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "driver": "org.postgresql.Driver",
            "batchsize": "10000",
        },  # type: ignore
    )


def main() -> None:
    """Main entry point."""
    logger.info("Initializing task to copy tables in stats database from MariaDB to Postgres.")

    for table_name in orig_schema.table_names:
        logger.info("Copying table (%s) from MariaDB to Postgres.", table_name)

        df = read_table_from_maria_db(spark, table_name)
        write_df_to_postgres(df, table_name)

        logger.info("Finish copying table (%s) from MariaDB to Postgres.", table_name)

    logger.info("Finish copying all tables in stats database from MariaDB to Postgres.")


if __name__ == "__main__":
    main()
