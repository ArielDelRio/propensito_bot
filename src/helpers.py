from random import randint

from src.constants import QUESTIONS


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

            # Pass the question index
            "question_index": question_index
            # "question": question,
        }
    }

    context.bot_data.update(payload)


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