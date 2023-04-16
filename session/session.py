from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from os import environ

db_name = environ.get('DB_NAME', 'db_graphql')
db_user = environ.get('DB_USER', 'db_user')
db_password = environ.get('DB_PASSWORD', 'db_password')

engine = create_engine(
    f'postgresql+psycopg2://{db_user}:{db_password}@db/{db_name}',
)

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_session():
    return session_factory()
