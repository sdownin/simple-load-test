# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 21:40:35 2016

@author: sdowning
"""

import requests, sys, math
import arrow as ar
import pandas as pd
from time import sleep
from threading import Thread
from multiprocessing import Queue


class ChocolyLoadTest(object):
    def __init__(self, url, calls=None):
        self.calls = calls if calls is not None else 1000
        self.concurrent = min(math.floor(self.calls/4), 100)
        self.q = Queue(self.concurrent)
        self.url = url
        self.urls = [url]*self.calls
        self.li = []
        self.df = pd.DataFrame()

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

    def run(self):
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
        self.q.close()

    def plotRate(self):
        keepTrying = True
        while keepTrying:
            try:
                df = pd.DataFrame(self.li)
                keepTrying = False
            except Exception as e:
                print(e)
                sleep(1)
        df['pd'] = df.time.apply(lambda x: x.format('hh:mm:ss'))
        rate = df.groupby('pd').count()
        rate.time.plot(kind='bar',figsize=(10,5))
        self.df = df
    
    def plotCodes(self):
        if len(self.df.columns) > 0:
            keepTrying = True
            while keepTrying:
                try:
                    self.df.groupby('status').count().pd.plot(kind="bar")
                    keepTrying = False
                except Exception as e:
                    print(e)
                    sleep(1)


if __name__=='__main__':
    url = 'http://devchocoly-dev1.7qha9u7kea.ap-northeast-1.elasticbeanstalk.com/'
    clt = ChocolyLoadTest(url, calls=8000)
    clt.run()
    clt.plotRate()
    clt.plotCodes()
