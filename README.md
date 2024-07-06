# Telegram Bot

Этот проект представляет собой Telegram-бота, который предоставляет несколько функций, включая просмотр изображения, получение значений из Google Sheets, оплату через YooMoney и ввод даты в Google Sheets.

## Установка и настройка

### Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий на свой локальный компьютер:

```sh
git clone https://github.com/yourusername/telegram-bot.git
cd telegram-bot
```

### Шаг 2: Создание и активация виртуального окружения

Создайте виртуальное окружение и активируйте его:

```sh
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

Установите необходимые зависимости:

```sh
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

Создайте файл `.env` в корне проекта и добавьте следующие строки, заменив значения на ваши собственные:

```sh
TELEGRAM_TOKEN=ваш_телеграм_токен
YOOMONEY_CLIENT_ID=ваш_yoomoney_client_id
YOOMONEY_LINK=ваш_yoomoney_link
CREDS_FILE=путь_к_вашему_файлу_учетных_данных.json
SPREADSHEET_ID=ваш_google_spreadsheet_id
```

### Шаг 5: Настройка Google Sheets

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/).
2. Включите API Google Sheets и Google Drive.
3. Создайте учетные данные для службы (Service Account) и скачайте JSON файл с учетными данными.
4. Поделитесь вашим Google Sheets документом с email из JSON файла.

### Шаг 6: Запуск бота

Запустите бота с помощью следующей команды:

```sh
python bot.py
```

## Функции бота

### Команда `/start`

Отправляет сообщение с интерактивными кнопками:

- **Открыть на карте:** Ссылка на Яндекс.Карты с конкретным адресом.
- **Оплатить 2 рубля:** Ссылка для оплаты через YooMoney.
- **Посмотреть картинку:** Отправляет изображение.
- **Получить значение ячейки A2:** Получает значение из ячейки A2 Google Sheets.
- **Ввести дату в ячейку В2:** Запускает диалог для ввода даты, которая будет сохранена в ячейке B2 Google Sheets.

### Callback функции

- `show_image`: Отправляет изображение.
- `get_a2_value`: Получает значение из ячейки A2 Google Sheets.
- `input_date_start`: Запускает диалог для ввода даты.
- `input_date_receive`: Обрабатывает ввод даты и сохраняет ее в ячейке B2 Google Sheets.
- `input_date_cancel`: Отменяет ввод даты.

## Пример кода

```python
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackContext,
    CallbackQueryHandler, ConversationHandler, MessageHandler, filters
)
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токенов и других настроек из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
YOOMONEY_CLIENT_ID = os.getenv('YOOMONEY_CLIENT_ID')
YOOMONEY_LINK = os.getenv('YOOMONEY_LINK')
CREDS_FILE_PATH = os.getenv('CREDS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Настройка доступа к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_PATH, SCOPE)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Состояния для ConversationHandler
INPUT_DATE = 1

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Открыть на карте: улица Ленина, дом 1", url="https://yandex.ru/maps/?text=Ленина 1")],
        [InlineKeyboardButton("Оплатить 2 рубля", url=YOOMONEY_LINK)],
        [InlineKeyboardButton("Посмотреть картинку", callback_data='show_image')],
        [InlineKeyboardButton("Получить значение ячейки A2", callback_data='get_a2_value')],
        [InlineKeyboardButton("Ввести дату в ячейку В2", callback_data='input_date')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Вас приветствует тестовый телеграм-бот! Выберите действие:', reply_markup=reply_markup)

async def show_image(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Отправляем изображение
    with open('img1.jpg', 'rb') as img:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=img, caption="Вот ваша картинка")

async def get_a2_value(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем значение из ячейки A2
    cell_value = sheet.acell('A2').value
    await query.message.reply_text(f'Значение A2: {cell_value}')

async def input_date_start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    await query.message.reply_text('Введите дату в формате ДД.ММ.ГГГГ (например, 01.01.2024):')
    return INPUT_DATE

async def input_date_receive(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()

    if user_input and not user_input.startswith('/'):
        try:
            user_date = datetime.strptime(user_input, '%d.%m.%Y')
            sheet.update('B2', [[user_input]])  # Записываем введенную дату в ячейку B2
            await update.message.reply_text('Дата верна и записана в Google Sheets.')
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text('Дата неверна. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.')
            return INPUT_DATE

async def input_date_cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Ввод даты отменён.')
    return ConversationHandler.END

def input_date_command_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(input_date_start, pattern='input_date')],
        states={
            INPUT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_date_receive)]
        },
        fallbacks=[CommandHandler("cancel", input_date_cancel)]
    )

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_image, pattern='show_image'))
    application.add_handler(CallbackQueryHandler(get_a2_value, pattern='get_a2_value'))

    conv_handler = input_date_command_handler()
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
```

