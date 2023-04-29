from os import environ
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_name = environ.get('TEST_DB_NAME', 'test_db_name')
db_user = environ.get('TEST_DB_USER', 'test_db_user')
db_password = environ.get('TEST_DB_PASSWORD', 'test_db_password')

engine = create_engine(
    f'postgresql+psycopg2://{db_user}:{db_password}@db_testing/{db_name}',
)

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_session():
    return session_factory()
