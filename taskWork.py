from datetime import date
import os.path
import json
from settings import template_day_task
from settings import cities_dict, costs


def add_task(task_dict):
    remove_task(task_dict['user_id'])
    # date_task = datetime.strptime(task_dict['date'], "%d.%m.%Y").date()
    str_date = date.today().strftime("%Y-%m-%d")
    file_path = f'tasks/{str_date}.json'
    is_file(file_path)
    with open(file_path, "r") as file:
        day_task = json.load(file)
    # print(date_task)
    for city in task_dict['cities']:
        for cost in task_dict['costs']:
            if task_dict['user_id'] not in day_task[city][cost]:
                day_task[city][cost].append(task_dict['user_id'])
    with open(file_path, "w") as file:
        json.dump(day_task, file)


def remove_task(user_id):
    str_date = date.today().strftime("%Y-%m-%d")
    file_path = f'tasks/{str_date}.json'
    is_file(file_path)
    with open(file_path, 'r') as file:
        day_task = json.load(file)
    for city in cities_dict:
        for cost in costs:
            if user_id in day_task[city][cost]:
                day_task[city][cost].remove(user_id)
    with open(file_path, "w") as file:
        json.dump(day_task, file)


def check_task(user_id):
    str_date = date.today().strftime("%Y-%m-%d")
    file_path = f'tasks/{str_date}.json'
    is_file(file_path)
    with open(file_path, 'r') as file:
        day_task = json.load(file)
    start_of_message = 'В данный момент Вы получаете оповещения по следующим городам с выбранными диапазонами:\n'
    message = start_of_message
    for city in cities_dict:
        costs_one_city = []
        for cost in costs:
            if user_id in day_task[city][cost]:
                costs_one_city.append(cost)
        if len(costs_one_city) > 0:
            message += cities_dict[city] + ':\n     ' + '\n     '.join(smooth_costs(costs_one_city)) + '\n'
    if message == start_of_message:
        message = 'Настройки не заданы.\n' \
                  'В данный момент Вы не получаете оповещения, для их настройки нажмите /start'
    return message


def smooth_costs(costs_list: list):
    temp = costs_list.copy()
    for i in range(len(costs_list) - 1, -1, -1):
        if costs[costs_list[i]][0] == costs[costs_list[i-1]][1] + 1:
            temp[i - 1] = temp[i-1].split(' - ')[0] + ' - ' + temp[i].split(' - ')[1]
            temp.pop(i)
    return temp


def is_file(file_path):
    str_date = date.today().strftime("%Y-%m-%d")
    if not os.path.isfile(file_path):
        day_task = template_day_task.copy()
        day_task['day'] = str_date
        with open(file_path, "w") as file:
            json.dump(day_task, file)
