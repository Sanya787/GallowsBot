import sqlalchemy
from data.db_session import SqlAlchemyBase


class Stats(SqlAlchemyBase):
    __tablename__ = 'statistics'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True)
    victories = sqlalchemy.Column(sqlalchemy.Integer)
    wins_now = sqlalchemy.Column(sqlalchemy.Integer)
    total = sqlalchemy.Column(sqlalchemy.Integer)
    friendly_victories = sqlalchemy.Column(sqlalchemy.Integer)
