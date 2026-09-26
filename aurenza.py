from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI


# =========================
# KEYS
# =========================

TELEGRAM_TOKEN = ""
OPENROUTER_KEY = ""


# =========================
# OPENROUTER
# =========================

ai = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# =========================
# AURENZA PERSONALITY
# =========================

SYSTEM_PROMPT = """
You are Aurenza, an intelligent AI assistant on Telegram.

Be friendly, natural, helpful and clear.
Answer questions accurately.
Keep simple answers concise.
Explain complicated things simply.
Help with learning, coding, writing, business,
planning and everyday questions.

Never claim to be human.
"""


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Aurenza is online!\n\n"
        "I'm ready. Send me a message."
    )


# =========================
# /HELP
# =========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Aurenza Help\n\n"
        "/start — Start Aurenza\n"
        "/help — Show help\n"
        "/new — New conversation\n\n"
        "Or simply send me a message."
    )


# =========================
# /NEW
# =========================

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["conversation"] = []

    await update.message.reply_text(
        "🧹 New conversation started."
    )


# =========================
# AI MESSAGE HANDLER
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_message = update.message.text

    try:

        await update.message.chat.send_action("typing")

        conversation = context.user_data.get(
            "conversation",
            []
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(conversation)

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        response = ai.chat.completions.create(
            model="openrouter/free",
            messages=messages
        )

        answer = response.choices[0].message.content

        conversation.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        context.user_data["conversation"] = conversation[-20:]

        await update.message.reply_text(answer)

    except Exception as error:

        print("AI ERROR:", repr(error))

        await update.message.reply_text(
            "⚠️ Aurenza couldn't get an AI response right now."
        )


# =========================
# MAIN
# =========================

def main():

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("new", new_chat)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("🤖 Aurenza is running...")

    app.run_polling(
        drop_pending_updates=True,
        poll_interval=1
    )


if __name__ == "__main__":
    main()
