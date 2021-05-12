from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler
import logging
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


game_rooms = {}

# Stages
PREPARE_GAME, IN_GAME = range(2)

# Callback data
JOIN, START, EXIT = range(3)


def get_players_ready_message(chat_id):
    message = "Esperando jugadores...\nUnidos: "

    if not chat_id:
        return message

    if chat_id in game_rooms:
        users = game_rooms[chat_id]
        for user in users:
            message += '\n' + user.first_name
    return message


def get_players_in_game_message(chat_id):
    message = "Jugadores: \n"

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


def clear_room(chat_id):
    if chat_id in game_rooms:
        game_rooms.pop(chat_id)


MAIN_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("Unirse", callback_data=str(JOIN)),
        InlineKeyboardButton("Empezar", callback_data=str(START)),
    ],
    [InlineKeyboardButton("X", callback_data=str(EXIT))],
]

MAIN_MENU_IN_GAME = [
    [InlineKeyboardButton("X", callback_data=str(EXIT))],
]


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(text='Bienvenido a Propensito Game\nEsperando jugadores...\n', reply_markup=InlineKeyboardMarkup(
        MAIN_MENU_KEYBOARD), quote=False)
    return PREPARE_GAME


def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Message', quote=False)
    return PREPARE_GAME


def main_menu(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_ready_message(
        chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD), quote=False)
    return PREPARE_GAME


def main_menu_in_game(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_in_game_message(
        chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_IN_GAME), quote=False)
    return IN_GAME


def join(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    chat_id = query.message.chat.id
    user = query.from_user

    added = add_player(chat_id, user)

    if added:
        query.edit_message_text(text=get_players_ready_message(
            chat_id), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))

    return PREPARE_GAME


def start_game(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Start the Game")
    return IN_GAME


def exit(update: Update, _: CallbackContext):
    query = update.callback_query
    clear_room(query.message.chat_id)
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main():
    updater = Updater(
        token=os.environ.get('TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PREPARE_GAME: [
                CommandHandler("main_menu", main_menu),
                CallbackQueryHandler(join, pattern='^' + str(JOIN) + '$'),
                CallbackQueryHandler(
                    start_game, pattern='^' + str(START) + '$'),
            ],
            IN_GAME: [
                CommandHandler("main_menu", main_menu_in_game),

            ],
        },
        fallbacks=[CallbackQueryHandler(exit, pattern='^' + str(EXIT) + '$')],
    )

    dispatcher.add_handler(conv_handler)

    # dispatcher.add_handler(
    #     CallbackQueryHandler(main_menu_callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
