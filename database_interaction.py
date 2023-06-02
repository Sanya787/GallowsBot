import sqlite3


def append_to_base(id, data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''INSERT INTO users (id, class)
    VALUES({id}, "{data}");'''
    cursor.execute(query)
    connection.commit()
    connection.close()


def update_base(id, new_data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    print(new_data)
    query = f'''UPDATE users
SET class = "{new_data}"
WHERE id = {id};'''
    cursor.execute(query)
    connection.commit()
    connection.close()


def check_base(id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''SELECT class FROM users
    WHERE id = {id}'''
    cursor.execute(query)
    if cursor.fetchall():
        return True
    return False


def get_from_base(id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''SELECT class FROM users
WHERE id = {id}'''
    cursor.execute(query)
    return cursor.fetchall()[0][0]


def append_to_statistics(id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''INSERT INTO statistics (id, victories, wins_now, total, friendly_victories) 
    VALUES({id}, 0, 0, 0, 0);'''
    cursor.execute(query)
    connection.commit()
    connection.close()


def update_base_stat(id, data):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''UPDATE statistics
SET victories = "{data[0]}", wins_now = "{data[1]}", total = "{data[2]}", friendly_victories = "{data[3]}"
WHERE id = {id};'''
    cursor.execute(query)
    connection.commit()
    connection.close()


def get_from_stat(id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''SELECT * FROM statistics
WHERE id = {id}'''
    cursor.execute(query)
    return cursor.fetchall()[0]


def check_stat(id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = f'''SELECT total FROM statistics
    WHERE id = {id}'''
    cursor.execute(query)
    if cursor.fetchall():
        return True
    return False
