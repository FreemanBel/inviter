import asyncio
import logging

from aiogram import Bot, types

import api
import config
import utils
from aioqiwi.wallet import QiwiUpdate, Wallet

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=config.token, parse_mode='HTML')
wallet = Wallet(api_hash=config.api_hash)
wallet.as_model = False
server_ip = utils.get_ip()
server_port = 7494
server_path = '/webhooks/qiwi/'
hook_url = f'http://{server_ip}:{server_port}{server_path}'


@wallet.on_update(incoming=True)
async def got_payment(event: QiwiUpdate):
    currency = event.Payment.Total.currency
    if currency != 643 and currency in config.allowed_currencies:
        in_rub = await utils.convert(event.Payment.Total.amount, config.allowed_currencies[currency])
    else:
        in_rub = event.Payment.Total.amount
    if event.Payment.comment.isdigit():
        user_id = int(event.Payment.comment)
        user = api.Users.get_user(user_id)
        if user:
            if in_rub >= api.Settings.get_price():
                if user:
                    try:
                        link = await bot.export_chat_invite_link(config.target_chat)
                        userdata = await bot.get_chat_member(config.target_chat, user.user_id)
                        if userdata.status in [types.ChatMemberStatus.KICKED, types.ChatMemberStatus.LEFT]:
                            await bot.unban_chat_member(config.target_chat, user.user_id)
                    except Exception as e:
                        print(e)
                    else:
                        try:
                            m = [
                                f'Ссылка на канал: {link}',
                                f'Ссылка перестанет работать через {api.Settings.get_seconds()} секунд'
                            ]
                            sent = await bot.send_message(user.user_id, '\n'.join(m))
                            api.Users.set_kicktime(user.user_id)
                            await asyncio.sleep(api.Settings.get_seconds())
                            await bot.delete_message(sent.chat.id, sent.message_id)
                            await bot.export_chat_invite_link(config.target_chat)
                        except Exception as e:
                            print(e)
                        else:
                            print(f'Ссылка на чат была успешно отправлена пользователю')
            else:
                m = [
                    f'Сумма платежа в {in_rub} RUB слишком мала. Платеж должен превышать {api.Settings.get_price()} RUB,'
                    ' чтобы вам была выдана ссылка'
                ]
                await bot.send_message(user.user_id, '\n'.join(m))
                print(f'Слишком маленькая сумма платежа: [{in_rub} RUB] от [{user_id}]')
        else:
            print(f'Пользователь не найден в БД: [{user_id}]')
    else:
        print(f'Коментарий не является ID пользователя: [{event.Payment.comment}]')


async def on_startup():
    hook = await wallet.hooks()
    if 'hookId' in hook:
        await wallet.delete_hooks(hook['hookId'])
    await wallet.hooks(url=hook_url, transactions_type=0)


if __name__ == '__main__':
    wallet.idle(on_startup=on_startup(), host='0.0.0.0', path=server_path, port=server_port)
