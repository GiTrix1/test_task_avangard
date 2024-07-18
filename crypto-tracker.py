import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot, ParseMode
from telegram.ext import Updater, CommandHandler

# Загрузка переменных окружения
load_dotenv()

# Получение API ключа для CoinMarketCap
CMC_API_KEY = os.getenv('CMC_API_KEY')

# Получение API ключа для Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализация Telegram бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Словарь для хранения пороговых значений
thresholds = {}


# Функция для получения текущего курса криптовалюты
def get_crypto_price(symbol):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
    }
    params = {
        "symbol": symbol,
        "convert": "USD",
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if "data" in data:
        return data["data"][symbol]["quote"]["USD"]["price"]
    else:
        return None


# Функция для отправки уведомления в Telegram
def send_notification(chat_id, message):
    bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)


# Функция для проверки пороговых значений
def check_thresholds():
    while True:
        for symbol, (min_threshold, max_threshold, chat_id) in thresholds.items():
            price = get_crypto_price(symbol)
            if price:
                if price <= min_threshold or price >= max_threshold:
                    message = f"{symbol} достиг порога:\nТекущая цена: ${round(price, 2)}"
                    send_notification(chat_id, message)
        time.sleep(60)  # Проверка каждую минуту


# Обработчик команды /setthreshold
def set_threshold(update, context):
    if len(context.args) != 3:
        update.message.reply_text("Используйте команду: /setthreshold <symbol> <min_threshold> <max_threshold>\n"
                                  "Пример: /setthreshold BTC 1 2")
        return

    symbol = context.args[0].upper()
    min_threshold = float(context.args[1])
    max_threshold = float(context.args[2])
    chat_id = update.message.chat_id

    thresholds[symbol] = (min_threshold, max_threshold, chat_id)
    update.message.reply_text(f"Пороги установлены для {symbol}")


# Основная функция
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("setthreshold", set_threshold))

    updater.start_polling()
    print("Бот запущен")

    check_thresholds()

    updater.idle()


if __name__ == '__main__':
    main()
