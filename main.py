import telebot
from time import localtime
from bs4 import BeautifulSoup
import requests

invalid_messages = ['поиск игр', "календарь выхода игр", "назад", '/calendar', '/search']

monthes = ("Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль",
           "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь")


def greeting(time):
    if 5 < time < 11:
        return ' Доброе утро. Я помогу найти тебе игру, а также подскажу ближайшие выходы игр'
    elif 10 < time < 17:
        return 'Добрый день. Я помогу найти тебе игру, а также подскажу ближайшие выходы игр'
    elif 16 < time < 22:
        return 'Добрый вечер. Я помогу найти тебе игру, а также подскажу ближайшие выходы игр'
    else:
        return 'Доброй ночи. Я помогу найти тебе игру, а также подскажу ближайшие выходы игр'


def correct_name(text):
    if not text.isalnum():
        correct_text = text
        for i in range(len(text)):
            if not text[i].isalnum():
                correct_text = correct_text.replace(text[i], '_')
        return correct_text
    else:
        return text


keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
keyboard2 = telebot.types.ReplyKeyboardMarkup(True).row('Назад')
keyboard_calendar = telebot.types.InlineKeyboardMarkup()
keyboard_calendar.add(telebot.types.InlineKeyboardButton('◀', callback_data='lft'),
                      telebot.types.InlineKeyboardButton('Текущий', callback_data='cur'),
                      telebot.types.InlineKeyboardButton('▶', callback_data='rght'))
reply_markup = keyboard1.row("Поиск игр", "Календарь выхода игр")

bot = telebot.TeleBot('6063851788:AAGLdSZW3L0WcBY33seBL8iYoPsXM-NSIfc')




@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, greeting(localtime()[3]), reply_markup=keyboard1)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEIfR1kL6vOZR8EKZnA_kPsLp0DqYZdowACCiMAAj5l4EiNWlrA3BiYxS8E')


current_section = None


@bot.message_handler(commands=['calendar'])
def calendar(message):
    url = 'https://stopgame.ru/games/dates/2023/' + str(localtime()[1])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    parents = soup.find_all('div', class_="_calendar-date_dmef8_1")
    dates = {}

    for child in parents:
        if child.find_next_sibling().find('a', class_="_card_13hsk_1"):
            games = child.find_next_sibling().find_all('a', class_="_card_13hsk_1")
            pairs_games = []
            for game in games:
                pairs_games.append(game.get('title'))
            dates[child.text] = '\n     '.join(pairs_games)

    x = []

    for key, value in dates.items():
        x.append(f"{key}:\n     {value}")

    bot.send_message(message.chat.id, "Календарь выхода игр на " + monthes[localtime()[1] - 1] + ':\n' + '\n'.join(x),
                     reply_markup=keyboard_calendar)


@bot.callback_query_handler(func=lambda c: c.data == 'lft' or c.data == 'rght' or c.data == 'cur')
def next_month(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    url = None
    c = 0
    if call.data == 'rght':
        url = 'https://stopgame.ru/games/dates/2023/' + str(localtime()[1] + 1)
        c = 1
    elif call.data == 'lft':
        url = 'https://stopgame.ru/games/dates/2023/' + str(localtime()[1] - 1)
        c = -1
    elif call.data == 'cur':
        url = 'https://stopgame.ru/games/dates/2023/' + str(localtime()[1])

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    parents = soup.find_all('div', class_="_calendar-date_dmef8_1")
    dates = {}

    for child in parents:
        if child.find_next_sibling().find('a', class_="_card_13hsk_1"):
            games = child.find_next_sibling().find_all('a', class_="_card_13hsk_1")
            pairs_games = []
            for game in games:
                pairs_games.append(game.get('title'))
            dates[child.text] = '\n     '.join(pairs_games)

    x = []

    for key, value in dates.items():
        x.append(f"{key}:\n     {value}")

    bot.send_message(call.message.chat.id,
                     "Календарь выхода игр на " + monthes[localtime()[1] + c - 1] + ':\n' + '\n'.join(x),
                     reply_markup=keyboard_calendar)


@bot.message_handler(commands=['search'])
@bot.message_handler(content_types=['text'])
def find_game(message):
    if message.text.lower() == '/search':
        bot.send_message(message.chat.id, 'Введите точное название игры на английском.', reply_markup=keyboard2)
    url = 'https://stopgame.ru/game/' + correct_name(message.text.lower().replace(' ', '_'))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    images = soup.find_all('img', class_='_image_sh7r2_31')
    for image in images:
        src = image.get("src")
        if src:
            bot.send_photo(message.chat.id, src,
                           caption=f'{url} \nПользовательская оценка: ' +
                                   str(soup.find('span', class_="_users-rating__total_sh7r2_1").text))
        if not images and not (message.text.lower() in invalid_messages):
            bot.send_message(message.chat.id, 'Игра не найдена.')

        if soup.find('div', class_="_description__inner_qrsvr_1"):
            bot.send_message(message.chat.id,
                             '📄Краткое описание:📄 \n' + soup.find('div', class_="_description__inner_qrsvr_1").text)

        if soup.find('div', class_="_screenshot-grid_qrsvr_506"):
            screenshots = soup.find('div', class_="_screenshot-grid_qrsvr_506").find_all('a')
            bot.send_message(message.chat.id, 'Скриншоты:')
            x = []
            for screenshot in screenshots:
                href = screenshot.get('href')
                if href:
                    x.append(telebot.types.InputMediaPhoto(href))
            bot.send_media_group(message.chat.id, x)

        if soup.find('div', class_="_facts__text_qrsvr_1"):
            bot.send_message(message.chat.id,
                             'Интересный факт: ' + str(soup.find('div', class_="_facts__text_qrsvr_1").text))
        if message.text.lower() == 'назад':
            bot.send_message(message.chat.id, '👇Выберите одну из функций ниже:👇', reply_markup=keyboard1)
            pass


bot.polling()
