import telebot
from time import localtime
from bs4 import BeautifulSoup
import requests
from langdetect import detect

invalid_messages = ['поиск игр', "календарь выхода игр", "назад", '/calendar', '/search']
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
reply_markup = keyboard1.row("Поиск игр", "Календарь выхода игр")

bot = telebot.TeleBot('6063851788:AAGLdSZW3L0WcBY33seBL8iYoPsXM-NSIfc')




@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, greeting(localtime()[3]), reply_markup=keyboard1)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEIfR1kL6vOZR8EKZnA_kPsLp0DqYZdowACCiMAAj5l4EiNWlrA3BiYxS8E')


@bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['search'])
def find_game(message):
    if message.text.lower() == 'поиск игр' or message.text == '/search':
        bot.send_message(message.chat.id, 'Введите точное название игры на английском.', reply_markup=keyboard2)
    elif detect(message.text) == 'ru' and not message.text.lower() in invalid_messages:
        bot.send_message(message.chat.id, 'Проверьте правильность написания.')
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


@bot.message_handler(['Календарь выхода игр'])
def calendar(message):
    print(message.text)
    url1 = 'https://stopgame.ru/games/dates/2023/' + str(localtime()[1])
    response1 = requests.get(url1)
    soup1 = BeautifulSoup(response1.text, 'lxml')
    gamelist = []
    if message.text.lower() == 'календарь выхода игр' or message.text == '/calendar':
        games = soup1.find_all('a', class_="_card_67304_1")
        for game in games:
            title = game.get('title')
            gamelist.append(title)
    print(gamelist)


bot.polling()
