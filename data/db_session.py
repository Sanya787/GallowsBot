import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, declarative_base

SqlAlchemyBase = declarative_base()  # type: ignore

__factory = None
'''
create connection with data-base
'''


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models  # noqa: F401

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()  # type: ignore
