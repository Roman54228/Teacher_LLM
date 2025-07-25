import os
import logging
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_loader import config

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Telegram библиотека недоступна: {e}")
    print("📦 Установите: pip install python-telegram-bot")
    TELEGRAM_AVAILABLE = False

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration from config.yaml
BOT_TOKEN = config.get('telegram.bot_token')
WEB_APP_URL = config.get('telegram.web_app_url', 'http://localhost:5000')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Create Web App button
    keyboard = [
        [InlineKeyboardButton(
            "🎯 Начать подготовку к собеседованию", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')],
        [InlineKeyboardButton("📊 Статистика", callback_data='stats')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🎯 **Добро пожаловать в Interview Prep Bot!**

Привет, {user.first_name}! Я помогу тебе подготовиться к техническим собеседованиям.

**Что я умею:**
• Тесты по Python, ML, NLP и Computer Vision
• ИИ-объяснения сложных вопросов 
• Отслеживание прогресса и уровня
• Персонализированные рекомендации
• Геймификация обучения

**Твой уровень определяется по баллам:**
🥉 Junior (0-59%)
🥈 Middle (60-79%) 
🏆 Senior (80%+)

Нажми кнопку ниже, чтобы начать!
    """
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'about':
        about_text = """
ℹ️ **О Interview Prep Bot**

Этот бот создан для подготовки к техническим собеседованиям в IT.

**Технологии:**
• YandexGPT для ИИ-объяснений
• PostgreSQL для хранения прогресса
• Telegram Mini Apps для удобного интерфейса

**Категории вопросов:**
🐍 Python - основы языка, структуры данных
🤖 Machine Learning - алгоритмы, метрики
💬 NLP - обработка текста, модели
👁️ Computer Vision - CNN, обработка изображений

**Разработчик:** @your_username
**Версия:** 1.0
        """
        
        keyboard = [[InlineKeyboardButton("← Назад", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            about_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'stats':
        # Here you could fetch user stats from database
        stats_text = """
📊 **Твоя статистика**

Для просмотра подробной статистики запусти приложение.

**Общие данные:**
• Всего пользователей: 1,000+
• Вопросов в базе: 100+
• Категорий: 4

**Популярные категории:**
1. Python (45%)
2. Machine Learning (30%)
3. NLP (15%)
4. Computer Vision (10%)
        """
        
        keyboard = [
            [InlineKeyboardButton(
                "📱 Открыть приложение", 
                web_app=WebAppInfo(url=WEB_APP_URL)
            )],
            [InlineKeyboardButton("← Назад", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'back_to_main':
        # Return to main menu
        await start(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🆘 **Помощь по Interview Prep Bot**

**Команды:**
/start - Главное меню
/help - Эта справка
/stats - Быстрая статистика

**Как пользоваться:**
1. Нажми "Начать подготовку" в главном меню
2. Выбери категию для изучения
3. Отвечай на вопросы и изучай объяснения
4. Отслеживай свой прогресс

**Система уровней:**
• Junior (0-59%) - изучай основы
• Middle (60-79%) - развивай навыки  
• Senior (80%+) - готов к собеседованиям!

**Особенности:**
• ИИ-объяснения на русском языке
• Персональные рекомендации
• Сохранение прогресса
• Красивый интерфейс

Возникли вопросы? Пиши @your_support_username
    """
    
    keyboard = [[InlineKeyboardButton(
        "🎯 Начать обучение", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Quick stats command."""
    user_id = update.effective_user.id
    
    # Here you would fetch real user stats from database
    quick_stats = """
📊 **Быстрая статистика**

🏆 Твой уровень: Junior
📝 Отвечено вопросов: 0
🎯 Средний балл: 0%
⭐ Сильные стороны: -
📚 Слабые стороны: -

Для подробной статистики открой приложение!
    """
    
    keyboard = [[InlineKeyboardButton(
        "📱 Открыть приложение", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        quick_stats,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_AVAILABLE:
        print("❌ Telegram библиотека недоступна!")
        print("📦 Установите: pip install python-telegram-bot")
        return
        
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        print("❌ Ошибка: Telegram Bot Token не настроен!")
        print("📝 Для настройки:")
        print("1. Создайте бота у @BotFather в Telegram")
        print("2. Скопируйте токен в config.yaml → telegram.bot_token") 
        print("3. Перезапустите бота")
        return
        
    print(f"🚀 Запуск Telegram бота...")
    print(f"🔗 Web App URL: {WEB_APP_URL}")
    
    try:
        # Create the Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Run the bot
        print("✓ Bot запущен и готов к работе!")
        print("💬 Попробуйте команду /start в Telegram")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("🔧 Проверьте токен бота и интернет соединение")

if __name__ == '__main__':
    main()