from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler, PollHandler, ConversationHandler, MessageHandler, PicklePersistence
import logging
import os

from telegram.ext.basepersistence import BasePersistence
from telegram.ext.filters import Filters
from telegram.ext.pollanswerhandler import PollAnswerHandler

from random import randint


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

QUESTIONS = [
    {"q": "¿Quién es más probable que mate a alguien accidentalmente?", "checked": False},
    {"q": "¿Quién es más probable que no le gusten mucho las películas?", "checked": False},
    {"q": "¿Quién es más probable que se convierta en un famoso actor/actriz?",
        "checked": False},
    {"q": "¿Quién es más probable que huya para no unirse al circo?", "checked": False},
    {"q": "¿Quién es más probable que salte de un tren en movimiento?", "checked": False},
    {"q": "¿Quién es más probable que tenga paranoias?", "checked": False},
    {"q": "¿Quién es más probable que sea el más atlético?", "checked": False},
    {"q": "¿Quién es más probable que vea películas románicas?", "checked": False},
    {"q": "¿Quién es más probable que se convierta en un stripper?", "checked": False},
    {"q": "¿Quién es más probable que sea detenido por acosar a un oficial de policía?", "checked": False}
]

# Stages
PREPARE_GAME, IN_GAME = range(2)

# Callback data
JOIN, START, EXIT = range(3)


def get_players_ready_message(context):
    message = "Esperando jugadores...\nUnidos: "

    if context.user_data.get("players"):
        users = context.user_data["players"]
        for user in users:
            message += '\n' + user.first_name
    return message


def get_players_in_game_message(context):
    message = "Jugadores: \n"

    if context.user_data.get("players"):
        users = context.user_data["players"]
        for user in users:
            message += '\n' + user.first_name
    return message


def add_player(user, context):
    if not context.user_data.get("players"):
        context.user_data["players"] = [user]
        return True
    if user not in context.user_data['players']:
        context.user_data["players"].append(user)
        return True
    else:
        return False


def send_poll(chat_id, context):

    question = QUESTIONS[randint(0, 9)]["q"]

    answers = [player.first_name for player in context.user_data["players"]]

    message = context.bot.send_poll(
        chat_id,
        question,
        answers,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "answers": answers,
            "message_id": message.message_id,
            "chat_id": chat_id,
            "question": question,
        },
        "players": context.user_data["players"]
    }

    context.user_data.update(payload)

    # context.bot_data.update(payload)


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
    print(_.user_data)
    update.message.reply_text('Help Message', quote=False)
    return PREPARE_GAME


def main_menu(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_ready_message(
        _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD), quote=False)
    return PREPARE_GAME


def main_menu_in_game(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_in_game_message(
        _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_IN_GAME), quote=False)
    return IN_GAME


def join(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    user = query.from_user
    bot = query.bot.get_me()

    added = add_player(user, _)
    added = add_player(bot, _)

    if added:
        query.edit_message_text(text=get_players_ready_message(
            _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))

    return PREPARE_GAME


def start_game(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Start the Game")

    # send_poll(update.effective_chat.id, _)
    question = QUESTIONS[randint(0, 9)]["q"]

    answers = [player.first_name for player in _.user_data["players"]]

    message = _.bot.send_poll(
        update.effective_chat.id,
        question,
        answers,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "answers": answers,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "question": question,
        },
    }
    _.chat_data.update(payload)

    _.user_data.update(payload)

    return IN_GAME


def exit(update: Update, _: CallbackContext):
    query = update.callback_query
    _.user_data.clear()
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def receive_poll_answer(update: Update, _: CallbackContext):
    answer = update.poll_answer
    poll_id = answer.poll_id
    # try:
    #     questions = _.bot_data[poll_id]["answers"]
    # # this means this poll answer update is from an old poll, we can't do our answering then
    # except KeyError:
    #     return
    # selected_options = answer.option_ids
    # answer_string = ""
    # for question_id in selected_options:
    #     answer_string += questions[question_id]

    # print("Chat data")
    # print(_.chat_data)
    print("Chat data oever dispatcher")
    print(_.dispatcher.chat_data)

    # print("User data")
    # print(_.user_data)

    send_poll(_.user_data[poll_id]["chat_id"], _)

    # _.bot.send_message(
    #     _.bot_data[poll_id]["chat_id"],
    #     f"{update.effective_user.first_name} feels {answer_string}!",
    # )


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
                    start_game, pattern='^' + str(START) + '$', pass_user_data=True),
            ],
            IN_GAME: [
                CommandHandler("main_menu", main_menu_in_game),
            ],
        },
        fallbacks=[CallbackQueryHandler(exit, pattern='^' + str(EXIT) + '$')],
        per_user=False,
        per_message=False,
        per_chat=True,
        name="GameHandler",
        persistent=True
    )

    dispatcher.add_handler(PollAnswerHandler(
        receive_poll_answer))

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
