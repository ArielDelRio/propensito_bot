from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello World')


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Message')


def callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def inlinequery(update: Update, _: CallbackContext) -> None:
    query_start = "Start Game"
    query_help = "Help message"

    keyboard = [
        [
            InlineKeyboardButton("Unirse", callback_data='join'),
            InlineKeyboardButton("Empezar", callback_data='start'),
        ],
        [InlineKeyboardButton("X", callback_data='3')],
    ]

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=query_start,
            input_message_content=InputTextMessageContent(
                'Esperando jugadores...'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=query_help,
            input_message_content=InputTextMessageContent(query_help),
        ),
    ]

    update.inline_query.answer(results)


def main():
    updater = Updater(
        token=os.environ.get('TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
