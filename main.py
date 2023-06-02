import random
import os

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia, InputFile,\
    ReplyKeyboardMarkup, KeyboardButton
from game import Game, analyze_game
from database_interaction import *

TOKEN_API = 'TOKEN'
PROXY_URL = "http://proxy.server:3128"

storage = MemoryStorage()
# bot = Bot(token=TOKEN_API, proxy=PROXY_URL)
bot = Bot(token=TOKEN_API)
dispatcher = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    file = State()


class DuelState(StatesGroup):
    contact = State()
    word = State()
    meaning = State()


@dispatcher.message_handler(content_types=['any'], state=UserState.file)
async def get_address(message: types.Message, state):
    try:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)

        await bot.download_file(file.file_path, f"{message.from_user.id}.txt")
        await bot.send_message(
            message.chat.id,
            'Поздравляем! Слова успешно добавлены в профиль ✅')
        await state.finish()
    except Exception:
        await bot.send_message(
            message.chat.id,
            '❌ Это не файл или файла не того формата. Попробуйте снова ')
        await state.finish()


@dispatcher.message_handler(content_types=['any'], state=DuelState.contact)
async def get_contact(message: types.Message, state):
    try:
        await state.update_data(contact=message['contact']['user_id'])
        await bot.send_message(message.from_user.id, 'Отправь слово')
        await DuelState.next()

    except TypeError:
        if message.text.isdigit():
            await state.update_data(contact=message.text)
            await bot.send_message(message.from_user.id, 'Отправь слово')
            await DuelState.next()
        else:
            await bot.send_message(message.from_user.id, 'Это не контакт 😧')


@dispatcher.message_handler(content_types=['any'], state=DuelState.word)
async def get_word(message: types.Message, state):
    try:
        await state.update_data(word=message.text)
        await bot.send_message(message.from_user.id, 'Отправь значение')

    except TypeError:
        await bot.send_message(message.from_user.id, 'Это не слово')
    await DuelState.next()


@dispatcher.message_handler(content_types=['any'], state=DuelState.meaning)
async def get_meaning(message: types.Message, state):
    try:
        await state.update_data(meaning=message.text)

    except TypeError:
        await bot.send_message(message.from_user.id, 'Это не контакт 😧')
    data = await state.get_data()
    print(data)
    await message.answer(f"Контакт: {data['contact']}\n"
                         f"Слово: {data['word']}\n"
                         f"Значение: {data['meaning']}")
    await state.finish()
    await give_word(f"{data['contact']}---{data['word']}---{data['meaning']}---{message.from_user.id}")
    await bot.send_message(
        chat_id=data['contact'],
        text=f'''Вы были вызваны на дуэль ⚔️
Оппонент: {message.from_user.username} ({message.from_user.full_name})'''
    )

stickers_list = [
    'CAACAgIAAxkBAAEIENNkCgRsmUrCEOWqAAGjcOGqwJimybwAAm8AA8GcYAzLDn2LwN1NVi8E',
    'CAACAgIAAxkBAAEIAQhkBEaOqezxBZAqH2nncSJrIfriswACVAADQbVWDGq3-McIjQH6LgQ',
    'CAACAgIAAxkBAAEIENFkCgRWQThlT61o41mTI-DQdxbuSwACIwEAAjDUnRGe2TeBrqpcAi8E',
    'CAACAgIAAxkBAAEIEM9kCgRMNI4rrGxTnrlBaUQ_8t-JlgACbgUAAj-VzAqGOtldiLy3NS8E',
    'CAACAgIAAxkBAAEIEMtkCgQ9FQxjlqfsKiam4Ohk-DeKsQACBQADwDZPE_lqX5qCa011LwQ',
    'CAACAgIAAxkBAAEIEMlkCgQnrCdSYaAvXdPN0OPASfuwvwACEQMAAvPjvgsZbp8lnswsJC8E',
    'CAACAgIAAxkBAAEIENdkCgTm-_jCWE1eMoBB6ZYjNS1fOgACpgADUomRI2u5KhCNt8e8LwQ',
    'CAACAgIAAxkBAAEIG_NkDiH6F9jpoSDnysf67MWH6eekeAACpRAAArRFoEpqI1qAWc6jRy8E',
    'CAACAgIAAxkBAAEIG_VkDiH_NN1C05If-NuEQqXIvsvhmgAC2A8AAkjyYEsV-8TaeHRrmC8E'
]


def get_keyboard(game):

    keyboard = InlineKeyboardMarkup(row_width=11)
    btns = []

    for elem in game.get_buttons_line():
        btns.append(InlineKeyboardButton(text=elem, callback_data=elem))
    keyboard.add(*[btns[i] for i in range(0, 8)])
    keyboard.add(*[btns[i] for i in range(8, 16)])
    keyboard.add(*[btns[i] for i in range(16, 24)])
    keyboard.add(*[btns[i] for i in range(24, 32)])
    if game.use_clue[0] == '1':
        btn1 = InlineKeyboardButton(
            text='✅ Открыть букву',
            callback_data='open_letter'
        )
        keyboard.add(btn1)
    if game.use_clue[1] == '1':
        btn2 = InlineKeyboardButton(
            text='💭 Значение слова',
            callback_data='meaning'
        )
        keyboard.add(btn2)
    if game.use_clue[2] == '1':
        btn3 = InlineKeyboardButton(
            text='🔂 Убрать 3 буквы',
            callback_data='delete_letter'
        )
        keyboard.add(btn3)
    btn4 = InlineKeyboardButton(
        text='❌ Закончить игру',
        callback_data='stop_play'
    )
    keyboard.add(btn4)

    return keyboard


@dispatcher.message_handler(commands=['start_play'])
async def give_word(message):
    if type(message) == type('1'):
        id, word, meaning, player = message.split('---')
        game = Game(player)
        game.word = word.lower()
        game.meaning = meaning
        game.live = 6
        game.guessed_letters += game.word[0].lower()
        game.buttons_line = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧЩШЬЫЪЭЮЯ'
        game.all_letters += game.word[0].lower()
        for elem in game.word:
            if elem not in game.buttons_line.lower():
                game.guessed_letters += elem

        if not check_base(id):  # Если пользователя нет в бд
            append_to_base(id, game.encode())
        else:  # Если пользователь уже есть в бд
            update_base(id, game.encode())
        keyboard = get_keyboard(game)

        await bot.send_photo(
            id,
            open('images/6.png', 'rb'),
            f'Я загадал слово. Попробуй отгадать:\n{game.get_string()}',
            parse_mode='HTML',
            reply_markup=keyboard,
        )
        print('Слово вроде как даже загадано')
    else:
        id = message.from_user.id
        game = Game()  # Класс игры
        file_path = f"{id}.txt"
        if os.path.exists(file_path):
            game.generate_word(file_path)
        else:
            game.generate_word()  # Генерация нового слова

        cort = get_from_stat(id)
        cort_new = cort[1], cort[2], cort[3] + 1, cort[4]
        update_base_stat(id, cort_new)

        if not check_base(id):  # Если пользователя нет в бд
            append_to_base(id, game.encode())
        else:  # Если пользователь уже есть в бд
            update_base(id, game.encode())

        keyboard = get_keyboard(game)
        await bot.send_photo(
            id,
            open('images/6.png', 'rb'),
            f'Я загадал слово. Попробуй отгадать:\n{game.get_string()}',
            parse_mode='HTML',
            reply_markup=keyboard,
        )


@dispatcher.message_handler(commands=['start'])
async def welcome(message: types.Message):
    game = Game()
    file_path = f"{message.from_user.id}.txt"
    if os.path.exists(file_path):
        game.generate_word(file_path)
    else:
        game.generate_word()

    if not check_base(message.from_user.id):
        append_to_base(message.from_user.id, game.encode())
        append_to_statistics(message.from_user.id)
    if not check_stat(message.from_user.id):
        append_to_statistics(message.from_user.id)

    # keyboard = ReplyKeyboardMarkup()
    # keyboard.add(KeyboardButton('Об авторе'),
    # KeyboardButton('О проекте'), KeyboardButton('Обратная связь'))

    await bot.send_sticker(
        message.from_user.id,
        sticker=random.choice(stickers_list),
        # reply_markup=keyboard
    )
    name = message.from_user.first_name
    text = f'''
Привет, {name}! Я - <b> Бот Виселица</b>. Со мной ты можешь сыграть в
игру, я загадываю слово - твоя задача его угадать. У тебя
будет возможность выбрать любую букву русского алфавита. ⚠️
<i>Ты всегда можешь написать мне /help и я помогу тебе :)</i>

Если ты 6 раз назовешь неправильную букву, увы, проиграешь.
Также я даю подсказки (каждую 1 раз):
1) Назвать 3 буквы, которых точно нет в слове ❌
2) Открыть 1 букву из слова ✅
3) Сказать значение слова 💬

Наверное, тебе осталось разобраться лишь с управлением, тут все
просто - жми на кнопки и получай удовольствие!🙂
<i>Чтобы начать нажми сюда 👉 /start_play</i>
    '''

    keyboard = InlineKeyboardMarkup(row_width=11)
    btn1 = InlineKeyboardButton(
        text='Играть 🎲',
        callback_data='start_play'
    )
    btn2 = InlineKeyboardButton(
        text='Смотреть статистику 📈',
        callback_data='see_static'
    )
    btn3 = InlineKeyboardButton(
        text='Добавить свои слова ✏️',
        callback_data='append_words'
    )
    btn4 = InlineKeyboardButton(
        text='Дуэль ⚔️',
        callback_data='start_duel'
    )
    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)

    await message.answer(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


@dispatcher.message_handler(commands=['help'])
async def helps(message: types.Message):
    text = '''
Я -  Бот Виселица. Со мной ты можешь сыграть в
игру, я загадываю слово - твоя задача его угадать. У тебя будет
 возможность выбрать любую букву русского алфавита. ⚠️

Если ты 6 раз назовешь неправильную букву, увы, проиграешь. Также
я даю подсказки (каждую 1 раз):
1) Назвать 3 буквы, которых точно нет в слове ❌
2) Открыть 1 букву из слова ✅
3) Сказать значение слова 💬

Основные команды:
/start - получить начальное меню
/start_play - начать игру
/help - выводит данное окно
/duel - вызвать игрока на дуэль
    '''
    if type(message) == type(1):
        id = message
    else:
        id = message.from_user.id
    await bot.send_message(
        id,
        text=text,
        parse_mode='HTML'
    )


@dispatcher.callback_query_handler()
async def callback(callback):
    check_box = [
        'start_play',
        'see_static',
        'append_words',
        'start_duel',
        'help'
    ]
    data_box = [
        'open_letter',
        'meaning',
        'stop_play',
        'delete_letter',
        'stop'
    ]
    if callback.data in check_box:
        if callback.data == 'start_play':
            await give_word(callback)

        elif callback.data == 'see_static':
            data = get_from_stat(callback.from_user.id)
            text = f'''<b>====Ваша статистика:====</b>
Всего побед: {data[1]} 🏆
Текущая серия побед: {data[2]} 🚩
Всего проведено игр: {data[3]} 🏳️
Выиграно дружеских игр: {data[4]} 🤝
'''
            await bot.send_message(
                callback.from_user.id,
                text=text,
                parse_mode='HTML'
            )

        elif callback.data == 'append_words':
            text = '''Для добавления нового словаря отправьте файл формата txt,
где будут на каждой новой строке храниться ваши слова в формате:
<b>(Слово):(Значение).</b>
<i>Пример такого файла:</i>'''
            await bot.send_message(
                callback.from_user.id,
                text=text,
                parse_mode='HTML'
            )
            await bot.send_document(
                callback.from_user.id,
                open('test.txt', encoding='UTF-8'))
            await UserState.file.set()

        elif callback.data == 'start_duel':
            text = '''Сейчас ты можешь бросить вызов любому своему другу ⚔️.
Ты загадываешь ему слово, а он будет отгадывать 💭. Для начала отправь контакт, с которым ты хочешь сыграть!'''
            await bot.send_message(
                callback.from_user.id,
                text=text,
                parse_mode='HTML'
            )
            await DuelState.contact.set()
        elif callback.data == 'help':
            await helps(callback.from_user.id)

    elif callback.data in data_box:
        if callback.data == 'stop_play':
            await callback.message.answer(
                text='Игра приостановлена',
                parse_mode='HTML',
            )

            await callback.message.delete()

        if callback.data == 'stop':
            await callback.message.delete()

        elif callback.data == 'meaning':
            game = Game()
            game.decode(get_from_base(callback.from_user.id))
            game.use_clue = f"{game.use_clue[0]}0{game.use_clue[2]}"
            update_base(callback.from_user.id, game.encode())

            keyboard = get_keyboard(game)
            cap = f"Я загадал слово. Попробуй отгадать:\n{game.get_string()}"
            text = f'<i><b>Подсказка:</b></i> \n{game.get_meaning()}'
            file = InputMedia(media=InputFile(
                f'images/{game.live}.png'),
                caption=cap)

            await callback.message.edit_media(file, reply_markup=keyboard)
            await bot.send_message(
                callback.from_user.id,
                text=text,
                parse_mode='HTML'
            )

        elif callback.data == 'delete_letter':
            game = Game()
            game.decode(get_from_base(callback.from_user.id))
            game.use_clue = f"{game.use_clue[0]}{game.use_clue[1]}0"
            game.delete_letters()

            update_base(callback.from_user.id, game.encode())

            keyboard = get_keyboard(game)
            cap = f"Я загадал слово. Попробуй отгадать:\n{game.get_string()}"
            file = InputMedia(media=InputFile(
                f'images/{game.live}.png'),
                caption=cap)
            await callback.message.edit_media(file, reply_markup=keyboard)

        elif callback.data == 'open_letter':
            game = Game()
            game.decode(get_from_base(callback.from_user.id))
            game.get_letter()

            game.use_clue = f"0{game.use_clue[1]}{game.use_clue[2]}"
            update_base(callback.from_user.id, game.encode())

            flag = True
            for elem in game.word:
                if elem not in game.guessed_letters:
                    flag = False
            if flag:
                cort = get_from_stat(callback.from_user.id)
                cort_new = cort[1] + 1, cort[2] + 1, cort[3], cort[4]
                update_base_stat(callback.from_user.id, cort_new)

                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(
                    text='Играть 🎲',
                    callback_data='start_play'
                ))

                keyboard.add(InlineKeyboardButton(
                    text='Завершить ❌',
                    callback_data='stop'
                ))

                keyboard.add(InlineKeyboardButton(
                    text='Анализ игры 📈',
                    callback_data=f'aw: {game.word}.{game.all_letters}'
                ))

                await bot.send_message(
                    chat_id=callback.from_user.id,
                    text=f'Поздравляю! Вы угадали слово - <b>{game.word}</b>! Хотите сыграть ещё?',
                    parse_mode='HTML',
                    reply_markup=keyboard
                )

                await callback.message.delete()
            else:

                keyboard = get_keyboard(game)
                cap = f"Я загадал слово. Попробуй отгадать:\n{game.get_string()}"
                file = InputMedia(media=InputFile(
                    f'images/{game.live}.png'),
                    caption=cap)
                await callback.message.edit_media(file, reply_markup=keyboard)

    elif 'aw: ' in callback.data:
        await callback.message.delete()
        word, letters = callback.data[4:].split('. ')
        result = analyze_game(word, letters)
        message = ''

        for idx in range(1, len(letters)):
            result_elem = sorted(result[idx].items(), key=lambda x: x[1])
            message += f'\n<b>Ваш ход: {letters[idx]}</b>'

            if letters[idx] == result_elem[-1][0]:
                message += f'\nХод номер {idx + 1}! Поздравляем ход логичный ✅'
            else:
                message += f'\nХод номер {idx + 1}! Ход нелогичный ❌'

            message += '\nЛучшие варианты ходов:'
            message += f'\n 1) {result_elem[-1][0]}'
            message += f': {str(result_elem[-1][1] * 100)[:4]}%'
            message += f'\n 2) {result_elem[-2][0]}'
            message += f': {str(result_elem[-2][1] * 100)[:4]}%'
            message += f'\n 3) {result_elem[-3][0]}'
            message += f': {str(result_elem[-3][1] * 100)[:4]}%'
            message += '\n======================='

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            text='Закрыть уведомление ❌', callback_data='stop'
        ))

        await bot.send_message(
            chat_id=callback.from_user.id,
            text=message,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    elif callback.data == ' ':
        pass
    else:
        game = Game()
        game.decode(get_from_base(callback.from_user.id))

        if callback.data != ' ':
            game.use_letter(callback.data.lower())
            game.all_letters += callback.data.lower()
            update_base(callback.from_user.id, game.encode())

        flag = True

        for elem in game.word:
            if elem not in game.guessed_letters:
                flag = False

        if game.live < 1:

            if game.player == 'BOT':
                cort = get_from_stat(callback.from_user.id)
                cort_new = cort[1] + 1, cort[2] + 1, cort[3], cort[4]
                update_base_stat(callback.from_user.id, cort_new)
                await bot.send_message(
                    callback.from_user.id,
                    text=f'''Поздравляем! 🎉 Вы загадали слово, которое противник не смог угадать!
Напомним, это было слово - <b>{game.word}</b>'''
                )
            else:
                cort = get_from_stat(game.player)
                cort_new = cort[1], cort[2], cort[3], cort[4] + 1
                update_base_stat(game.player, cort_new)

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text='Играть 🎲',
                callback_data='start_play'
            ))

            keyboard.add(InlineKeyboardButton(
                text='Завершить ❌',
                callback_data='stop'
            ))

            keyboard.add(InlineKeyboardButton(
                text='Анализ игры 📈',
                callback_data=f'aw: {game.word}.{game.all_letters}'
            ))

            a = 'К сожалению, вы проиграли:('
            b = f' Попробовать снова?\nСлово было: <b>{game.word}</b>'

            await bot.send_photo(
                callback.from_user.id,
                open('images/0.png', 'rb'),
                a + b,
                parse_mode='HTML',
                reply_markup=keyboard,
            )

            await callback.message.delete()
        elif flag:
            if check_stat(callback.from_user.id):
                cort = get_from_stat(callback.from_user.id)
            else:
                append_to_statistics(callback.from_user.id)
                cort = 0, 0, 0, 0
            if game.player == 'BOT':
                cort_new = cort[1] + 1, cort[2] + 1, cort[3], cort[4]
                await bot.send_message(
                    callback.from_user.id,
                    text=f'''О, нет! Оппонент угадал слово..😕
Напомним, это было слово - <b>{game.word}</b>'''
                )
            else:
                cort_new = cort[1], cort[2], cort[3], cort[4] + 1
            update_base_stat(callback.from_user.id, cort_new)

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text='Играть 🎲',
                callback_data='start_play'
            ))

            keyboard.add(InlineKeyboardButton(
                text='Завершить ❌',
                callback_data='stop'
            ))
            if game.player == 'BOT':
                keyboard.add(InlineKeyboardButton(
                    text='Анализ игры 📈',
                    callback_data=f'aw: {game.word}.{game.all_letters}'
                ))
            else:
                keyboard.add(InlineKeyboardButton(
                    text='Что умеет этот бот ❓',
                    callback_data='help'
                ))

            await bot.send_message(
                chat_id=callback.from_user.id,
                text=f'Поздравляю! Вы угадали слово - <b>{game.word}</b>! Хотите сыграть ещё?',
                parse_mode='HTML',
                reply_markup=keyboard
            )

            await callback.message.delete()

        else:
            keyboard = get_keyboard(game)
            cap = f"Я загадал слово. Попробуй отгадать:\n{game.get_string()}"
            file = InputMedia(media=InputFile(
                f'images/{game.live}.png'),
                caption=cap)

            await callback.message.edit_media(file, reply_markup=keyboard)


@dispatcher.message_handler(content_types=['any'])
async def all_message(message):
    try:
        await message['contact']['user_id']
        await bot.send_message(message.from_user.id, 'Это контакт')

    except TypeError:
        await bot.send_message(message.from_user.id, 'Что ж тебе ответить..')
        await message.delete()


if __name__ == '__main__':
    executor.start_polling(dispatcher)
