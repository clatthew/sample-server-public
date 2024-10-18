"""Miscellaneous helper functions, classes and custom errors"""

from pg8000.native import Connection, DatabaseError, InterfaceError
import os
import sys
from typing import TypedDict
import logging
from src.data.sql import query_strings
from fastapi import HTTPException
from dotenv import dotenv_values


# Logging config
logger = logging.getLogger("App")

file_loc = "./logs/app.log"

log_levels = {
    "error": logging.ERROR,
    "warn": logging.WARN,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

log_level = log_levels[os.environ.get("LOG_LEVEL", "debug")]

file_handler = logging.FileHandler(file_loc)
stream_handler = logging.StreamHandler(sys.stdout)
logger.setLevel(log_level)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


# Errors
class DBConnectionException(Exception):
    """Wraps pg8000.native Error or DatabaseError."""

    def __init__(self, e):
        """Initialise with provided error message."""
        self.message = str(e)
        super().__init__(self.message)


class ItemNotFoundException(Exception):
    """Encapsulates an error following null results"""

    def __init__(self, item_name: str, item_id: int = None) -> None:
        """Initialise with provided error message."""
        m1 = f"No instance of {item_name} was found in the database"
        m2 = f" with id {item_id}." if item_id else "."
        self.message = f"{m1}{m2}"
        super().__init__(self.message)


class NoSuchUserException(Exception):
    """Encapsulates an error if no user found"""

    def __init__(self, user_id: int) -> None:
        """Initialise with provided error message."""
        self.message = f"No user with id {user_id} was found in the database"
        super().__init__(self.message)


# Request Parameters
class Params(TypedDict, total=False):
    """Parameter types for standard query processing."""

    user_id: int
    product_id: int
    date_from: str
    date_to: str


# Helper functions


def get_config(path: str = ".env") -> dict:
    return dotenv_values(path)


def get_db_connection() -> Connection:
    """Gets a Connection to the database.

    Credentials are retrieved from environment variables.

    Returns:
        a database connection

    Raises:
        DBConnectionException
    """
    try:
        config = get_config()
        DB_HOST = config["DB_HOST"]
        DB_PORT = config["DB_PORT"]
        DB_USER = config["DB_USER"]
        DB_PASSWORD = config["DB_PASSWORD"]
        DB_DB = config["DB_DB"]
        return Connection(
            host=DB_HOST,
            user=DB_USER,
            port=DB_PORT,
            password=DB_PASSWORD,
            database=DB_DB,
        )
    except InterfaceError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise DBConnectionException("Failed to connect to database")


def process_query(query: str, **kwargs: Params) -> list[dict]:
    """Gets a connection, executes a query, closes connection.

    Pass in a valid query string and any query parameters.

    Args:
        query (string): a valid SQL query.

    Keyword Arguments:
        kwargs: a tuple of SQL parameters e.g. user_id=3

    Returns:
        a response containing query results.

        Example:
        [
            {"category_id": 3, "category_name": "Books"},
            {"category_id": 7, "category_name": "Movies"}
        ]

    Raises:
        DBConnectionException, InterfaceError, DatabaseError
    """
    conn = None
    try:
        conn = get_db_connection()
        result = conn.run(query, **kwargs)
        columns = [c["name"] for c in conn.columns]
    except DBConnectionException as d:
        conn = None
        raise HTTPException(
            status_code=500,
            detail=f"There was an error connecting to the database: {d}",
        )
    except DatabaseError as db:
        err = db.args[0]
        raise HTTPException(
            status_code=500,
            detail=f"Database Error, code {err['C']}, message {err['M']}",
        )
    finally:
        if conn:
            conn.close()
    return [dict(zip(columns, r)) for r in result]


def check_user(user_id: int) -> list[int]:
    try:
        check_users = process_query(query_strings["users"])
        present = [v for c in check_users if (v := c["id"]) == user_id]
        if len(present) == 0:
            raise ItemNotFoundException("user", user_id)
        return present
    except DBConnectionException as d:
        logger.info("Connection exception while checking user exists")
        raise HTTPException(status_code=500, detail=d)
    except ItemNotFoundException as i:
        logger.info(f"No user: {i}")
        raise HTTPException(status_code=404, detail=str(i))
