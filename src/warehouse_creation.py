import os

from .schemas.warehouse_schema import BaseWarehouse
from .utils import logger as _logger
from .utils.sqlalchemy_connector import (SQLAlchemyConnectionConfig,
                                         SQLAlchemyConnector)

# Initiate logger
logger = _logger.get_default_logger(__name__)

# Inititate SQLAlchemy connection config (for warehouse database)
alchemy_mssql_conn_config = SQLAlchemyConnectionConfig.create_mssql_config(
    hostname=os.environ["MSSQL_HOSTNAME"],
    username=os.environ["MSSQL_USER"],
    password=os.environ["MSSQL_PASSWORD"],
    db_name=os.environ["MSSQL_WAREHOUSE_DATABASE"],
)


def main() -> None:
    """The main entry point to the application."""
    mssql_conn = None
    try:
        # BaseWarehouse.metadata contains information of wanted tables
        mssql_conn = SQLAlchemyConnector(alchemy_mssql_conn_config, BaseWarehouse.metadata)

        # Use SQLAlchemy to create tables and drop any existing tables
        mssql_conn.drop_all_tables()
        mssql_conn.create_all_tables()
    finally:
        if mssql_conn is not None:
            mssql_conn.close()


if __name__ == "__main__":
    main()
