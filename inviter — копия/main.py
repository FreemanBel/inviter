from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


import asyncio
import logging
import datetime
import api
import config
import filters
import keyboards
import utils

bot = Bot(token=config.token, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

dp.filters_factory.bind(filters.AdminFilter)


class Form(StatesGroup):
    main = State()
    price = State()
    user_delete = State()
    url_delete = State()


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    api.Users.register_user(msg.from_user.id)
    m = [
        f'Добро пожаловать, чтобы получить доступ к VIP каналу, переведите {api.Settings.get_price()} рублей на '
        f'<a href="{config.link_to_payment}">этот аккаунт</a> с комментарием {msg.from_user.id}'
        f'\n\n'
        f'----------------------'
        f'\n\n'
        f'Чтобы получить временный доступ в VIP канал на 10 минут, отправьте команду /temporary_access'
    ]
    await msg.reply('\n'.join(m), reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['temporary_access'])
async def temporary(msg: types.Message):
    user_id = msg.from_user.id
    user = api.Users.get_user(user_id)
    now = datetime.datetime.now()
    weekday = datetime.datetime.today().weekday()
    print(api.Users.get_day(user_id))
    print(now.day)
    if api.Users.get_day(user_id) != now.day and weekday != 5 and weekday != 6:
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
                api.Users.set_kicktime_demo(user.user_id)
                print('a')
                api.Users.set_day_use(user.user_id)
                print('b')
                await asyncio.sleep(api.Settings.get_seconds())
                await bot.delete_message(sent.chat.id, sent.message_id)
                await bot.export_chat_invite_link(config.target_chat)
            except Exception as e:
                print(e)
            else:
                print(f'Ссылка на чат была успешно отправлена пользователю')
    elif weekday == (5 or 6):
        await bot.send_message(user.user_id, 'К сожалению у нас нет возможности предоставить пробный доступ в выходные дни. Попробуйте в будни.')
    else:
        await bot.send_message(user.user_id, 'Вы уже использовали свой пробный период на сегодня, дождитесь следующего дня.')


@dp.message_handler(commands=['admin'], is_admin=True)
async def admin_menu(msg: types.Message):
    await msg.reply(text='Админ-панель', reply_markup=keyboards.AdminKB.main())
    await Form.main.set()


@dp.message_handler(lambda msg: msg.text == 'Стоимость подписки', state=Form.main)
async def admin_price_start(msg: types.Message):
    await msg.reply(text='Введите стоимость подписок в рублях')
    await Form.price.set()


@dp.message_handler(lambda msg: msg.text == 'Длительность подписки', state=Form.main)
async def admin_price_start(msg: types.Message):
    await msg.reply(text='Введите длительность подписки в днях')
    await Form.user_delete.set()


@dp.message_handler(lambda msg: msg.text == 'Интервал удаления ссылки', state=Form.main)
async def admin_price_start(msg: types.Message):
    await msg.reply(text='Введите время, через которое ссылка будет деактивирована в секундах')
    await Form.url_delete.set()


@dp.message_handler(state=Form.price)
async def admin_price_enter(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        api.Settings.set_price(int(msg.text))
        await msg.reply(f'Стоимость подписки теперь: <b>{msg.text}</b> руб.')
        await Form.main.set()
    else:
        await msg.reply(text='Стоимость должна быть целым числом')


@dp.message_handler(state=Form.user_delete)
async def admin_user_delete_enter(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        api.Settings.set_days(int(msg.text))
        await msg.reply(f'Длительность подписки установлена: <b>{msg.text}</b> д.')
        await Form.main.set()
    else:
        await msg.reply(text='Количество дней должно быть целым числом')


@dp.message_handler(state=Form.url_delete)
async def admin_url_delete_enter(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        api.Settings.set_seconds(int(msg.text))
        await msg.reply(f'Время удаления ссылки установлено: <b>{msg.text}</b> сек.')
        await Form.main.set()
    else:
        await msg.reply(text='Время должно быть целым числом')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
