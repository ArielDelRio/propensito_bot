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
    update.message.reply_text('Hello World')

def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Message')

def main_menu(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_ready_message(chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))

def callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    query.answer()
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
    dispatcher.add_handler(CommandHandler("main_menu", main_menu))

    # For @bot_name inline command use
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    dispatcher.add_handler(
        CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
