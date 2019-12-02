import pymongo
from os import environ

# c = 'mongodb+srv://sasha_kuprii:K04u02p20r04ii@estate-q9wuv.mongodb.net/test?retryWrites=true&w=majority'
client = pymongo.MongoClient(environ.get('CONNECTION_STRING'))
# client = pymongo.MongoClient(c)
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

