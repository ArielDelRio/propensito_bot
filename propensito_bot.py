from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def get_inline_menu():
    return [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Main Menu",
            input_message_content=InputTextMessageContent(
                get_players_ready_message()),
            reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD)
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Help message",
            input_message_content=InputTextMessageContent("Help message"),
        ),
    ]

MAIN_MENU_KEYBOARD = [
        [
            InlineKeyboardButton("Unirse", callback_data='join'),
            InlineKeyboardButton("Empezar", callback_data='start'),
        ],
        [InlineKeyboardButton("X", callback_data='3')],
    ]


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello World')


def help_command(update: Update, _: CallbackContext) -> None:
def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Message')


def callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    users = []
    mess = "Esperando jugadores...\nUnidos: "

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    users.append(query.from_user.first_name)
    for user in users:
        mess += '\n' + user
    keyboard = [
        [
            InlineKeyboardButton("Unirse", callback_data='join'),
            InlineKeyboardButton("Empezar", callback_data='start'),
        ],
        [InlineKeyboardButton("X", callback_data='3')],
    ]
    query.edit_message_text(text=mess, reply_markup=InlineKeyboardMarkup(keyboard))

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

# def startgame_command(bot, update, args):
#     chat_id = update.message.chat_id
#     bot.send_message(chat_id, 'test')

def cmd_decir(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    update.message.chat.send_message('hiiii')

def main():
    updater = Updater(
        token=os.environ.get('TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    # dispatcher.add_handler(CommandHandler("dime", cmd_decir))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(callback_handler))

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == "__main__":
    main()
