from aiogram import types


class AdminKB:
    @staticmethod
    def main() -> types.ReplyKeyboardMarkup:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btns = [
            'Стоимость подписки',
            'Длительность подписки',
            'Интервал удаления ссылки'
        ]
        kb.add(*[types.KeyboardButton(i) for i in btns])
        return kb
