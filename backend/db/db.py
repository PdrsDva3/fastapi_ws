import hashlib
import logging

import psycopg2
from psycopg2 import sql

import config

db_config = {
    'dbname': config.DB_NAME,
    'user': config.DB_USER,
    'password': config.DB_PASSWORD,
    'host': config.DB_HOST,
    'port': config.DB_PORT,
}


def db_connection():
    return psycopg2.connect(**db_config)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)



async def get_user(user_id):
    connection = db_connection()
    cursor = connection.cursor()

    try:
        get_user_query = sql.SQL("""
        SELECT name, email FROM users WHERE id = %s
        """)
        cursor.execute(get_user_query, (user_id,))

        row = cursor.fetchone()

        users = {"name": row[0], "email": row[1]}

        logger.info("Database fetched successfully")
        return users

    except (Exception, psycopg2.DatabaseError) as error:

        logger.error(error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info('Database connection closed.')
            # logger.debug("-" * 40)


async def create_user(login, password, name) -> int:
    connection = db_connection()
    cursor = connection.cursor()

    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

    try:
        create_user_query = sql.SQL("""
            INSERT INTO users (email, hashed_pwd, name) VALUES (%s, %s, %s) returning id
            """)
        cursor.execute(create_user_query, (login, hashed_pwd, name))

        user_id = cursor.fetchone()

        connection.commit()
        logger.info("Created user successfully")
        return user_id

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info('Database connection closed.')
            # logger.debug("-" * 40)


async def login_user(login, password):
    connection = db_connection()
    cursor = connection.cursor()

    try:
        login_user_query = sql.SQL("""
            SELECT id, hashed_pwd FROM users WHERE email = %s
            """)
        cursor.execute(login_user_query, (login,))

        row = cursor.fetchone()

        users = {"id": row[0], "hashed_pwd": row[1]}

        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

        if hashed_pwd == users["hashed_pwd"]:
            connection.commit()
            logger.info("Login successful")
            return users["id"]
        else:
            logger.error("Invalid password")
            return None

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info('Database connection closed.')