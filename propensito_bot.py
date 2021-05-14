from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler, PollHandler, ConversationHandler, MessageHandler, PicklePersistence
import logging
import os

from telegram.ext.basepersistence import BasePersistence
from telegram.ext.filters import Filters
from telegram.ext.pollanswerhandler import PollAnswerHandler


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


def send_poll(chat_id, context):
    players = chat_id in game_rooms and game_rooms[chat_id]

    if not players:
        raise ValueError

    message = context.bot.send_poll(
        chat_id,
        "Primera Pregunta",
        players,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": players,
            "message_id": message.message_id,
            "chat_id": chat_id,
            "answers": 0,
        }
    }

    context.bot_data.update(payload)


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

    send_poll(update.effective_chat.id, _)

    return IN_GAME


def exit(update: Update, _: CallbackContext):
    query = update.callback_query
    clear_room(query.message.chat_id)
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def receive_poll_answer(update: Update, _: CallbackContext):
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = _.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        answer_string += questions[question_id]
    _.bot.send_message(
        _.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.first_name} feels {answer_string}!",
    )


def main():
    persistence = PicklePersistence(filename='conversationbot')

    updater = Updater(
        token=os.environ.get('TOKEN'), persistence=persistence, use_context=True)

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
        per_user=False,
        per_message=False,
        name="GameHandler",
        # persistent=True
    )

    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))

    dispatcher.add_handler(conv_handler)

    # dispatcher.add_handler(
    #     CallbackQueryHandler(main_menu_callback_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
