from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import logging, asyncio, datetime
import requests

# Включение логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения пользователей и их данных
users = {}
subscriptions = {}

# Конфигурация Outline API
OUTLINE_API_URL = "http://127.0.0.1:8081/access-keys"
OUTLINE_API_KEY = "ВАШ_API_КЛЮЧ_OUTLINE"

# Функция для проверки подписки
async def check_subscriptions(context: CallbackContext):
    now = datetime.datetime.now()
    for user_id, sub_end in list(subscriptions.items()):
        if now >= sub_end:
            # Приостанавливаем доступ
            del subscriptions[user_id]
            await context.bot.send_message(chat_id=user_id, text="⛔ Ваш доступ приостановлен из-за нехватки средств. Пополните баланс для продолжения использования.")

# Создание нового ключа Outline
def create_outline_key():
    headers = {"Authorization": f"Bearer {OUTLINE_API_KEY}"}
    response = requests.post(OUTLINE_API_URL, headers=headers)
    if response.status_code == 200:
        key_data = response.json()
        return key_data["accessUrl"]  # Возвращает URL для подключения
    else:
        return None

# Команда /start с приветственным сообщением и кнопкой
async def start(update: Update, context: CallbackContext) -> None:
    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWVtbjR2dHIzcGdvaDdwMThqZ3M5bnBwMDN2cjdleDFmc3o1cmt6ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JSdj7V1G7wQIcDXVcN/giphy.gif"  # Вставьте ссылку на гифку
    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url)

    await update.message.reply_text(
        "Что может делать этот бот?\n"
        "В этом боте вы можете подключить быстрый и безопасный VPN.\n\n"
        "\U0001F44D Нажмите кнопку ниже, чтобы подключить VPN бесплатно!"
    )
    keyboard = [[InlineKeyboardButton("🎉 Подключить VPN 🎉", callback_data="connect_vpn")]]
    await update.message.reply_text("Жмите кнопку!", reply_markup=InlineKeyboardMarkup(keyboard))

# Обработчик кнопки подключения VPN
async def connect_vpn(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 100, "key": create_outline_key() or "Не удалось создать ключ"}
    
    await query.edit_message_text(
        f"Привет, {query.from_user.first_name}!\n\n"
        "Подключите VPN бесплатно! Дарим вам 100Р на баланс!\n\n"
        "💰 Самая низкая цена на рынке!\n"
        "🚀 Высокая скорость!\n"
        "🌍 Доступ ко всем сайтам!\n"
        "💳 Оплата картами РФ 🇷🇺 и СБП!\n\n"
        "Стоимость 100Р/мес за 1 устройство, до 5 устройств.\n\n"
        f"Ваш ключ: {users[user_id]['key']}"
    )
    keyboard = [[InlineKeyboardButton("🎉 Пополнить баланс 🎉", callback_data="menu")]]
    await query.message.reply_text("\U0001F44D Нажмите кнопку ниже!", reply_markup=InlineKeyboardMarkup(keyboard))

# Меню пополнения баланса
async def recharge_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("100Р", callback_data="pay_100"), InlineKeyboardButton("200Р", callback_data="pay_200")],
        [InlineKeyboardButton("300Р", callback_data="pay_300"), InlineKeyboardButton("500Р", callback_data="pay_500")]
    ]
    await query.edit_message_text(
        "Ваш баланс низкий. Пополните его для продолжения:\n\n"
        "Выберите сумму для пополнения:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработчик оплаты
async def process_payment(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Сумма пополнения
    amount = int(query.data.split("_")[1])
    if user_id in users:
        users[user_id]["balance"] += amount
        subscriptions[user_id] = datetime.datetime.now() + datetime.timedelta(days=30)
        users[user_id]["key"] = create_outline_key() or "Не удалось создать ключ"
        await query.edit_message_text(
            f"✅ Оплата успешна! Ваш баланс: {users[user_id]['balance']}Р.\n"
            f"🔑 Ваш ключ: {users[user_id]['key']}\n\n"
            "Доступ активирован на 30 дней!"
        )
        # Выбор устройства после оплаты
        keyboard = [
            [InlineKeyboardButton("📱 Android", callback_data="device_android")],
            [InlineKeyboardButton("📱 iOS (iPhone, iPad)", callback_data="device_ios")]
        ]
        await query.message.reply_text(
            "🎉 Поздравляем, вы активировали аккаунт, 100Р у вас на балансе!\n\n"
            "Теперь давайте настроим ваш VPN. Выберите тип вашего устройства:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Обработчик выбора устройства
async def device_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "device_android":
        await query.edit_message_text(
            "📱 Инструкции для Android:\n"
            "1. Скачайте приложение Outline из Google Play.\n"
            "2. Получите конфигурацию на нашем сайте.\n"
            "3. Импортируйте файл в приложение и подключитесь!"
        )
    elif query.data == "device_ios":
        await query.edit_message_text(
            "📱 Инструкции для iOS (iPhone, iPad):\n"
            "1. Скачайте приложение Outline из App Store.\n"
            "2. Получите конфигурацию на нашем сайте.\n"
            "3. Импортируйте файл в приложение и подключитесь!"
        )

# Основная функция запуска бота
def main() -> None:
    # Укажите токен вашего бота
    TOKEN = "7876814497:AAE8i2DlhaY4DFDqgUbMDd5oVFcJnT_wgI0"

    # Создание объекта приложения
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков команд и кнопок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(connect_vpn, pattern="connect_vpn"))
    application.add_handler(CallbackQueryHandler(recharge_menu, pattern="menu"))
    application.add_handler(CallbackQueryHandler(process_payment, pattern="pay_.*"))
    application.add_handler(CallbackQueryHandler(device_choice, pattern="device_.*"))

    # Задача для проверки подписок
    application.job_queue.run_repeating(check_subscriptions, interval=60, first=10)

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
