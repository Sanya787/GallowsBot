import sqlalchemy
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):  # type: ignore
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True)
    game = sqlalchemy.Column(sqlalchemy.String)
