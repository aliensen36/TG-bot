from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токенов и других настроек из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
YOOMONEY_LINK = os.getenv('YOOMONEY_LINK')
CREDS_FILE_PATH = os.getenv('CREDS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Настройка доступа к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_PATH, SCOPE)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Узнай, в каких городах есть улица Ленина, дом 1", url="https://yandex.ru/maps/?text=Ленина 1")],
        [InlineKeyboardButton("Оплатить 2 рубля", url=YOOMONEY_LINK)],
        [InlineKeyboardButton("Посмотреть картинку", callback_data='show_image')],
        [InlineKeyboardButton("Получить значение A2", callback_data='get_a2_value')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

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

def main() -> None:
    # Создаем Application и передаем токен вашего бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_image, pattern='show_image'))
    application.add_handler(CallbackQueryHandler(get_a2_value, pattern='get_a2_value'))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
