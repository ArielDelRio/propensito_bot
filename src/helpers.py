from random import randint

from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from src.constants import MAIN_MENU_KEYBOARD, STICKERS

from telegram.parsemode import ParseMode


def get_players_ready_message(chat_id, context):
    message = "Esperando jugadores...\nUnidos: "

    if chat_id in context.bot_data:
        users = context.bot_data[chat_id]["players"]
        for user in users:
            if user.id == context.bot_data[chat_id]["game_master"].id:
                message += user.first_name + " (GM🔸)"
            else:
                message += '\n' + user.first_name
    return message


def get_players_in_game_message(chat_id, context):
    message = "Jugadores: \n"

    if chat_id in context.bot_data:
        users = context.bot_data[chat_id]["players"]
        for user in users:
            if user.id == context.bot_data[chat_id]["game_master"].id:
                message += user.first_name + " (GM🔸)"
            else:
                message += '\n' + user.first_name
    return message


def add_player(user, chat_id, context):
    if not context.bot_data.get(chat_id):
        context.bot_data[chat_id] = {"players": [user]}
        return True

    if user not in context.bot_data[chat_id]["players"]:
        context.bot_data[chat_id]["players"].append(user)
        return True
    return False


def set_game_master(user, chat_id, context):
    context.bot_data[chat_id]["game_master"] = user


def is_game_master(user, chat_id, context):
    return user == context.bot_data[chat_id]["game_master"]


def clear_room(chat_id, context):
    context.bot_data.pop(chat_id)


def user_leave(user, chat_id, context):
    context.bot_data[chat_id]["players"].pop(user)


def count_players(chat_id, context):
    return len(context.bot_data[chat_id]["players"])


def send_poll(chat_id, context):

    questions = context.bot_data[chat_id]["questions"]

    # get random question index
    question_index = randint(0, len(questions) - 1)

    # get that question
    question = questions[question_index]["q"]

    answers = [
        player.first_name + " (" + player.name + ")" for player in context.bot_data[chat_id]["players"]]

    message = context.bot.send_poll(
        chat_id,
        question,
        answers,
        is_anonymous=True,
        allows_multiple_answers=True,
    )

    context.bot_data[chat_id]["current_poll"] = message.message_id

    context.bot_data.update({
        message.poll.id: {
            "chat_id": chat_id,
            "question_index": question_index
        }
    })


def get_winners_by_poll(poll):
    max_voter_count = 0
    winners = []
    for option in poll.options:
        # players with same max_voter_count
        if option.voter_count == max_voter_count:
            winners.append(option.text)

        # max_voter_count is upper then clear winners and put the new one
        if option.voter_count > max_voter_count:
            max_voter_count = option.voter_count
            winners.clear()
            winners = [option.text]

    return winners


def set_result_in_summary(question, winners, chat_id, context):
    result = {"q": question, "winners": winners}

    if "summary" not in context.bot_data[chat_id]:
        context.bot_data[chat_id]["summary"] = [result]
    else:
        context.bot_data[chat_id]["summary"].append(result)


def check_if_end_polls(chat_id, context):
    return len(context.bot_data[chat_id]["questions"]) == 0


def send_welcome_message(message_to_reply, chat_id, context):
    message_to_reply.reply_sticker(
        sticker=STICKERS["PENNY_PUG_ANXIOUS"], quote=False)

    message_to_reply.reply_text(text='Bienvenido a Propensito Game\n' + get_players_ready_message(chat_id, context), reply_markup=InlineKeyboardMarkup(
        MAIN_MENU_KEYBOARD), quote=False)


def send_bye_message(message_to_reply):
    message_to_reply.reply_text(text="See you next time! 👋", quote=False)

    message_to_reply.reply_sticker(
        sticker=STICKERS["PENNY_PUG_HEART_BROKEN"], quote=False)


def send_not_understand_message(chat_id, context):
    context.bot.send_sticker(
        chat_id=chat_id, sticker=STICKERS["PENNY_PUG_SAD"])

    context.bot.send_message(
        chat_id=chat_id, text="Sorry i can't help you now 😔", parse_mode=ParseMode.HTML)
