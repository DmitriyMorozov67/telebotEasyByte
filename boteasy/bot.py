import logging
import os

from dotenv import load_dotenv
import os

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

API_KEY = os.environ.get('API_KEY')
TOKEN = os.environ.get('TOKEN')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Приветствую! Я бот-конвертор!\n'
             'Для получения справки введите /help!'

    )


async def help(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Помощь по командам:\n'
             '- /start - запуск бота\n'
             '- /help - справка по командам\n'
             '- /convert конвертация суммы из одной валюты в другую'
    )


async def convert(update: Update, context: CallbackContext):
    text = update.message.text.split()
    if len(text) == 4 and text[1].isdigit():
        amount = round(float(text[1]), 2)
        from_currency = text[2].upper()
        to_currency = text[3].upper()

        url = (f'https://api.apilayer.com/exchangerates_data/'
               f'convert?to={to_currency}&from={from_currency}&amount={amount}')
        headers = {
            'apikey': API_KEY,
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(response.json()['info']['rate'])
            rate = response.json()['info']['rate']
            if rate:
                converted_amount = round(amount * rate, 2)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'{amount} {from_currency} = {converted_amount}'
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Не удалось найти информацию о валюте {to_currency}'
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Не удалось получить актуальные данные'
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Неверный формат команды\nПример: /convert 100 USD EUR'
        )


async def text_message(update: Update, context: CallbackContext):
    text = update.message.text
    username = update.effective_chat.username
    if 'привет' in text.lower():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Приветствую, {username}!'
        )
    elif 'пока' in text.lower():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Прощай, {username}!'
        )


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    convert_handler = CommandHandler('convert', convert)
    application.add_handler(convert_handler)

    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text_message)
    application.add_handler(text_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
