import json
import random
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia, InputFile

TOKEN_API = 'TOKEN'

bot = Bot(TOKEN_API)
dispatcher = Dispatcher(bot)


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


class Play:
    def __init__(self):
        self.word = ' '
        self.meaning = ' '
        self.live = 6
        self.guessed_letters = ' '
        self.all_letters = ' '
        self.buttons_line = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧЩШЬЫЪЭЮЯ'

    def encode(self):
        string = ''
        for elem in self.guessed_letters:
            string += elem
        string2 = ''
        for elem in self.all_letters:
            string2 += elem
        return '---'.join([self.word, self.meaning, str(self.live), string, string2])

    def decode(self, string):
        self.word, self.meaning, self.live, self.guessed_letters, self.all_letters = string.split('---')
        self.live = int(self.live)

    def get_string(self):
        answer = ''
        for elem in self.word:
            if elem in self.guessed_letters:
                answer += elem
            else:
                answer += '-'
        return answer

    def get_buttons_line(self):
        string = ''
        for elem in self.buttons_line:
            if elem.lower() in self.all_letters:
                string += ' '
            else:
                string += elem
        return string

    def generate_word(self):
        with open('words.json') as cat_file:
            f = cat_file.read()
            data = json.loads(f)
            key = random.choice(list(data.items()))
        self.word = key[0]
        self.meaning = key[1]['definition']
        self.guessed_letters += self.word[0]
        self.buttons_line = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧЩШЬЫЪЭЮЯ'
        self.all_letters = ' '
        self.live = 6

    def use_letter(self, letter):
        if letter in self.word:
            self.guessed_letters += letter
        else:
            self.live -= 1

    def get_meaning(self):
        return self.meaning


@dispatcher.message_handler(commands=['start_play'])
async def give_word(message):
    play = Play()
    play.generate_word()
    if not check_base(message.from_user.id):
        append_to_base(message.from_user.id, play.encode())
    else:
        update_base(message.from_user.id, play.encode())

    keyboard = InlineKeyboardMarkup(row_width=11)
    btns = []
    for elem in play.get_buttons_line():
        if elem == ' ':
            btns.append(InlineKeyboardButton(text=''))
        else:
            btns.append(InlineKeyboardButton(text=elem, callback_data=elem))
    keyboard.add(btns[0], btns[1], btns[2], btns[3], btns[4], btns[5], btns[6], btns[7])
    keyboard.add(btns[8], btns[9], btns[10], btns[11], btns[12], btns[13], btns[14], btns[15])
    keyboard.add(btns[16], btns[17], btns[18], btns[19], btns[20], btns[21], btns[22], btns[23])
    keyboard.add(btns[24], btns[25], btns[26], btns[27], btns[28], btns[29], btns[30], btns[31])
    await bot.send_photo(
        message.chat.id,
        open('images/6.png', 'rb'),
        f'Я загадал слово. Попробуй отгадать:\n{play.get_string()}',
        parse_mode='HTML',
        reply_markup=keyboard
    )


@dispatcher.message_handler(commands=['start'])
async def welcome(message: types.Message):
    play = Play()
    play.generate_word()
    if not check_base(message.from_user.id):
        append_to_base(message.from_user.id, play.encode())
    await bot.send_sticker(message.from_user.id,
                           sticker='CAACAgIAAxkBAAEIAQhkBEaOqezxBZAqH2nncSJrIfriswACVAADQbVWDGq3-McIjQH6LgQ')
    await message.answer(text=f'Привет, <b>{message.from_user.first_name}</b>!', parse_mode='HTML')


@dispatcher.message_handler(commands=['help'])
async def helps(message: types.Message):
    text = '''
    Мои команды:
/start - запуск
/help - выводит данное окно
/start_play - пока что просто загадывает слово
    '''
    await message.answer(text=text, parse_mode='HTML')


@dispatcher.callback_query_handler()
async def callback(callback):
    play = Play()
    play.decode(get_from_base(callback.from_user.id))
    if callback.data != ' ':
        play.use_letter(callback.data.lower())
        play.all_letters += callback.data.lower()
        update_base(callback.from_user.id, play.encode())
    flag = True
    for elem in play.word:
        if elem not in play.guessed_letters:
            flag = False
    if play.live < 1:
        await callback.message.answer(
            text=f'К сожалению, вы проиграли:(',
            parse_mode='HTML',
        )
        await callback.message.delete()
    elif flag:
        await callback.message.answer(
            text=f'Поздравляю! Вы угадали слово!',
            parse_mode='HTML',
        )
        await callback.message.delete()

    else:
        keyboard = InlineKeyboardMarkup(row_width=11)
        btns = []
        for elem in play.get_buttons_line():
            btns.append(InlineKeyboardButton(text=elem, callback_data=elem))
        keyboard.add(btns[0], btns[1], btns[2], btns[3], btns[4], btns[5], btns[6], btns[7])
        keyboard.add(btns[8], btns[9], btns[10], btns[11], btns[12], btns[13], btns[14], btns[15])
        keyboard.add(btns[16], btns[17], btns[18], btns[19], btns[20], btns[21], btns[22], btns[23])
        keyboard.add(btns[24], btns[25], btns[26], btns[27], btns[28], btns[29], btns[30], btns[31])
        file = InputMedia(media=InputFile(
            f'images/{play.live}.png'),
            caption=f"Я загадал слово. Попробуй отгадать:\n{play.get_string()}")
        await callback.message.edit_media(file, reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dispatcher)
