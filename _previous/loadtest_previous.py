# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 21:40:35 2016

@author: sdowning
"""

import requests, json, sys, math
#import urllib3 as ul
import arrow as ar
import pandas as pd
#from bs4 import BeautifulSoup
from time import time, sleep
from tornado import ioloop, httpclient
#
from threading import Thread
from multiprocessing import Queue
#from funkload.FunkLoadTestCase import FunkLoadTestCase 


#------------------------------------------------

class ChocolyLoadTest(object):
    def __init__(self, url, calls=None):
        self.calls = calls if calls is not None else 1000
        self.concurrent = math.floor(self.calls/4)
        self.q = Queue(self.concurrent)
        self.url = url
        self.urls = [url]*self.calls
        self.li = []

    def getStatus(self, url):
        try:
            response = requests.get(url=url)
            return response.status_code, url
        except Exception as e:
            print(e)
            return "error", url

    def store(self, status, url):
        self.li.extend([dict(status=status,time=ar.now())])

    def doWork(self):
        while True:
            url = self.q.get()
            status, url = self.getStatus(url)
            self.store(status, url)
            #q.empty()
    
    def hmsS(self, ar):
        return ar.format('hh:mm:ss.SSSSS')
    
    def plotRate(self):
        df = pd.DataFrame(self.li)
        df['pd'] = df.time.apply(lambda x: x.format('hh:mm:ss'))
        rate = df.groupby('pd').count()
        rate.time.plot(kind='bar',figsize=(10,5))
        self.df = df
    
    def main(self):
        for i in range(self.concurrent):
            self.t = Thread(target=self.doWork)
            self.t.daemon = True
            self.t.start()
        try:
            for url in self.urls:
                self.q.put(url.strip())
            #q.join_thread()
        except KeyboardInterrupt:
            sys.exit(1)



url = 'http://devchocoly-dev1.7qha9u7kea.ap-northeast-1.elasticbeanstalk.com/'

test = ChocolyLoadTest(url, calls=1000)

test.main()

df = pd.DataFrame(li)
plotRate(li)

#------------------------------------------------


def getUrl(url, i=None, *args, **kwargs):
    response = requests.get(url=url)
    return 1 if response.ok else 0

def getCallBatch(url, calls):
    return [ {'time':ar.now(),'resp':getUrl(url)} for i in range(calls) ]

def loadTest(url, calls, runs, nap):
    x = []
    t0 = time()
    for run in range(runs):
        x.extend(getCallBatch(url, calls))
        print('finished run {r: >3d} elapsed seconds: {t: >7.2f}'.format(r=run, t=time()-t0) )
        sleep(nap)
    return pd.DataFrame(x)

def handleRequest(response):
    global x
    x.extend([response.ok])
    global i
    i -= 1
    if i == 0:
        ioloop.IOLoop.instance().stop()


def doWork():
    while True:
        url = q.get()
        status, url = getStatus(url)
        store(status, url)
        #q.empty()

def getStatus(url):
    try:
        response = requests.get(url=url)
        return response.status_code, url
    except Exception as e:
        print(e)
        return "error", url

def store(status, url):
    li.extend([dict(status=status,time=ar.now())])

def hmsS(ar):
    return ar.format('hh:mm:ss.SSSSS')

def plotRate(df):
    df['pd'] = df.time.apply(lambda x: x.format('hh:mm:ss'))
    rate = df.groupby('pd').count()
    rate.time.plot(kind='bar',figsize=(10,5))

def main(urls, q):
    for i in range(concurrent):
        t = Thread(target=doWork)
        t.daemon = True
        t.start()
    try:
        for url in urls:
            q.put(url.strip())
        #q.join_thread()
    except KeyboardInterrupt:
        sys.exit(1)

calls = 900
concurrent = 300
q = Queue(concurrent * 2)
url = 'http://devchocoly-dev1.7qha9u7kea.ap-northeast-1.elasticbeanstalk.com/'
urls = [url]*calls

## RUN MAIN
li = []
main(urls, q)

df = pd.DataFrame(li)
plotRate(li)







#----------------------------------------------------------


url = 'http://devchocoly-dev1.7qha9u7kea.ap-northeast-1.elasticbeanstalk.com/'
runs = 3
calls = 500
nap = 10

df = loadTest(url, calls, runs, nap)

# plot calls per second
df['pd'] = df.time.apply(lambda x: x.format('hh:mm'))
rate = df.groupby('pd').count()
rate.time.plot(kind='bar')


i = 0
x = []
calls = 10
http_client = httpclient.AsyncHTTPClient()

for url_i in [url]*calls:
    i += 1
    http_client.fetch(url_i.strip(), handleRequest, method='HEAD')
    

ioloop.IOLoop.instance().start()


from tornado.httpclient import AsyncHTTPClient
from tornado.concurrent import Future

def async_fetch_future(url):
    http_client = AsyncHTTPClient()
    my_future = Future()
    fetch_future = http_client.fetch(url)
    fetch_future.add_done_callback(
        lambda f: my_future.set_result(f.result()))
    return my_future

future = async_fetch_future(url)



