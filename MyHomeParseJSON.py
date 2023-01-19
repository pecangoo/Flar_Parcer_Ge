import requests
import SQLprocessing
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import DispatchBotMailer
from settings import *
from taskWork import is_file
import pytz
from loggingModele import logger


params = {
    # 'Keyword': 'Tbilisi',
    # 'cities': '1996871',
    # 'GID': '1996871',
    'AdTypeID': '3',
    'PrTypeID': '1',
    'Page': '1',
    # 'FCurrencyID': '1',
    # 'FPriceTo': '1000',
    'Ajax': '1',
}


def open_url_get_soup(url, session_mh):
    response = session_mh.get(url)
    if response.status_code == 200:
        # logger.info(response)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
    else:
        logger.warning('!!', response)
        soup = None
    return soup


def align_text(text):
    return ' '.join(text.split())


def info_to_log(message: list):
    message = [str(item) for item in message]
    message = ' '.join(message)
    print(message)
    with open(f'logs/MHP_log_{datetime.today().strftime("%Y-%m-%d")}.txt', 'a') as file:
        file.write(message + '\n')


def get_new_aparts_id(session_mh, first_loading):
    one_more_page = 0
    vip = 20
    page = 0
    id_list = []
    while one_more_page != 1:
        if vip == 0:
            one_more_page += 1
        page += 1
        params['Page'] = str(page)
        try:
            response = session_mh.get('https://www.myhome.ge/ru/s/', params=params)
        except Exception as ex:
            logger.error('Session connection FAILED: ' + str(ex))
        if response.status_code == 200:
            # print(response)
            data = response.json()
            if data['StatusCode'] == 1:
                for item in data['Data']['Prs']:
                    if item['vip'] == '0':
                        vip = 0
                    if SQLprocessing.is_id_not_in_db(item['product_id'], 'myhome'):
                        if not first_loading:
                            if item['price']:
                                price = item['price'].split('.')[0]
                            else:
                                price = ''
                            city = ''
                            for city_t in cities_dict:
                                if city_t.lower() in item['pathway_json'].lower() or \
                                        city_t.lower() in item['seo_title_json'].lower():
                                    city = city_t
                                    break
                            apart_dict = {'id': item['product_id'],
                                          'time': item['order_date'],
                                          'cost': price + '$' if item['currency_id'] == '1' else price + 'GEL',
                                          'city': city
                                          }
                            id_list.append(apart_dict)
                            # print()
                            # print('ID объявления: ', item['product_id'])
                            # print('Опубликовано: ', item['order_date'])
                            # print('Цена: ', item['price'])
                            # print('Валюта: ', '$' if item['currency_id'] == '1' else 'GEL')
                            # print('Тип VIP: ', item['vip'])
                        else:
                            SQLprocessing.insert_id(item['product_id'], 'myhome')
            else:
                logger.warning('In JSON loading status code not 1:', data['StatusCode'], data['StatusMessage'])
        else:
            logger.warning('Page with JSON aparts list response status not <200>')
            break
    logger.debug(f"JSON pages: {page}")
    id_list = sorted(id_list, key=lambda x: x['time'])
    return id_list


def usd_to_cost(usd):
    cost = None
    try:
        usd = int(usd.replace(',', ''))
        for key, val in costs.items():
            if val[0] <= usd <= val[1]:
                cost = key
                break
    except Exception as ex:
        logger.warning('Bad USD to cost:', ex)
    return cost


def get_aparts_data_mh(new_aparts_list: list, session_mh):
    for apart in new_aparts_list:
        images = []
        sleep_time = 2
        sleep(sleep_time)
        soup = open_url_get_soup('https://www.myhome.ge/ru/pr/' + apart['id'], session_mh)
        if soup:
            temp = soup.find('span', class_='d-block convertable')
            try:
                gel = temp.get('data-price-gel')
            except Exception as ex:
                logger.warning('!! Bad gel price\n', ex)
                gel = '***'
            try:
                usd = temp.get('data-price-usd')
            except Exception as ex:
                logger.warning('!! Bad usd price\n', ex)
                usd = '***'
            try:
                temp = soup.find('div', class_='main-features row no-gutters').findAll('span', class_='d-block')
                area = temp[0].text.strip()
                rooms = temp[1].text.strip()
                bedrooms = temp[2].text.strip() + ' ' + temp[3].text.strip()
                flour = temp[4].text.strip() + ' ' + temp[5].text.strip()
            except Exception as ex:
                logger.warning('!! Bad main-features\n', ex)
                area = '**'
                rooms = '**'
                bedrooms = '**'
                flour = '**'
            try:
                looks = soup.find('div', class_='d-flex align-items-center views').text.strip()
            except Exception as ex:
                logger.warning('!! Bad looks\n', ex)
                looks = '**'
            link = 'https://www.myhome.ge/ru/pr/' + apart['id']
            try:
                all_host_ads = soup.find('a', class_='see-all-statements').text.split()[-1]
                all_host_ads = all_host_ads[1:-1]
            except Exception as ex:
                logger.warning('!! Bad all_host_ads\n', ex)
                all_host_ads = '**'
            images_soup = soup.find('div', class_='swiper-wrapper').findAll('img')
            if images_soup:
                images_soup = images_soup[:num_of_attached_photos]
                for image in images_soup:
                    image = image.get('data-src')
                    if 'nophoto' in image:
                        images.append('https://fogo.com.ru/api/v1/files/placeholder')
                        break
                    else:
                        images.append(image)
                # print(images)
            description = soup.find('p', class_='pr-comment translated')
            if description:
                description = description.text.strip()
                description = align_text(description).replace('&quot;', '')
            else:
                description = '** нет описания **'
            name = soup.find('h1', class_='mb-0')
            if name:
                name = name.text.strip()
                name = align_text(name)
            else:
                name = '** нет названия **'
            address = soup.find('span', class_='address')
            if address:
                address = address.text.strip()
                address = align_text(address)
            else:
                address = '** нет адреса **'

            message = 'Опубликовано: ' + apart['time'] + '\n' + \
                      'Просмотры: ' + looks + '\n' + \
                      'Объявлений у автора: ' + all_host_ads + '\n' + \
                      usd + '$ / ' + gel + 'GEL' + '\n' + \
                      name + '\n' + \
                      address + '\n' + \
                      area + '  ' + rooms + '  ' + bedrooms + '  ' + flour + '\n' + \
                      description + '\n'
            if len(message) + len(link) + 7 > 1024:
                message = message[:1024 - len(link) - 7] + ' ...'
            message += link
            logger.info(apart['city'] + ' ' + usd + '$  ' + link)
            images = DispatchBotMailer.unite_images(images, message)
            message_dict = {'city': apart['city'],
                            'cost': usd_to_cost(usd),
                            'images': images,
                            'message': message
                            }
            try:
                SQLprocessing.insert_id(apart['id'], 'myhome')
            except Exception as ex:
                logger.error(f'!!!! SQL insert problem. Apart id {apart["id"]} not in database.\n', ex)
            DispatchBotMailer.dispatch_message(message_dict)
        else:
            logger.warning('!! Bad aparts soup')


def today_first_load():
    str_datetime_now = datetime.now(pytz.timezone(our_timezone)).strftime("%Y-%m-%d")
    file_path = f'tasks/{str_datetime_now}.json'
    is_file(file_path)


def main():
    logger.info(f'\n' + '*' * 30 + f'\n### {datetime.now(pytz.timezone(our_timezone)).strftime("%H:%M:%S")} '
                                   f'- SERVICE MyHomeParser RUN\n')
    SQLprocessing.clear_table('myhome')
    session_mh = requests.Session()
    session_mh.headers.update({
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 '
                      'Safari/537.36'})
    num_of_loadings = 0
    while True:
        start_parser_time = datetime.now(pytz.timezone(our_timezone)) \
            .replace(hour=parser_start_hour, minute=parser_start_minute, second=0, microsecond=0)
        stop_parser_time = datetime.now(pytz.timezone(our_timezone)) \
            .replace(hour=parser_stop_hour, minute=parser_stop_minute, second=0, microsecond=0)
        start_time = datetime.now(pytz.timezone(our_timezone))
        if start_parser_time.timestamp() < start_time.timestamp() < stop_parser_time.timestamp():
            logger.info(f'# {datetime.now(pytz.timezone(our_timezone)).strftime("%H:%M:%S")} - main loop start')
            num_of_loadings += 1
            first_loading = True if num_of_loadings == 1 else False
            if first_loading:
                today_first_load()
            new_aparts_id_list = get_new_aparts_id(session_mh, first_loading)
            if len(new_aparts_id_list):
                logger.info('New ads: ' + str(len(new_aparts_id_list)))
            get_aparts_data_mh(new_aparts_id_list, session_mh)
        else:
            logger.info(f'# {datetime.now(pytz.timezone(our_timezone)).strftime("%H:%M:%S")} '
                        f'- Parser sleeps until {parser_start_time}')
            if num_of_loadings > 0:
                logger.info(f'$$$$$$$$$$$$$$ {datetime.now(pytz.timezone(our_timezone)).strftime("%H:%M:%S")} '
                            f'- Количество main loop`ов: {num_of_loadings}')
            num_of_loadings = 0
        now_time = datetime.now(pytz.timezone(our_timezone))
        if now_time - start_time < timedelta(seconds=main_loop_time):
            sleep(main_loop_time - (now_time - start_time).seconds)


if __name__ == '__main__':
    main()
