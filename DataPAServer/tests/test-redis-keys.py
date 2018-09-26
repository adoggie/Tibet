#coding:utf-8

import redis
from mantis.fundamental.utils.useful import Singleton


"""
https://pypi.python.org/pypi/redis
https://redis.io/topics/quickstart

https://redislabs.com/lp/python-redis/

http://www.runoob.com/redis/redis-lists.html


"""
import json
import fire

host='127.0.0.1'
port=6379
db = 0

def dump_contacts(output='contacts.txt'):
    conn = redis.StrictRedis(host, port, db=db)

    r = conn.hgetall('cta_contract_list')

    keys = sorted(r.keys(),lambda x,y:cmp(x,y))
    print keys
    f = open(output,'w')
    for k in keys:
        v = r[k]
        v = json.loads(v)
        s = v.get('name')
        # print s
        if k.count('-') or k.count('&') or len(k) >8:
            pass
        else:
            f.write('{:<20}{}\n'.format(k,s.encode('utf-8')))
    f.close()
    # print json.dumps(r)

def clear_contacts():
    conn = redis.StrictRedis(host, port, db=db)
    conn.delete('cta_contract_list')

if __name__ == '__main__':
    # dump_contacts()
    fire.Fire()