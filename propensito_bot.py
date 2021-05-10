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

    chat_id = query.message.chat.id
    if chat_id in chats.keys():
        if query.from_user not in chats[chat_id]:
            chats[chat_id].append(query.from_user)
    else:
        chats[chat_id] = [query.from_user]

    query.edit_message_text(text=get_players_ready_message(chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))

def inlinequery(update: Update, _: CallbackContext) -> None:
    update.inline_query.answer(get_inline_menu())


def main():
    updater = Updater(
        token=os.environ.get('TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    # For @bot_name inline command use
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    dispatcher.add_handler(
        CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
