import time
from datetime import date
import json
from telebot import types, TeleBot
import re
from loggingModele import logger
from settings import *

MenuBot = TeleBot('5721296479:AAHG-eLXCVN6rs2C4XC06IeI3bTPi5zE4T0')
AnotherBot = TeleBot('5449243136:AAGq1SXTaS02aX-3fp3rEOwUzQyVU1IJ_XM')


def send_message(user_id_list, message, image_group):
    try:
        MenuBot.send_media_group(user_id_list, image_group)
        logger.info('Message has been sent')
    except Exception as ex:
        ex = str(ex)
        logger.warning('!!!!!! Sending message error', ex)
        if 'Too Many Requests' in ex:
            time_to_sleep = int(ex.split(' ')[-1])
            logger.error(ex)
            logger.error('Telegram said to sleep' + str(time_to_sleep) + 'sec')
            time.sleep(time_to_sleep)
        elif 'Wrong type of the web page content' in ex:
            num_of_bad_photo = int(re.findall(r'#\d+ ', ex)[0].strip().replace('#', ''))
            logger.error(f"Bad pictures #{num_of_bad_photo}, telegram doesn't want it")
            logger.info('Try to delete bad photo and receive again')
            image_group.pop(num_of_bad_photo - 1)
            send_message(user_id_list, message, image_group)
            logger.info('Message without bad photo received')
        else:
            for user_id in user_id_list:
                MenuBot.send_message(user_id, message, disable_web_page_preview=True)
                time.sleep(1/30)


def dispatch_message(message):
    if message['city'] and message['cost']:
        str_date = date.today().strftime("%Y-%m-%d")
        with open(f'tasks/{str_date}.json', 'r') as file:
            day_task = json.load(file)
        id_list_task = day_task[message['city']][message['cost']]
        if len(id_list_task) > 0:
            send_message(id_list_task, message['message'], message['images'])
    else:
        logger.info(f"!!!  Message with bad city or bad cost: message['city']: {message['city']} message['cost']: "
                    f"{message['cost']}")
        AnotherBot.send_media_group(admins_list, message['images'])


def unite_images(urls_list, mess):
    media_group = []
    count = 0
    for url_image in urls_list:
        if not count:
            media_group.append(types.InputMediaPhoto(media=url_image, caption=mess))
        else:
            media_group.append(types.InputMediaPhoto(media=url_image))
        count += 1
    if not len(media_group):
        media_group = None
    return media_group
