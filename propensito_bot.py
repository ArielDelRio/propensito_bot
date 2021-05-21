import os
import logging
from telegram.ext import Updater, CommandHandler,  CallbackQueryHandler, PollHandler, ConversationHandler, PicklePersistence
from src.constants import *
from src.commands import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def main():
    persistence = PicklePersistence(filename='propensito_bot')

    updater = Updater(token=os.environ.get('TOKEN'),
                      persistence=persistence, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help))

    conversation_handler = ConversationHandler(
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
                CallbackQueryHandler(
                    get_current_poll, pattern='^' + str(CURRENT_POLL) + '$'),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(exit, pattern='^' + str(EXIT) + '$'),
            CommandHandler("cls", clear_all),
        ],
        per_user=False,
        per_message=False,
        per_chat=True,
        name="propensito_bot",
        persistent=True
    )

    dispatcher.add_error_handler(error_handler)

    dispatcher.add_handler(PollHandler(receive_poll_answer))

    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
