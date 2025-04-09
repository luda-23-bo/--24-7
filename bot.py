
import os
import random
from datetime import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters, CallbackContext
)

TOKEN = os.getenv("BOT_TOKEN")

# --- Команди ---
GOAL, WEIGHT, ACTIVITY = range(3)
REMINDER_TIME = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = [["/products", "/schedule"],
            ["/faq", "/motivation"],
            ["/reminder", "/profile"]]
    reply_markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! Я бот Herbalife. Обери команду з меню:",
        reply_markup=reply_markup
    )

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Ось деякі продукти Herbalife:
"
        "- Formula 1 — білковий коктейль
"
        "- Herbal Aloe — напій для покращення травлення
"
        "- Thermo Complete — енергетичні таблетки
"
        "- Protein Bar — білковий батончик

"
        "Хочеш більше інформації про якийсь продукт — просто напиши його назву!"
    )
    await update.message.reply_text(text)

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Приклад графіку прийому продукції:

"
        "Сніданок:
"
        "- Formula 1 (коктейль)
"
        "- Чай Thermo

"
        "Обід:
"
        "- Збалансована їжа
"
        "- Aloe напій

"
        "Вечеря:
"
        "- Formula 1 (за бажанням)
"
        "- Легка вечеря"
    )
    await update.message.reply_text(text)

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Найчастіші питання:

"
        "1. *Чи можна схуднути з Herbalife?*
"
        "Так, при правильному режимі та раціоні.

"
        "2. *Чи безпечно вживати продукцію щодня?*
"
        "Так, вона створена для щоденного вживання.

"
        "3. *Чи можна поєднувати з фізичними навантаженнями?*
"
        "Обов’язково! Це підсилює ефект.

"
        "4. *Що робити, якщо я забув прийом?*
"
        "Просто повернись до графіка — не страшно пропустити один раз."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Твоє тіло — твій дім. Дбай про нього!",
        "Результат приходить до тих, хто діє.",
        "Кожен день — новий шанс бути кращим.",
        "Не здавайся. Зміни вже почались!",
        "Сьогодні ти на крок ближче до мети!"
    ]
    await update.message.reply_text(random.choice(quotes))

# --- Profile: персональні поради ---
async def profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Яка твоя мета?
Вибери одну з трьох:
- Схуднення
- Набір маси
- Підтримка форми"
    )
    return GOAL

async def profile_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text.strip().lower()
    await update.message.reply_text("Яка твоя поточна вага в кг?")
    return WEIGHT

async def profile_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = update.message.text.strip()
    await update.message.reply_text("Оціни рівень своєї фізичної активності:
- Низький
- Середній
- Високий")
    return ACTIVITY

async def profile_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activity = update.message.text.strip().lower()
    goal = context.user_data['goal']
    weight = context.user_data['weight']

    if "схуднення" in goal:
        advice = f"Твоя мета — схуднення.
Рекомендую:
- Коктейль Formula 1 на сніданок та вечерю
- Більше води (≈ {int(float(weight)*30)} мл)
- Більше руху"
    elif "набір" in goal:
        advice = "Твоя мета — набір маси.
Рекомендую:
- Коктейль + білкові перекуси
- Мінімум 120 г білка в день
- Тренування з вагами"
    else:
        advice = "Твоя мета — підтримка форми.
Тримай баланс:
- Коктейль Formula 1 на сніданок
- Вода та збалансоване харчування
- 30 хв активності щодня"

    await update.message.reply_text(advice)
    return ConversationHandler.END

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опитування скасовано.")
    return ConversationHandler.END

# --- Reminder ---
async def send_reminder(context: CallbackContext):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=random.choice([
            "Не забудь випити коктейль Formula 1!",
            "Час для здорового вибору!",
            "Гідратація — ключ до результату. Попий води!",
            "Крок за кроком — ти досягнеш мети!"
        ])
    )

async def reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("В який час щодня надсилати нагадування? (Формат: 09:00)")
    return REMINDER_TIME

async def reminder_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        h, m = map(int, update.message.text.strip().split(":"))
        reminder = time(hour=h, minute=m)
        context.job_queue.run_daily(
            send_reminder,
            time=reminder,
            chat_id=update.effective_chat.id,
            name=str(update.effective_chat.id)
        )
        await update.message.reply_text(f"Нагадування встановлено на {h:02d}:{m:02d} щодня!")
        return ConversationHandler.END
    except:
        await update.message.reply_text("Формат неправильний. Введи час як HH:MM (наприклад, 08:30)")
        return REMINDER_TIME

async def reminder_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Нагадування скасовано.")
    return ConversationHandler.END

# --- Main ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("products", products))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("motivation", motivation))

    profile_conv = ConversationHandler(
        entry_points=[CommandHandler("profile", profile_start)],
        states={
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_goal)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_weight)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_activity)],
        },
        fallbacks=[CommandHandler("cancel", profile_cancel)]
    )

    reminder_conv = ConversationHandler(
        entry_points=[CommandHandler("reminder", reminder_start)],
        states={
            REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_set)],
        },
        fallbacks=[CommandHandler("cancel", reminder_cancel)]
    )

    app.add_handler(profile_conv)
    app.add_handler(reminder_conv)

    app.run_polling()

if __name__ == "__main__":
    main()
