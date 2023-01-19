import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             port=3307,
                             password='1234',
                             db='georgia_apartments',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def insert_id(apart_id, table):
    query = f'INSERT INTO {table} (id) VALUE ({apart_id})'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
    except Exception as ex:
        print('!!!! Error insert ID to SQL', ex)
        print(str(ex.__traceback__))


def is_id_not_in_db(apart_id, table):
    query = 'SELECT * FROM ' + table + ' where id = ' + apart_id
    with connection.cursor() as cursor:
        cursor.execute(query)
        zn = cursor.fetchone()
        connection.commit()
    if zn:
        return 0
    else:
        return 1


def clear_table(table):
    query = f'TRUNCATE {table}'
    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()
