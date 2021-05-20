from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update, InlineKeyboardMarkup

import logging

import traceback
import html
import json

from telegram.parsemode import ParseMode


from src.constants import *
from src.helpers import *

logger = logging.getLogger(__name__)


def start(update: Update, _: CallbackContext):
    update.message.reply_sticker(
        sticker=STICKERS["PENNY_PUG_ANXIOUS"], quote=False)

    update.message.reply_text(text='Bienvenido a Propensito Game\nEsperando jugadores...\n', reply_markup=InlineKeyboardMarkup(
        MAIN_MENU_KEYBOARD), quote=False)
    return PREPARE_GAME


def help(update: Update, _: CallbackContext):
    update.message.reply_text('Help Message', quote=False)
    return PREPARE_GAME


def main_menu(update: Update, _: CallbackContext):
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_ready_message(
        chat_id,
        _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD), quote=False)
    return PREPARE_GAME


def main_menu_in_game(update: Update, _: CallbackContext):
    chat_id = update.message.chat.id
    update.message.reply_text(text=get_players_in_game_message(
        chat_id,
        _), reply_markup=InlineKeyboardMarkup(MAIN_MENU_IN_GAME), quote=False)
    return IN_GAME


def clear_all(update: Update, _: CallbackContext):
    update.message.reply_text(text="clear data", quote=False)
    _.bot_data.clear()
    return ConversationHandler.END


# Callbacks

def join(update: Update, _: CallbackContext):
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

    # Put questions inside a bot_data chat id to remove answered questions
    _.bot_data[query.message.chat_id]["questions"] = QUESTIONS

    send_poll(query.message.chat_id, _)

    return IN_GAME


def exit(update: Update, _: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    if chat_id in _.bot_data:
        _.bot_data.pop(chat_id)
    query.answer()
    query.message.reply_sticker(
        sticker=STICKERS["PENNY_PUG_HEART_BROKEN"], quote=False)
    query.edit_message_text(text="See you next time! 👋")
    return ConversationHandler.END


def receive_poll_answer(update: Update, _: CallbackContext):
    poll = update.poll

    chat_id = _.bot_data[poll.id]["chat_id"]
    question_index = _.bot_data[poll.id]['question_index']

    print('poll ------------\n')
    print(poll)
    print('\npoll ------------\n\n\n')

    print('bot data---------\n')
    print(_.bot_data)
    print('\nbot data---------\n\n\n')

    count_players = len(_.bot_data[chat_id]["players"])
    all_vote = poll.total_voter_count / count_players >= 1

    if all_vote:
        winners = get_winners_by_poll(poll)

        set_result_in_summary(poll.question, winners, chat_id, _)

        _.bot_data[chat_id]["questions"].pop(question_index)
        _.bot_data.pop(poll.id)

        end_polls = check_if_end_polls(chat_id, _)
        if not end_polls:
            send_poll(chat_id, _)
        else:
            _.bot.send_message(
                chat_id=chat_id, text=' '.join(map(str, _.bot_data[chat_id]['summary'])))
            _.bot.send_message(
                chat_id=chat_id, text="The game is over. Thanks for playing")
            _.bot.send_sticker(
                chat_id=chat_id, sticker=STICKERS["PENNY_PUG_THUMBS_UP"])

            return ConversationHandler.END


def error_handler(update: object, _: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:",
                 exc_info=_.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, _.error, _.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(_.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(_.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    chat_id = update.message.chat.id if update.message else update.callback_query.message.chat.id

    # Finally, send the message
    _.bot.send_message(chat_id=DEVELOPER_CHAT_ID,
                       text=message, parse_mode=ParseMode.HTML)

    _.bot.send_sticker(
        chat_id=chat_id, sticker=STICKERS["PENNY_PUG_SAD"])

    _.bot.send_message(chat_id=chat_id, text="Sorry i can't help you now 😔",
                       parse_mode=ParseMode.HTML)

    return ConversationHandler.END