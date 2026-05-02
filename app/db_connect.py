import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Global connection pool (initialized once at startup)
_pool: asyncpg.Pool = None


async def init_db():
    """Initialize the connection pool and create tables once at startup."""
    global _pool
    _pool = await asyncpg.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        min_size=2,
        max_size=10,
    )

    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                email TEXT PRIMARY KEY NOT NULL,
                password TEXT NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS personal_details (
                email TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                dateofbirth DATE NOT NULL,
                gender TEXT NOT NULL,
                height FLOAT NOT NULL,
                weight FLOAT NOT NULL,
                waist FLOAT NOT NULL,
                FOREIGN KEY (email) REFERENCES credentials(email)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                email TEXT PRIMARY KEY NOT NULL,
                foodpreference TEXT NOT NULL,
                snackpreferences TEXT NOT NULL,
                mealtimings TEXT NOT NULL,
                cheatdayfrequency TEXT NOT NULL,
                culturalpreferences TEXT NOT NULL,
                preferredingredients TEXT NOT NULL,
                cuisinepreferences TEXT NOT NULL,
                spicyfoodtolerance TEXT NOT NULL,
                preferredmealtype TEXT NOT NULL,
                favoritemeal TEXT NOT NULL,
                mealfrequency TEXT NOT NULL,
                sweetpreference TEXT NOT NULL,
                eatingoutfrequency TEXT NOT NULL,
                hydrationlevel FLOAT NOT NULL,
                preferreddrinks TEXT NOT NULL,
                activitylevel TEXT NOT NULL,
                fitnessgoal TEXT NOT NULL,
                foodrestrictions TEXT NOT NULL,
                caffeineintake TEXT NOT NULL,
                averagesleep FLOAT NOT NULL,
                sleepquality TEXT NOT NULL,
                supplementusage TEXT NOT NULL,
                supplementfrequency TEXT NOT NULL,
                FOREIGN KEY (email) REFERENCES credentials(email)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_conditions (
                email TEXT PRIMARY KEY NOT NULL,
                allergies TEXT NOT NULL,
                diabetes TEXT NOT NULL,
                hypertension TEXT NOT NULL,
                cholesterol TEXT NOT NULL,
                thyroid TEXT NOT NULL,
                kidneydisease TEXT NOT NULL,
                liverdisease TEXT NOT NULL,
                lactoseintolerance TEXT NOT NULL,
                glutensensitivity TEXT NOT NULL,
                pcos TEXT,
                anemia TEXT NOT NULL,
                osteoporosis TEXT NOT NULL,
                ibs TEXT NOT NULL,
                gerd TEXT NOT NULL,
                gout TEXT NOT NULL,
                otherconditions TEXT NOT NULL,
                FOREIGN KEY (email) REFERENCES credentials(email)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id UUID PRIMARY KEY,
                email TEXT NOT NULL,
                expiration TIMESTAMPTZ NOT NULL,
                FOREIGN KEY (email) REFERENCES credentials(email)
            );
        """)

    print("Database pool initialized and tables ensured.")


def get_pool() -> asyncpg.Pool:

    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")
    return _pool


async def connect_db():
   
    pool = get_pool()
    return await pool.acquire()