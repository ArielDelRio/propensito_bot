
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton


DEVELOPER_CHAT_ID = 999273250


STICKERS = {
    "PENNY_PUG_SAD": 'CAACAgIAAxkBAAECUm1gpqI8kLliVJDBKnXGNBULtWJm5AACIwADnP4yMGLSFbgqnabRHwQ',
    "PENNY_PUG_ANXIOUS": 'CAACAgIAAxkBAAECUn1gpq6x1tbqKFEd5Ts5FctSDEhz7gACIQADnP4yMOQGvNtSSJXGHwQ',
    "PENNY_PUG_HEART_BROKEN": "CAACAgIAAxkBAAECUpZgprh8TrZloaChwZn6DTMc99ooeAACHAADnP4yMJbopn7Nh5taHwQ",
    "PENNY_PUG_THUMBS_UP": "CAACAgIAAxkBAAECUqZgptE6hiQaUZ7jnM3fjikTitWdLAACCgADnP4yMFsQVnkk-4rwHwQ"
}


QUESTIONS = [
    {"q": "¿Quién es más probable que mate a alguien accidentalmente?"},
    {"q": "¿Quién es más probable que no le gusten mucho las películas?"},
    {"q": "¿Quién es más probable que se convierta en un famoso actor/actriz?"},
    {"q": "¿Quién es más probable que huya para no unirse al circo?"},
    {"q": "¿Quién es más probable que salte de un tren en movimiento?"},
    {"q": "¿Quién es más probable que tenga paranoias?"},
    {"q": "¿Quién es más probable que sea el más atlético?"},
    {"q": "¿Quién es más probable que vea películas románicas?"},
    {"q": "¿Quién es más probable que se convierta en un stripper?"},
    {"q": "¿Quién es más probable que sea detenido por acosar a un oficial de policía?"}
]


# Stages
PREPARE_GAME, IN_GAME = range(2)

# Callback data
JOIN, START, EXIT = range(3)


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
