import pymongo
from os import environ


client = pymongo.MongoClient(environ.get('CONNECTION_STRING'))
db = client.Estate


def get_exist_links(country, resource):
    exist_links = set()
    exist_data = db[country].find({'resource': resource})
    for x in exist_data:
        exist_links.add(x['link'])

    return list(exist_links)


def save(data, country):
    db[country].insert_many(data)




if __name__ == '__main__':
    pass

