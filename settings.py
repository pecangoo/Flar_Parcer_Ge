from math import inf


admins_list = [491386387]

#  Словарь городов. Ключ для бэка, значение для фронта меню бота
cities_dict = {'Tbilisi': 'Тбилиси',
               'Batumi': 'Батуми',
               'Kutaisi': 'Кутаиси',
               'Poti': 'Поти',
               'Rustavi': 'Рустави'}


#  Диапазоны отбора объявлений.
split_cost_values_list = [300, 400, 500, 700, 1000]

#  Словарь продолжительности доступа. Ключ для бэка, значения для  фронта меню бота
duration_dict = {'1': '1 час - 100 руб.',
                 '2': '2 часа - 190 руб.',
                 '3': '3 часа - 270 руб.',
                 '4': '4 часа - 340 руб.',
                 'DAY': 'Весь день - 500 руб.'}

#  Количество дней, отображаемых в меню выбора дат
num_of_days = 3

#  Часовой пояс парсера
our_timezone = 'Asia/Tbilisi'

#  Время ежедневного старта парсера по часовому поясу парсера (формат: строка 'ЧЧ:ММ')
parser_start_time = '9:00'

#  Время ежедневного финиша парсера по часовому поясу парсера (формат: строка 'ЧЧ:ММ')
parser_stop_time = '23:59'

#  Продолжительность главного цикла в секундах
main_loop_time = 30

#  Максимальное количество фото в сообщении.
#  Лимит, поддерживаемый телеграммом - 10 фото, может выдерживаться при небольшом количестве публикуемых сообщений.
#  Рекомендуемое значение - не больше 5 фото, т.к. при генерации большого траффика, телеграм отправляет в таймаут.
#  У меня был таймаут 2249 сек = ~37 мин
num_of_attached_photos = 5

#  Папка хранения логов
log_dir = 'logs'

#


###########################################################
## Ниже ничего не трогаем, все настройки делаются сверху ##
###########################################################
def split_costs(values):
    costs_d = {}
    values.sort()
    costs_d['0 - ' + str(values[0]) + '$'] = [-inf, values[0]]
    for i in range(len(values) - 1):
        costs_d[str(values[i] + 1) + '$ - ' + str(values[i+1]) + '$'] = [values[i] + 1, values[i+1]]
    costs_d[str(values[-1] + 1) + '$ - max'] = [values[-1] + 1, inf]
    return costs_d


cities_checkbox = {city: 0 for city in cities_dict}

costs = split_costs(split_cost_values_list)
costs_list = [cost for cost in costs]
costs_checkbox = {cost: 0 for cost in costs}

#  Шаблон дневного задания. Зависит от cities_dict и costs_list
template_day_task = {city: {cost: [] for cost in costs} for city in cities_dict}

parser_start_hour = int(parser_start_time.split(':')[0])
parser_start_minute = int(parser_start_time.split(':')[1])
parser_stop_hour = int(parser_stop_time.split(':')[0])
parser_stop_minute = int(parser_stop_time.split(':')[1])
