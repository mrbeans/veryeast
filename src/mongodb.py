import pymongo

class MyMongoDB(object):
    MONGODB_CONFIG = {
        'host': '127.0.0.1',
        'port': 27017,
        'db_veryeast':'veryeast',
        'table_base_info': 'veryeast',
        'table_preview': 'veryeast',
        'username': None,
        'password': None
    }

    def __init__(self):
        try:
            self.client=pymongo.MongoClient(MyMongoDB.MONGODB_CONFIG['host'],MyMongoDB.MONGODB_CONFIG['port'])
            self.connected = True
        except Exception:
            print(traceback.format_exc())
            sys.exit(1)
    
    def getDB(self,dbname):
        if(MyMongoDB.MONGODB_CONFIG[dbname]==None):
            raise Exception("the special database ")
        return self.client[MyMongoDB.MONGODB_CONFIG[dbname]]
    
    def getCollection(self,dbname,collectionName):
        if(MyMongoDB.MONGODB_CONFIG[dbname]==None):
            raise Exception("the special database ")
        return self.client[MyMongoDB.MONGODB_CONFIG[dbname]]['collectionName']
