import app.config as config
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker

settings = config.Settings()

def get_database_url():

    return f"postgresql+psycopg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

url = get_database_url()

engine = create_engine(url)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
