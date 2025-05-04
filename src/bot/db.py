import asyncpg
from typing import Optional, List, Dict, Any
from parser.models import Vacancy
from config import config
import logging

class DataBase:

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):

        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                host=config.DB_HOST,
                port=config.DB_PORT
            )

            logging.info("Connected to PostgreSQL database")

        except Exception as e:

            logging.error(f"Database connection error: {e}")
            raise

    async def close(self):

        if self.pool:
            await self.pool.close()
            logging.info("Database connection closed")

    async def initialize(self):

        async with self.pool.acquire() as connection:
            try:
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')

                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS searches (
                        search_id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES users(user_id),
                        query TEXT NOT NULL,
                        area_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(user_id, query, area_id)
                    )
                ''')

                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS vacancies (
                        vacancy_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        employer TEXT NOT NULL,
                        salary TEXT,
                        experience TEXT,
                        url TEXT NOT NULL,
                        search_id INTEGER REFERENCES searches(search_id),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')

                logging.info("Database tables initialized")

            except Exception as e:

                logging.error(f"Database initialization error: {e}")
                raise            

