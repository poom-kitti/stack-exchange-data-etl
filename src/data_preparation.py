"""This module is an application that extract `stats` data from Postgres database,
perform transformations, and load the data into MS SQL (SQL Server) database."""
import os

from pyspark import SparkConf
from pyspark.sql import SparkSession

from .schemas.stats_schema import (Badges, BaseStats, Comments,
                                   PostHistoryTypes, PostHitories, PostLinks,
                                   PostLinkTypes, Posts, PostsAnswers,
                                   PostsTags, PostTypes, Tags, Users,
                                   UsersBadges, Votes, VoteTypes)
from .transformations import stats_transformation as transformation
from .utils import logger as _logger
from .utils.pyspark_utils import JDBCConnectionConfig
from .utils.sqlalchemy_connector import (SQLAlchemyConnectionConfig,
                                         SQLAlchemyConnector)

# Initiate logger
logger = _logger.get_default_logger(__name__)

# Initiate JDBC configs
source_db_config = JDBCConnectionConfig.create_postgres_config(
    hostname=os.environ["POSTGRES_HOSTNAME"],
    port=os.environ["POSTGRES_PORT"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    db_name=os.environ["POSTGRES_DATABASE"],
)
destination_db_config = JDBCConnectionConfig.create_mssql_config(
    hostname=os.environ["MSSQL_HOSTNAME"],
    port=os.environ["MSSQL_PORT"],
    user=os.environ["MSSQL_USER"],
    password=os.environ["MSSQL_PASSWORD"],
    db_name=os.environ["MSSQL_DATABASE"],
)

# Inititate SQLAlchemy connection config (for destination database)
alchemy_mssql_conn_config = SQLAlchemyConnectionConfig.create_mssql_config(
    hostname=os.environ["MSSQL_HOSTNAME"],
    username=os.environ["MSSQL_USER"],
    password=os.environ["MSSQL_PASSWORD"],
    db_name=os.environ["MSSQL_DATABASE"],
)

# Configure spark
conf = SparkConf()
conf.set("spark.jars", "jdbc_driver/mssql-jdbc-10.2.0.jre8.jar,jdbc_driver/postgresql-42.3.3.jar")
conf.set("spark.sql.session.timeZone", "Asia/Bangkok")

spark = SparkSession.builder.config(conf=conf).appName("data_preparation").master("local[*]").getOrCreate()


def log_loading_table(table_name: str) -> None:
    """Make a log that the table is being loaded from source to destination database."""
    logger.info("Loading `%s` table.", table_name)


def main() -> None:
    """The main entry point to the application."""
    mssql_conn = None
    try:
        # BaseStats.metadata contains information of wanted tables
        mssql_conn = SQLAlchemyConnector(alchemy_mssql_conn_config, BaseStats.metadata)

        # Use SQLAlchemy to create tables beforehand as pyspark cannot set PK / FK
        mssql_conn.drop_all_tables()
        mssql_conn.create_all_tables()
    finally:
        if mssql_conn:
            mssql_conn.close()

    log_loading_table(Users.get_table_name())
    transformation.load_users_table(spark, source_db_config, destination_db_config)

    log_loading_table(Badges.get_table_name())
    transformation.load_badges_table(spark, source_db_config, destination_db_config)

    log_loading_table(UsersBadges.get_table_name())
    transformation.load_users_badges_table(spark, source_db_config, destination_db_config)

    log_loading_table(PostTypes.get_table_name())
    transformation.load_post_types_table(spark, destination_db_config)

    log_loading_table(Posts.get_table_name())
    transformation.load_posts_table(spark, source_db_config, destination_db_config)

    log_loading_table(PostsAnswers.get_table_name())
    transformation.load_posts_answers_table(spark, source_db_config, destination_db_config)

    log_loading_table(Comments.get_table_name())
    transformation.load_comments_table(spark, source_db_config, destination_db_config)

    log_loading_table(Tags.get_table_name())
    transformation.load_tags_table(spark, source_db_config, destination_db_config)

    log_loading_table(PostsTags.get_table_name())
    transformation.load_posts_tags_table(spark, source_db_config, destination_db_config)

    log_loading_table(VoteTypes.get_table_name())
    transformation.load_vote_types_table(spark, destination_db_config)

    log_loading_table(Votes.get_table_name())
    transformation.load_votes_table(spark, source_db_config, destination_db_config)

    log_loading_table(PostLinkTypes.get_table_name())
    transformation.load_post_link_types_table(spark, destination_db_config)

    log_loading_table(PostLinks.get_table_name())
    transformation.load_post_links_table(spark, source_db_config, destination_db_config)

    log_loading_table(PostHistoryTypes.get_table_name())
    transformation.load_post_history_types_table(spark, destination_db_config)

    log_loading_table(PostHitories.get_table_name())
    transformation.load_post_histories_table(spark, source_db_config, destination_db_config)


if __name__ == "__main__":
    main()
