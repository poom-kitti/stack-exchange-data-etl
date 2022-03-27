"""This module is an application that copy `stats` data from https://relational.fit.cvut.cz/dataset/Stats
to Postgres database.
"""
import os

from pyspark import SparkConf
from pyspark.sql import SparkSession

from .schemas import orig_schema
from .utils import logger as _logger
from .utils import pyspark_utils
from .utils.pyspark_utils import JDBCConnectionConfig

# Configure logger
logger = _logger.get_default_logger(__name__)

# Initiate JDBC configs
# Connection to source database is given in
# https://relational.fit.cvut.cz/dataset/Stats.
source_db_config = JDBCConnectionConfig.create_mysql_config(
    hostname="relational.fit.cvut.cz", port="3306", user="guest", password="relational", db_name="stats"
)
destination_db_config = JDBCConnectionConfig.create_postgres_config(
    hostname=os.environ["POSTGRES_HOSTNAME"],
    port=os.environ["POSTGRES_PORT"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    db_name=os.environ["POSTGRES_DATABASE"],
)

# Configure spark
conf = SparkConf()
conf.set("spark.jars", "jdbc_driver/mysql-connector-java-8.0.28.jar,jdbc_driver/postgresql-42.3.3.jar")

spark = SparkSession.builder.config(conf=conf).appName("data_preparation").master("local[*]").getOrCreate()


def main() -> None:
    """Main entry point."""
    logger.info("Initializing task to copy tables in stats database from MariaDB to Postgres.")

    for table_name in orig_schema.table_names:
        logger.info("Copying table (%s) from MariaDB to Postgres.", table_name)

        df = pyspark_utils.read_db_table(spark, source_db_config, table_name, {"fetchsize": "10000"})
        pyspark_utils.write_df_to_db_table(df, destination_db_config, table_name, "overwrite", {"batchsize": "10000"})

        logger.info("Finish copying table (%s) from MariaDB to Postgres.", table_name)

    logger.info("Finish copying all tables in stats database from MariaDB to Postgres.")


if __name__ == "__main__":
    main()
