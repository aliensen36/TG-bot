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

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_image, pattern='show_image'))
    application.add_handler(CallbackQueryHandler(get_a2_value, pattern='get_a2_value'))

    # Регистрируем обработчик для ввода даты
    conv_handler = input_date_command_handler()
    application.add_handler(conv_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
