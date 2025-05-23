import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from aiogram.exceptions import TelegramBadRequest
import asyncio
from aiogram.exceptions import TelegramBadRequest

TOKEN = "7876814497:AAE8i2DlhaY4DFDqgUbMDd5oVFcJnT_wgI0"
PROVIDER_TOKEN = "390540012:LIVE:62444"
CONFIG_KZ = r"C:\Users\хозяин\Desktop\Sova\client1.ovpn"
DB_PATH = "sovavpn_users.db"
CHANNEL_USERNAME = "SovaVpnNews"
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"
INSTRUCTIONS_LINK = "https://sovavpn.online/"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Инициализация базы данных ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            start_date TEXT,
            server TEXT,
            balance INTEGER DEFAULT 0,
            vpn_subscriptions INTEGER DEFAULT 0
        )
    """)

    # Таблица истории платежей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            payment_type TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()

# --- Проверка подписки на канал ---
async def is_user_subscribed(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False

# --- Добавление пользователя в базу ---
def add_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (user_id, start_date, server, balance, vpn_subscriptions) VALUES (?, ?, ?, ?, ?)", 
                       (user_id, start_date, None, 0, 0))
        conn.commit()
    conn.close()

# --- Команда /start (профиль пользователя) ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    add_user(user_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, vpn_subscriptions FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    balance = user_data[0] if user_data else 0
    vpn_subs = user_data[1] if user_data else 0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Подключить VPN", callback_data="connect_vpn")],
        [InlineKeyboardButton(text="💳 Мой баланс", callback_data="menu")],
        [InlineKeyboardButton(text="📖 Инструкции", url=INSTRUCTIONS_LINK),
         InlineKeyboardButton(text="🆘 Помощь", url="https://t.me/Arthur_serg")]
    ])



    profile_text = f"""
👨‍💻 **Профиль пользователя**
📌 **ID:** `{user_id}`
💰 **Баланс:** {balance} ₽
🔐 **Активные VPN-подписки:** {vpn_subs}

📡 **Канал [🚀 Sova VPN]({CHANNEL_LINK})**
💬 Нажмите кнопку ⚡ Подключить VPN, чтобы настроить ваше устройство.
    """
    
    await message.answer(profile_text, parse_mode="Markdown", reply_markup=keyboard)


# --- Проверка подписки перед покупкой VPN ---
@dp.callback_query(F.data == "connect_vpn")
async def connect_vpn_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if await is_user_subscribed(user_id):
        vpn_price = 999
        amount = vpn_price * 100

        prices = [LabeledPrice(label=f"Подключение VPN ({vpn_price} ₽)", amount=amount)]
        
        await bot.send_invoice(
            chat_id=user_id,
            title="Подключение VPN",
            description=f"Вы покупаете SovaVpn с доступом НАВСЕГДАл за {vpn_price} ₽",
            provider_token=PROVIDER_TOKEN,
            currency="RUB",
            prices=prices,
            payload=f"vpn_{user_id}"
        )
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="🔄 Проверить подписку", callback_data="check_subscription")]
        ])
        await callback.message.answer("❗ Перед оплатой вам нужно подписаться на наш канал.", reply_markup=keyboard)

import asyncio
from aiogram.exceptions import TelegramBadRequest

import asyncio
from aiogram.exceptions import TelegramBadRequest

async def is_user_subscribed(user_id):
    """ Проверяет, подписан ли пользователь на канал """
    try:
        chat_member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest as e:
        print(f"Ошибка проверки подписки: {e}")  # Логирование ошибки
        return False  # Если ошибка, считаем, что не подписан

@dp.callback_query(F.data == "check_subscription")
@dp.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Перейти в канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="confirm_subscription")]
        ]
    )

    await callback.message.edit_text(
        "❗ Чтобы продолжить, подпишитесь на канал и нажмите '✅ Я подписался'.", 
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "confirm_subscription")
async def confirm_subscription_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Подтверждаем успешную подписку
    await callback.message.edit_text("✅ Отлично! Загружаю ваш профиль...")

    # Имитация команды /start (вызывает стартовый хендлер)
    await start_handler(callback.message)

# --- Подтверждение оплаты VPN ---
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# --- Обработчик успешной оплаты (сохранение в БД) ---
@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    user_id = message.from_user.id
    amount = message.successful_payment.total_amount // 100
    payment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if message.successful_payment.invoice_payload.startswith("vpn_"):
        payment_type = "VPN"
        cursor.execute("UPDATE users SET vpn_subscriptions = vpn_subscriptions + 1 WHERE user_id = ?", (user_id,))
        
        vpn_config = FSInputFile(CONFIG_KZ)
        await message.answer("✅ Оплата успешна! Ваша VPN подписка активирована на 1 год!")
        await message.answer_document(vpn_config)

        # Показываем меню выбора устройства
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 iPhone / iPad", callback_data="device_ios"),
             InlineKeyboardButton(text="🤖 Android", callback_data="device_android")],
            [InlineKeyboardButton(text="💻 Windows", callback_data="device_windows"),
             InlineKeyboardButton(text="🖥️ Apple Mac", callback_data="device_mac")],
            [InlineKeyboardButton(text="🐧 Linux", callback_data="device_linux"),
             InlineKeyboardButton(text="📺 Android TV", callback_data="device_android_tv")]
        ])
        await message.answer("🔧 **На каком устройстве вам нужно подключить VPN?**", reply_markup=keyboard)

    elif message.successful_payment.invoice_payload.startswith("balance_"):
        payment_type = "Баланс"
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id,))
        await message.answer(f"✅ Оплата успешна! Ваш баланс пополнен на {amount} ₽.")

    cursor.execute(
        "INSERT INTO payments (user_id, amount, payment_type, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, amount, payment_type, payment_time)
    )

    conn.commit()
    conn.close()

# --- Обработчики выбора устройства ---
@dp.callback_query(F.data.startswith("device_"))
async def device_selected_handler(callback: types.CallbackQuery):
    device = callback.data.split("_")[1]  # Получаем тип устройства

    instructions = {
        "ios": {
            "text": "📱 **Инструкция для iPhone / iPad**:\n\n"
                    "1️⃣ Скачайте **OpenVPN Connect**: [App Store](https://apps.apple.com/app/openvpn-connect/id590379981)\n"
                    "2️⃣ Откройте `.ovpn` файл и импортируйте его в OpenVPN.\n"
                    "3️⃣ Нажмите **'Connect'** и наслаждайтесь безопасным интернетом! 🔒",
            "images": ["C:/Users/хозяин/Desktop/SovaVpn/instructions/ios1.png",
                       "C:/Users/хозяин/Desktop/SovaVpn/instructions/ios2.png",
                       "C:/Users/хозяин/Desktop/SovaVpn/instructions/ios3.png"]
        },
        "android": {
            "text": "🤖 **Инструкция для Android**:\n\n"
                    "1️⃣ Установите **OpenVPN Connect**: [Google Play](https://play.google.com/store/apps/details?id=net.openvpn.openvpn)\n"
                    "2️⃣ Откройте `.ovpn` файл и добавьте его в OpenVPN.\n"
                    "3️⃣ Нажмите **'Connect'** и пользуйтесь интернетом без ограничений! 🔒",
            "images": ["C:/Users/хозяин/Desktop/SovaVpn/instructions/android1.png",
                       "C:/Users/хозяин/Desktop/photo_2025-03-15_19-09-29.jpg"]
        },
        "windows": {
            "text": "💻 **Инструкция для Windows**:\n\n"
                    "1️⃣ Скачайте **OpenVPN для Windows**: [Загрузить](https://openvpn.net/community-downloads/)\n"
                    "2️⃣ Установите и импортируйте `.ovpn` файл.\n"
                    "3️⃣ Нажмите **'Подключиться'** и пользуйтесь VPN! 🔒",
            "images": ["C:/Users/хозяин/Desktop/SovaVpn/instructions/windows1.png",
                       "C:/Users/хозяин/Desktop/SovaVpn/instructions/windows2.png"]
        },
        "mac": {
            "text": "🖥️ **Инструкция для Mac**:\n\n"
                    "1️⃣ Скачайте **OpenVPN**: [Загрузить](https://openvpn.net/downloads/openvpn-connect-v3-macos.dmg/)\n"
                    "2️⃣ Откройте `.ovpn` файл и импортируйте его в OpenVPN.\n"
                    "3️⃣ Подключитесь и пользуйтесь VPN! 🔒",
            "images": ["C:/Users/хозяин/Desktop/SovaVpn/instructions/mac1.png"]
        },
        "linux": {
            "text": "🐧 **Инструкция для Linux**:\n\n"
                    "1️⃣ Установите OpenVPN с помощью команды:\n"
                    "```sudo apt install openvpn```\n"
                    "2️⃣ Запустите VPN командой:\n"
                    "```sudo openvpn --config /путь_к_файлу.ovpn```",
            "images": []
        },
        "android_tv": {
            "text": "📺 **Инструкция для Android TV**:\n\n"
                    "1️⃣ Установите **OpenVPN Connect** через Google Play.\n"
                    "2️⃣ Импортируйте `.ovpn` файл.\n"
                    "3️⃣ Подключитесь к VPN!",
            "images": []
        }
    }

    instruction = instructions.get(device)

    if instruction:
        await callback.message.answer(instruction["text"], parse_mode="Markdown", disable_web_page_preview=True)
        for image_path in instruction["images"]:
            await callback.message.answer_photo(photo=FSInputFile(image_path))

    await callback.answer()

# --- Просмотр истории платежей ---
@dp.message(Command("payments"))
async def show_payments(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT amount, payment_type, timestamp FROM payments WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
    payments = cursor.fetchall()
    conn.close()

    history = "\n".join([f"💰 {row[0]} ₽ | {row[1]} | 🕒 {row[2]}" for row in payments]) if payments else "📜 У вас пока нет платежей."
    await message.answer(f"📜 **История платежей:**\n\n{history}", parse_mode="Markdown")

# --- Запуск бота ---
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())