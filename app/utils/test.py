import redis

r = redis.StrictRedis(host='40.125.161.3', port=6379, db=0, password='77RuoXu123456')
'''
key = "%s_%s" % (1, '1010468795')
mHash = r.hgetall(key)
book = dict()
for key in mHash:
    book[key.decode()] = mHash[key].decode()
print(book['bookName'])

keys =  r.keys("1_book_*")
for k in keys:
    key = k.decode()
    mHash = r.hgetall(key)
    book = dict()
    for key in mHash:
        book[key.decode()] = mHash[key].decode()
    print(book)
'''

a = ['1', '2']
print('|'.join(a))

