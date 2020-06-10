import asyncio

import api
import config
from aiogram import Bot

bot = Bot(token=config.token)


async def main():
    users = api.Users.get_users_to_kick()
    m = [
        'Вы были исключены из нашего канала. Нажмите /start, чтобы получить реквизиты для оплаты.'
    ]
    if users:
        for user in users:
            try:
                await bot.kick_chat_member(config.target_chat, user.user_id)
                await bot.unban_chat_member(config.target_chat, user.user_id)
            except Exception as e:
                print(e)
            else:
                pass
                # try:
                #     await bot.send_message(user.user_id, '\n'.join(m))
                # except Exception as e:
                #     print(e)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
