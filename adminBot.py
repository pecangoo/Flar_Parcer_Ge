from datetime import datetime
import os.path
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import IDFilter, Text
from aiogram.utils import executor
from subprocess import call as sub_call
import pytz
from settings import our_timezone, admins_list


logging.basicConfig(level=logging.INFO)
API_TOKEN = '5648149900:AAGM2gwz46RxmEnEVxkvSogTdvNamJvImZU'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

message_id = 0

serv_list = {'MyHomeParser': 'MHP', 'OrderMenuBot': 'OMB'}
serv_menu_list = {'FROM CONSOLE': '_console.sh',
                  'START/RESTART': '_start.sh',
                  'STOP': '_stop.sh'}


class ServState(StatesGroup):
    main = State()
    menu = State()


@dp.message_handler(IDFilter(user_id=admins_list), commands='servers')
async def cmd_servers(message: types.Message):
    await ServState.main.set()
    serv_kb = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(item, callback_data=item) for item in serv_list]
    for button in buttons:
        serv_kb.add(button)
    mes = await message.answer("Выберите сервис:", reply_markup=serv_kb)
    global message_id
    message_id = mes.message_id


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(lambda c: c.data in serv_list, IDFilter(user_id=admins_list), state=ServState.main)
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['serv'] = callback_query.data
    await ServState.next()
    serv_menu_kb = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(item, callback_data=item) for item in serv_menu_list]
    for button in buttons:
        serv_menu_kb.add(button)
    global message_id
    await bot.edit_message_text(f'Выбран сервис: {callback_query.data}\n'
                                f'\n'
                                f'Выберите действие:',
                                callback_query.from_user.id, message_id, reply_markup=serv_menu_kb)


@dp.callback_query_handler(lambda c: c.data in list(serv_menu_list)[1:], IDFilter(user_id=admins_list),
                           state=ServState.menu)
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        path = f'./scripts/{serv_list[data["serv"]]}{serv_menu_list[callback_query.data]}'
        print(path)
        print(sub_call(['sh', path]))
    await state.finish()
    global message_id
    await bot.edit_message_text(f'Сервис: {data["serv"]}\n'
                                f'Действие: {callback_query.data}',
                                callback_query.from_user.id, message_id, reply_markup=types.InlineKeyboardMarkup(0))


@dp.callback_query_handler(lambda c: c.data == list(serv_menu_list)[0], IDFilter(user_id=admins_list),
                           state=ServState.menu)
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        file_path = f'logs/{serv_list[data["serv"]]}_log_' \
                    f'{datetime.now(pytz.timezone(our_timezone)).strftime("%Y-%m-%d")}.txt'
        print(file_path)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                text = file.read()[-1000:] + '\n' + '_'*30 + \
                       f"\n## {datetime.now(pytz.timezone(our_timezone)).strftime('%H:%M:%S')} " \
                       f"{file_path.split('/')[-1]}"
        else:
            text = '!!! Файл с логом не найден'
    await state.finish()
    global message_id
    await bot.edit_message_text(text,
                                callback_query.from_user.id, message_id, reply_markup=types.InlineKeyboardMarkup(0))





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
