import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import wikipediaapi

# Настройки
API_TOKEN = 'ВАШ_ТОКЕН'  # Замените на токен от BotFather
DATABASE_NAME = 'history_bot.db'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Wikipedia API с user-agent
wiki = wikipediaapi.Wikipedia('ru', user_agent="HistoryBot/1.0 (your_email@example.com)")

# Клавиатура с командами
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="История Древнего мира")],
    [KeyboardButton(text="История Средних веков")],
    [KeyboardButton(text="История Нового времени")],
    [KeyboardButton(text="Викторина"), KeyboardButton(text="Таблица лидеров")]
], resize_keyboard=True)

# Функции работы с базой данных
def get_or_create_user(user_id, username):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result is None:
        cursor.execute("INSERT INTO users (user_id, username, score) VALUES (?, ?, ?)", (user_id, username, 0))
        conn.commit()
        score = 0
    else:
        score = result[0]
    
    conn.close()
    return score

def update_score(user_id, points):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 5")
    results = cursor.fetchall()
    
    conn.close()
    return results

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Аноним"
    get_or_create_user(user_id, username)
    
    await message.answer("Привет! Выбери период истории или начни викторину.", reply_markup=main_keyboard)

# Обработчик текстовых сообщений
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Аноним"

    if message.text.startswith("История"):
        period = message.text.replace("История ", "")
        events = {
            "Древнего мира": "Появление письменности в Шумере (3200 год до н.э.)",
            "Средних веков": "Подписание Великой хартии вольностей (1215 год, Англия)",
            "Нового времени": "Начало промышленной революции (XVIII век, Великобритания)"
        }
        response = events.get(period, "Нет информации по этому периоду.")
        await message.answer(response)

    elif message.text == "Викторина":
        question = "Когда началась Первая мировая война?"
        options = ["1914", "1917", "1939"]
        
        quiz_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=opt)] for opt in options], resize_keyboard=True
        )
        await message.answer(question, reply_markup=quiz_keyboard)

    elif message.text in ["1914", "1917", "1939"]:  # Проверяем ответы на викторину
        if message.text == "1914":
            update_score(user_id, 10)
            await message.answer("Правильно! 🎉 Ты заработал 10 баллов.")
        else:
            await message.answer("Неправильно. Попробуй ещё раз!")

    elif message.text == "Таблица лидеров":
        leaders = get_leaderboard()
        if leaders:
            leaderboard_text = "🏆 ТОП-5 игроков:\n"
            for i, (username, score) in enumerate(leaders, start=1):
                leaderboard_text += f"{i}. {username}: {score} баллов\n"
        else:
            leaderboard_text = "Пока нет участников в таблице лидеров."
        
        await message.answer(leaderboard_text)

    else:
        await message.answer("Я не понимаю этот запрос. Выбери команду из меню.")
# Запуск бота
async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
