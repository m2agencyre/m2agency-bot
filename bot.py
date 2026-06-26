"""
m² Agency — Telegram Lead Bot
Квалификация лидов по недвижимости на первичном рынке.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ── Конфигурация ──────────────────────────────────────────────────────────────
BOT_TOKEN = "8709163271:AAEHVCAN3mYOJnY6yVCl4ee69Gd0yNhygWI"
CEO_CHAT_ID = 853426594

# ── Состояния диалога ─────────────────────────────────────────────────────────
COUNTRY, BUDGET, GOAL, TIMELINE, CONTACT = range(5)

# ── Логирование ───────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── Клавиатуры ────────────────────────────────────────────────────────────────

def kb_country() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("🇦🇪 Дубай", callback_data="Дубай"),
            InlineKeyboardButton("🇬🇪 Грузия", callback_data="Грузия"),
            InlineKeyboardButton("🇹🇭 Таиланд", callback_data="Таиланд"),
        ],
        [
            InlineKeyboardButton("🇨🇾 Кипр", callback_data="Кипр"),
            InlineKeyboardButton("🇮🇱 Израиль", callback_data="Израиль"),
            InlineKeyboardButton("Другая страна", callback_data="Другая страна"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def kb_budget() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("До $100К", callback_data="До $100К"),
            InlineKeyboardButton("$100–200К", callback_data="$100–200К"),
        ],
        [
            InlineKeyboardButton("$200–500К", callback_data="$200–500К"),
            InlineKeyboardButton("$500К+", callback_data="$500К+"),
        ],
        [
            InlineKeyboardButton("Пока не определился", callback_data="Пока не определился"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def kb_goal() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Инвестиция (сдача в аренду)", callback_data="Инвестиция (сдача в аренду)")],
        [InlineKeyboardButton("Рост капитала (перепродажа)", callback_data="Рост капитала (перепродажа)")],
        [InlineKeyboardButton("Для проживания", callback_data="Для проживания")],
        [InlineKeyboardButton("Ещё не решил", callback_data="Ещё не решил")],
    ]
    return InlineKeyboardMarkup(buttons)


def kb_timeline() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("В ближайший месяц", callback_data="В ближайший месяц"),
            InlineKeyboardButton("1–3 месяца", callback_data="1–3 месяца"),
        ],
        [
            InlineKeyboardButton("3–6 месяцев", callback_data="3–6 месяцев"),
            InlineKeyboardButton("Пока изучаю", callback_data="Пока изучаю"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


# ── Утилита: username пользователя ────────────────────────────────────────────

def get_username(user) -> str:
    if user.username:
        return f"@{user.username}"
    return "нет username"


def get_user_link(user) -> str:
    """Ссылка на диалог с пользователем."""
    return f"tg://user?id={user.id}"


# ── Шаг 1: /start или любое первое сообщение ──────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сброс диалога и начало с шага 1."""
    context.user_data.clear()

    text = (
        "Добро пожаловать в m² Agency. Мы работаем только с первичным рынком — "
        "застройщики Дубая, Грузии, Таиланда и ещё 9 стран. Комиссия с вас — 0%.\n\n"
        "Чтобы подобрать варианты, уточним несколько вещей. Какая страна вас интересует?"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=kb_country())
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=kb_country())

    return COUNTRY


# ── Шаг 2: страна выбрана ─────────────────────────────────────────────────────

async def country_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["country"] = query.data
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        "Какой бюджет рассматриваете?",
        reply_markup=kb_budget(),
    )
    return BUDGET


# ── Шаг 3: бюджет выбран ──────────────────────────────────────────────────────

async def budget_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["budget"] = query.data
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        "Цель покупки?",
        reply_markup=kb_goal(),
    )
    return GOAL


# ── Шаг 4: цель выбрана ───────────────────────────────────────────────────────

async def goal_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["goal"] = query.data
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        "Когда планируете принять решение?",
        reply_markup=kb_timeline(),
    )
    return TIMELINE


# ── Шаг 5: срок выбран ────────────────────────────────────────────────────────

async def timeline_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["timeline"] = query.data
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        "Отлично. Как вас зовут и как с вами связаться? (телефон или Telegram-ник)"
    )
    return CONTACT


# ── Шаг 6: контакт получен, уведомляем CEO ────────────────────────────────────

async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    contact_text = update.message.text.strip()
    context.user_data["contact"] = contact_text

    data = context.user_data

    # Ответ пользователю
    first_name = user.first_name or ""
    name_part = f", {first_name}" if first_name else ""
    await update.message.reply_text(
        f"Спасибо{name_part}! Мы получили вашу заявку.\n\n"
        "Наш специалист свяжется с вами в течение нескольких часов.\n\n"
        "Если хотите пообщаться прямо сейчас — @SolomonDavidovich\n\n"
        "Если появятся вопросы или захотите начать подбор заново — просто напишите /start"
    )

    # Уведомление CEO
    user_link = get_user_link(user)
    username_str = get_username(user)

    ceo_message = (
        "🔥 НОВЫЙ ЛИД — m² Agency\n\n"
        f"👤 Имя/контакт: {contact_text}\n"
        f"🌍 Страна: {data.get('country', '—')}\n"
        f"💰 Бюджет: {data.get('budget', '—')}\n"
        f"🎯 Цель: {data.get('goal', '—')}\n"
        f"⏰ Срок: {data.get('timeline', '—')}\n"
        f"📱 Telegram: {username_str}\n\n"
        f"Ответить: {user_link}"
    )

    try:
        await context.bot.send_message(
            chat_id=CEO_CHAT_ID,
            text=ceo_message,
        )
        logger.info("Уведомление CEO отправлено. User ID: %s", user.id)
    except Exception as e:
        logger.error("Не удалось отправить уведомление CEO: %s", e)

    context.user_data.clear()
    return ConversationHandler.END


# ── Обработчик «не та» кнопка / текст не в том месте ─────────────────────────

async def unexpected_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Напоминание выбрать кнопку, когда ожидается callback."""
    await update.message.reply_text(
        "Пожалуйста, выберите один из предложенных вариантов выше."
    )


async def unexpected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Устаревшая или неожиданная кнопка."""
    query = update.callback_query
    await query.answer("Начните сначала: /start", show_alert=False)


# ── Fallback: любое сообщение вне диалога ────────────────────────────────────

async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Предлагает написать /start при любом сообщении вне активного диалога."""
    await update.message.reply_text(
        "Если появятся вопросы или захотите начать подбор заново — просто напишите /start"
    )


# ── Сборка и запуск ───────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            COUNTRY: [
                CallbackQueryHandler(country_chosen),
                MessageHandler(filters.TEXT & ~filters.COMMAND, unexpected_text),
            ],
            BUDGET: [
                CallbackQueryHandler(budget_chosen),
                MessageHandler(filters.TEXT & ~filters.COMMAND, unexpected_text),
            ],
            GOAL: [
                CallbackQueryHandler(goal_chosen),
                MessageHandler(filters.TEXT & ~filters.COMMAND, unexpected_text),
            ],
            TIMELINE: [
                CallbackQueryHandler(timeline_chosen),
                MessageHandler(filters.TEXT & ~filters.COMMAND, unexpected_text),
            ],
            CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, contact_received),
                CallbackQueryHandler(unexpected_callback),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    # Любое сообщение вне активного диалога — предлагаем /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message))

    logger.info("Бот m² Agency запущен. Ожидание сообщений...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
