import pymongo
from os import environ


c = 'mongodb+srv://smartdataestate:Estate4628134@estate-dqksq.gcp.mongodb.net/test?retryWrites=true&w=majority'
# client = pymongo.MongoClient(environ.get('CONNECTION_STRING'))
client = pymongo.MongoClient(c)
cursor = client.list_databases()
for db in cursor:
    print(db)
db = client.Estate
print("db connected ok")



def get_exist_links(country, resource):
    exist_links = set()
    exist_data = db[country].find({'resource': resource})
    for x in exist_data:
        exist_links.add(x['link'])

    return list(exist_links)


def save(data, country):
    db[country].insert_many(data)

# try:
#     # Подключиться к существующей базе данных
#     connection = psycopg2.connect(user="postgres",
#                                 # пароль, который указали при установке PostgreSQL
#                                 password="1111",
#                                 host="127.0.0.1",
#                                 port="5432",
#                                 database="postgres_db")

#     # Создайте курсор для выполнения операций с базой данных
#     cursor = connection.cursor()
#     # SQL-запрос для создания новой таблицы
#     create_table_query = '''CREATE TABLE mobile
#                         (ID INT PRIMARY KEY     NOT NULL,
#                         MODEL           TEXT    NOT NULL,
#                         PRICE         REAL); '''
#     # Выполнение команды: это создает новую таблицу
#     cursor.execute(create_table_query)
#     connection.commit()
#     print("Таблица успешно создана в PostgreSQL")

# except (Exception, Error) as error:
#     print("Ошибка при работе с PostgreSQL", error)
# finally:
#     if connection:
#         cursor.close()
#         connection.close()
#         print("Соединение с PostgreSQL закрыто")


if __name__ == '__main__':
    pass
    


