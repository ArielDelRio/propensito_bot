from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


game_rooms = {}


def get_players_ready_message(chat_id):
    message = "Esperando jugadores...\nUnidos: "

    if not chat_id:
        return message

    if chat_id in game_rooms:
        users = game_rooms[chat_id]
        for user in users:
            message += '\n' + user.first_name
    return message


def add_player(chat_id, user):
    if chat_id in game_rooms.keys():
        if user not in game_rooms[chat_id]:
            game_rooms[chat_id].append(user)
            return True
        return False
    else:
        game_rooms[chat_id] = [user]
        return True


MAIN_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("Unirse", callback_data='join'),
        InlineKeyboardButton("Empezar", callback_data='start'),
    ],
    [InlineKeyboardButton("X", callback_data='3')],
]


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello World', quote=False)


def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Message', quote=False)


def main_menu(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_ready_message(
        chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD), quote=False)


def callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    chat_id = query.message.chat.id
    user = query.from_user

    added = add_player(chat_id, user)

    if added:
        query.edit_message_text(text=get_players_ready_message(
            chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))


def main():
    updater = Updater(
        token=os.environ.get('TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("main_menu", main_menu))

    dispatcher.add_handler(
        CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
