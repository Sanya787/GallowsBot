from data import db_session
from data.users import User
from data.statistics import Stats


db_session.global_init("db/database.db")
def append_to_base(id, data):

    db_sess = db_session.create_session()
    user = User(
        id=id,
        game=data
    )
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()

    
def update_base(id, new_data):

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    user.game = new_data
    db_sess.commit()
    db_sess.close()
    print(new_data)


def check_base(id):

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    db_sess.close()
    if user:
        return True
    return False


def get_from_base(id):

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    db_sess.close()
    return user.game


def append_to_statistics(id):

    db_sess = db_session.create_session()
    stats = Stats(
        id=id,
        vicroties=0,
        wins_now=0,
        total=0,
        friendly_victories=0
    )
    db_sess.add(stats)
    db_sess.commit()
    db_sess.close()


def update_base_stat(id, data):

    db_sess = db_session.create_session()
    stats = db_sess.query(Stats).filter(Stats.id == id).first()
    stats.victories, stats.wins_now = data[0], data[1]
    stats.total, stats.friendly_victories = data[2], data[3]
    db_sess.commit()
    db_sess.close()


def get_from_stat(id):

    db_sess = db_session.create_session()
    stats = db_sess.query(Stats).filter(Stats.id == id).first()
    db_sess.close()
    answer = stats.id, stats.victories, stats.wins_now
    answer += stats.total, stats.friendly_victories
    return answer
