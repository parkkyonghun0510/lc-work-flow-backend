import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL is None:
    raise ValueError("REDIS_URL environment variable not set.")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_redis_client():
    return redis_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()