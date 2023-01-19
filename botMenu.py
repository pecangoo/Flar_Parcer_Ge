from loggingModele import *
from datetime import date, timedelta
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from settings import *
from UsersAccessWork import *
from taskWork import add_task, remove_task, check_task, smooth_costs


"""
### Команды чата
**********************************
start - Запустить рассылку / изменить настройки
check - Показать текущие настройки
stop - Остановить рассылку
add - Получить доступ к сервису
remove - Отключить доступ к сервису
cancel - Сбросить ввод
**********************************
"""

logging.basicConfig(level=logging.INFO)


API_TOKEN = '5721296479:AAHG-eLXCVN6rs2C4XC06IeI3bTPi5zE4T0'

bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Settings(StatesGroup):
    city = State()
    cost = State()
    finish = State()


class Payment(StatesGroup):
    duration = State()
    date = State()
    confirm = State()


def check_all_off(check_dict):
    return all([True if not val else False for val in check_dict.values()])


def make_all_off(dict_off):
    return {key: 0 for key in dict_off}


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message, state: FSMContext):
    message_json = json.loads(message.as_json())
    print(str(type(message_json)) + str(message_json))
    logger.info('New message /start from: ' + str(message_json['from']))
    if message.from_user.id in get_users_access():
        await Settings.city.set()
        await message.answer("Здесь вы можете настроить рассылку публикующихся на myhome.ge новых "
                             "объявлений")
        city_kb = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(cities_dict[item], callback_data=item) for item in cities_dict]
        for button in buttons:
            city_kb.add(button)
        mes = await message.answer("Выберите город поиска (можно несколько) и подтвердите выбор:", reply_markup=city_kb)
        async with state.proxy() as data:
            data['cities_checkbox'] = cities_checkbox.copy()
            data['costs_checkbox'] = costs_checkbox.copy()
            data['dates_dict'] = {str(i): (date.today() + timedelta(days=i)).strftime('%d.%m.%Y')
                                  for i in range(num_of_days)}
            data['dates_checkbox'] = {str(i): 0 for i in range(num_of_days)}
            data['user_id'] = message.from_user.id
            data['message_id'] = mes.message_id
    else:
        await message.answer("Вы не оформили подписку, и не имеете доступа к сервису")


@dp.message_handler(commands='stop')
async def cmd_start(message: types.Message):
    remove_task(message.from_user.id)
    await message.reply('Как скажете. Сообщения перестанут приходить в течение минуты')


@dp.message_handler(commands='check')
async def cmd_start(message: types.Message):
    await message.reply(check_task(message.from_user.id))


@dp.message_handler(commands='add')
async def cmd_start(message: types.Message):
    users_list = get_users_access()
    logger.info('Users list: ' + str(users_list))
    if message.from_user.id not in users_list:
        add_user_access(message.from_user.id)
        await message.reply('Вы получили доступ к сервису')
    else:
        await message.reply('Вы уже имеете доступ к сервису')


@dp.message_handler(commands='remove')
async def cmd_start(message: types.Message):
    users_list = get_users_access()
    if message.from_user.id in users_list:
        del_user_access(message.from_user.id)
        await message.reply('Вы отменили доступ к сервису')
    else:
        await message.reply('Вы итак не имеете доступа к сервису')


# You can use state '*' if you need to handle all states
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


@dp.callback_query_handler(lambda c: c.data in cities_dict, state=Settings.city)
async def process_cities_checkbox(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['cities_checkbox'][callback_query.data] = (data['cities_checkbox'][callback_query.data] + 1) % 2
    cities_kb = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(cities_dict[key] if data['cities_checkbox'][key] == 0
                                          else cities_dict[key] + '  ✅',
                                          callback_data=key) for key in data['cities_checkbox']]
    if not check_all_off(data['cities_checkbox']):
        buttons.append(types.InlineKeyboardButton('Подтвердить выбор', callback_data='OK'))
    for button in buttons:
        cities_kb.add(button)
    await bot.edit_message_text("Выберите город поиска (можно несколько) и подтвердите выбор:",
                                callback_query.from_user.id, data['message_id'], reply_markup=cities_kb)


@dp.callback_query_handler(lambda c: c.data == 'OK', state=Settings.city)
async def process_city_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        if check_all_off(data['cities_checkbox']):
            cities_kb = types.InlineKeyboardMarkup()
            buttons = [
                types.InlineKeyboardButton(cities_dict[key] if data['cities_checkbox'][key] == 0
                                           else cities_dict[key] + '  ✅',
                                           callback_data=key) for key in data['cities_checkbox']]
            for button in buttons:
                cities_kb.add(button)
            await bot.edit_message_text("Не выбрано ни одного города.\n\nВыберите город поиска и подтвердите выбор:",
                                        callback_query.from_user.id, data['message_id'], reply_markup=cities_kb)
        else:
            checked_cities = []
            for city in data['cities_checkbox']:
                if data['cities_checkbox'][city] == 1:
                    checked_cities.append(city)
            logger.info('User-selected cities: ' + str(checked_cities))
            data['cities'] = checked_cities
            await Settings.next()
            costs_kb = types.InlineKeyboardMarkup()
            buttons = [types.InlineKeyboardButton(cost, callback_data=cost) for cost in costs_list]
            for button in buttons:
                costs_kb.add(button)
            await bot.edit_message_text(f'Выбран поиск в город{"ах" if len(checked_cities) > 1 else "е"}: \n'
                                        f'{", ".join([cities_dict[key] for key in checked_cities])}\n'
                                        f'\n'
                                        f'Выберите диапазон(ы) поиска арендной платы, подтвердите выбор:',
                                        callback_query.from_user.id, data['message_id'], reply_markup=costs_kb)


@dp.callback_query_handler(lambda c: c.data in costs_list, state=Settings.cost)
async def process_cost_checkbox(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['costs_checkbox'][callback_query.data] = (data['costs_checkbox'][callback_query.data] + 1) % 2
    cost_kb = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(item if data['costs_checkbox'][item] == 0 else item + '  ✅',
                                   callback_data=item) for item in costs_list]
    if not check_all_off(data['costs_checkbox']):
        buttons.append(types.InlineKeyboardButton('Подтвердить выбор', callback_data='OK'))
    for button in buttons:
        cost_kb.add(button)
    await bot.edit_message_text("Выберите диапазон(ы) поиска арендной платы, подтвердите выбор:",
                                callback_query.from_user.id, data['message_id'], reply_markup=cost_kb)


@dp.callback_query_handler(lambda c: c.data == 'OK', state=Settings.cost)
async def process_cost_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        if check_all_off(data['costs_checkbox']):
            cost_kb = types.InlineKeyboardMarkup()
            buttons = [
                types.InlineKeyboardButton(item if data['costs_checkbox'][item] == 0 else item + '  ✅',
                                           callback_data=item) for item in data['costs_checkbox']]
            for button in buttons:
                cost_kb.add(button)
            await bot.edit_message_text("Не выбрано ни одного диапазона.\n"
                                        "\n"
                                        "Выберите диапазон(ы) поиска арендной платы, подтвердите выбор:",
                                        callback_query.from_user.id, data['message_id'], reply_markup=cost_kb)
        else:
            checked_costs = []
            for cost in data['costs_checkbox']:
                if data['costs_checkbox'][cost] == 1:
                    checked_costs.append(cost)
            logger.info('User-selected costs: ' + str(checked_costs))
            data['costs'] = checked_costs
            await Settings.finish.set()
            accept_kb = types.InlineKeyboardMarkup()
            accept_kb.add(types.InlineKeyboardButton('ДА', callback_data='YES'))
            accept_kb.add(types.InlineKeyboardButton('НЕТ', callback_data='NO'))
            await bot.edit_message_text(
                md.text(
                    md.text('Вы выбрали:'),
                    md.text('Города поиска: ', md.hbold(', '.join([cities_dict[key] for key in data['cities']]))),
                    md.text('Диапазоны арендной платы: ', md.hbold(', '.join(smooth_costs(data['costs'])))),
                    md.text(),
                    md.text('Всё верно?'),
                    sep='\n',
                ),
                callback_query.from_user.id,
                data['message_id'],
                parse_mode=types.ParseMode.HTML,
                reply_markup=accept_kb
            )
            del data['cities_checkbox']
            del data['costs_checkbox']
            del data['dates_checkbox']
            del data['dates_dict']


@dp.callback_query_handler(lambda c: c.data == 'NO', state=Settings.finish)
async def process_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Попробуйте задать новые настройки, нажмите /start.')
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'YES', state=Settings.finish)
async def process_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        logger.info('Settings selected in menu: ' + str(data.as_dict()))
        add_task(data.as_dict())
        await bot.edit_message_text(
            md.text(
                md.text('Вы выбрали:'),
                md.text('Города поиска: ', md.hbold(', '.join([cities_dict[key] for key in data['cities']]))),
                md.text('Диапазоны арендной платы: ', md.hbold(', '.join(smooth_costs(data['costs'])))),
                md.text(),
                md.text('Настройки применены, оповещение уже работает. Сообщения будут приходить по мере их '
                        'публикации на ресурсах. Спасибо!'),
                md.text(),
                md.text('* Вы всегда можете проверить текущие настройки, нажав /check'),
                sep='\n',
            ),
            callback_query.from_user.id,
            data['message_id'],
            parse_mode=types.ParseMode.HTML)
    await state.finish()


@dp.message_handler(state='*')
async def cmd_start(message: types.Message):
    await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp)  # , skip_updates=True)
