from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sq


from dotenv import dotenv_values
secrets_values = dotenv_values('.env')

USER = secrets_values['USER']
PASSWORD = secrets_values['PASSWORD']
HOST = secrets_values['HOST']
PORT = secrets_values['PORT']
DB_NAME = secrets_values['DB_NAME']

DSN = f'postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'

engine = create_async_engine(DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class SwapiPeople(Base):
    __tablename__ = 'people'

    person_id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    birth_year = sq.Column(sq.String)
    eye_color = sq.Column(sq.String(50))
    films = sq.Column(sq.String(200))
    gender = sq.Column(sq.String(50))
    hair_color = sq.Column(sq.String(50))
    height = sq.Column(sq.String)
    homeworld = sq.Column(sq.String(50))
    mass = sq.Column(sq.String)
    name = sq.Column(sq.String(50))
    skin_color = sq.Column(sq.String(50))
    species = sq.Column(sq.String(200))
    starships = sq.Column(sq.String(200))
    vehicles = sq.Column(sq.String(200))
