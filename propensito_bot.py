from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CallbackQueryHandler, PollHandler, ConversationHandler, MessageHandler, PicklePersistence
import logging
import os
from telegram.ext import filters

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


def get_players_ready_message(chat_id, context):
    message = "Esperando jugadores...\nUnidos: "

    if chat_id in context.bot_data:
        users = context.bot_data[chat_id]["players"]
        for user in users:
            message += '\n' + user.first_name
    return message


def get_players_in_game_message(chat_id, context):
    message = "Jugadores: \n"

    if chat_id in context.bot_data:
        users = context.bot_data[chat_id]["players"]
        for user in users:
            message += '\n' + user.first_name
    return message


def add_player(chat_id, user, context):
    if not context.bot_data.get(chat_id):
        context.bot_data[chat_id] = {"players": [user]}
        return True

    if user not in context.bot_data[chat_id]["players"]:
        context.bot_data[chat_id]["players"].append(user)
        return True
    return False


def send_poll(chat_id, context):

    question = QUESTIONS[randint(0, 9)]["q"]

    answers = [
        player.first_name for player in context.bot_data[chat_id]["players"]]

    message = context.bot.send_poll(
        chat_id,
        question,
        answers,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        # chat_id: {
        #     "players": context.bot_data[chat_id]["players"]
        # },
        message.poll.id: {
            # "answers": answers,
            # "message_id": message.message_id,
            "chat_id": chat_id,
            # "question": question,
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
        chat_id,
        _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD), quote=False)
    return PREPARE_GAME


def main_menu_in_game(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_in_game_message(
        chat_id,
        _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_IN_GAME), quote=False)
    return IN_GAME


def join(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    user = query.from_user
    bot = query.bot.get_me()
    chat_id = query.message.chat_id

    added = add_player(chat_id, user, _)
    # added = add_player(chat_id, bot, _)

    if added:
        query.edit_message_text(text=get_players_ready_message(
            chat_id,
            _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))

    return PREPARE_GAME


def start_game(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Start the Game")

    send_poll(query.message.chat_id, _)

    return IN_GAME


def exit(update: Update, _: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    if chat_id in _.bot_data:
        _.bot_data.pop(chat_id)
        print("Check all bot Data")
        print(_.bot_data)
        print("Check if exist yet")
        print(chat_id in _.bot_data)
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def receive_poll_answer(update: Update, _: CallbackContext):
    # answer = update.poll_answer
    # poll_id = answer.poll_id

    chat_id = _.bot_data[update.poll.id]["chat_id"]

    print('poll ------------\n')
    print(update.poll)
    print('\npoll ------------\n\n\n')

    print('bot data---------\n')
    print(_.bot_data)
    print('\nbot data---------\n\n\n')

    # all_vote = all([vote['voter_count'] > 0 for vote in update.poll.options])
    count_players = len(_.bot_data[chat_id]["players"])
    all_vote = update.poll.total_voter_count / count_players >= 1

    # print([vote['voter_count'] > 0 for vote in update.poll.options])
    if all_vote:
        send_poll(chat_id, _)
        _.bot_data.pop(update.poll.id)


def clear_all(update: Update, _: CallbackContext):
    update.message.reply_text(text="clear data", quote=False)
    _.bot_data.clear()
    return ConversationHandler.END


def main():
    persistence = PicklePersistence(filename='conversationbot')

    updater = Updater(
        token=os.environ.get('TOKEN'), persistence=persistence, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help))

    cbq_exit = CallbackQueryHandler(exit, pattern='^' + str(EXIT) + '$')
    ch_cls = CommandHandler("cls", clear_all)

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
        fallbacks=[cbq_exit, ch_cls],
        per_user=False,
        per_message=False,
        per_chat=True,
        name="GameHandler",
        persistent=True
    )

    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("main_menu", main_menu))
    # dispatcher.add_handler(CallbackQueryHandler(
    #     join, pattern='^' + str(JOIN) + '$'))

    # dispatcher.add_handler(CallbackQueryHandler(
    #     start_game, pattern='^' + str(START) + '$'))

    # dispatcher.add_handler(CallbackQueryHandler(
    #     exit, pattern='^' + str(EXIT) + '$'))

    dispatcher.add_handler((PollHandler(receive_poll_answer)))

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
