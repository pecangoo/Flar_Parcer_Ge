import pickle
import json


access_now_path = 'users/access_now.usr'


def add_user_access(user_id):
    with open(access_now_path, 'rb') as f:
        data = pickle.load(f)
        data.append(user_id)
    with open(access_now_path, 'wb') as f:
        pickle.dump(data, f)


def del_user_access(user_id):
    with open(access_now_path, 'rb') as f:
        data = pickle.load(f)
    try:
        data.remove(user_id)
    except Exception as ex:
        print('!!! В списке доступа нет запрашиваемого на удаление ID', ex)
    with open(access_now_path, 'wb') as f:
        pickle.dump(data, f)


def get_users_access():
    with open(access_now_path, 'rb') as f:
        return pickle.load(f)


def make_readable_access_list():
    with open(access_now_path, 'rb') as f:
        data = pickle.load(f)
    with open(access_now_path + '.json', "w") as file:
        json.dump(data, file)


def print_access_list():
    with open(access_now_path, 'rb') as f:
        print(pickle.load(f))

print_access_list()
