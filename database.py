from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = URL.create(
    'postgresql',
    username='koyeb-adm',
    password='yam3Cbgn4THq',
    host='ep-sweet-sky-a2r1vkha.eu-central-1.pg.koyeb.app',
    database='koyebdb',
)

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
