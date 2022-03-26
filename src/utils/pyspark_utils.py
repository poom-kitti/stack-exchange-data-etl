"""This module contains utiltiy functions for pyspark application."""
from dataclasses import dataclass


@dataclass
class JDBCConnectionConfig:
    """A data class to contain information to connect to a JDBC database."""

    hostname: str
    port: str
    username: str
    password: str
    db_name: str
