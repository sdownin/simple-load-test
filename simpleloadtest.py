# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 21:40:35 2016

@author: sdowning
"""

import requests, sys, logging
import numpy as np
import pandas as pd
import arrow as ar
import matplotlib.pyplot as plt
from time import time, sleep
from threading import Thread
from multiprocessing import Queue


class SimpleLoadTest(object):
    
    def __init__(self, urls):
        logging.basicConfig(filename='simpleloadtestlog.log', level=logging.INFO)
        self.urls = urls if isinstance(urls, (list,np.ndarray,pd.Series)) else [urls]
        self.li = []
        self.df = pd.DataFrame()

    def _getStatus(self, url):
        try:
            response = requests.get(url=url)
        except Exception as e:
            print(e)
            return "error", url
        length = response.headers['content-length'] if 'content-length' in response.headers else 0
        return url, response.status_code, length

    def _handleResults(self):
        while True:
            url = self.q.get()
            url, status, length = self._getStatus(url)
            resultDict = dict(url=url,status=status,length=length,time=ar.now())
            self.li.extend([resultDict])

    def run(self, calls=100, concurrent=25):
        """
        Runs load test.
        
        Params
        -----
            calls : int
                Number of calls in test run [default 100]
            
            concurrent : int
                Number of concurrent connections [default 25]
        """
        self.calls = calls
        self.concurrent = concurrent
        self.q = Queue(self.concurrent)
        t0 = time()
        ## start threads
        for i in range(self.concurrent):
            self.t = Thread(target=self._handleResults)
            self.t.daemon = True
            self.t.start()
        ## make calls
        for url in self.urls:
            msg = 'running test of %s calls (%s concurrently) to %s ...' % (self.calls, self.concurrent, url)
            logging.info(msg);  print(msg)
            try:
                for _ in range(self.calls):
                    self.q.put(url.strip())
                    #q.join_thread()
            except KeyboardInterrupt:
                sys.exit(1)
        ## wait for queue to finish
        while not self.q.empty():
            sleep(1)
        ## results list to dataframe
        keepTrying = True
        while keepTrying:
            try:
                self.df = pd.DataFrame(self.li)
                keepTrying = False
            except Exception as e:
                print(e)
                sleep(1)
        msg = 'completed %s calls in %.2f seconds (%.2f calls/sec)' % (len(self.li), time()-t0, len(self.li)/(time()-t0) )
        logging.info(msg);  print(msg)
#        msg = 'completed %s calls in %.2f seconds (%.2f calls/sec): '
#        for status in self.df.status.unique():
#            msg += ' {:.1%} ' + str(status)
#        msg = msg.format(len(self.li), time()-t0, len(self.li)/(time()-t0), 
#                   self.df.groupby('status').agg({'status':'count'})/ self.df.shape[0] )
#        logging.info(msg);  print(msg)
#        #print(''.format(self.df.groupby('status').agg({'status':'count'})/ len(self.df.shape[0])) ))

    def _plotGroupby(self, param, kind, marker, figsize):
        if len(self.df.columns) > 0:
            if 'pd' not in self.df.columns:
                self.df['pd'] = self.df.time.apply(lambda x: x.format('hh:mm:ss'))
            keepTrying = True
            while keepTrying:
                try:
                    #fig_rate = plt.figure()
                    tmp = self.df.groupby(param).count().time
                    if marker is not '':
                        plot = tmp.plot(kind=kind,figsize=figsize,marker=marker)
                    else: 
                        plot = tmp.plot(kind=kind,figsize=figsize)                 
                    fig = plot.get_figure()
                    fig.savefig('simpleloadtest_group_%s.png' % param)
                    plt.show()
                    keepTrying = False
                except Exception as e:
                    print(e)
                    sleep(1)
    
#    def plotParam(self,param):
#        if plot in ['rate','rates']:
#            param,kind,marker,figsize = 'pd','line', 'o', (10,5)
#        elif plot in ['code','codes']:
#            param,kind,marker,figsize = 'status','bar', '',(6,4)
#        else:
#            raise ValueError('Specificy valid plot type.')
#        plot = self.df.loc[:,param].plot(title=param)
#        fig = plot.get_figure()
#        fig.savefig('simpleloadtest_%s.png' % param)
#        plt.show()
        
    def plotGroup(self, plot):
        """
        Plot results of SimpleLoadTest run.
        
        Params
        -----
            plot : str 
                'rate' : calls per second\n
                'code' : count of http request response codes  
        """
        if plot in ['rate','rates']:
            param,kind,marker,figsize = 'pd','line', 'o', (10,5)
        elif plot in ['code','codes']:
            param,kind,marker,figsize = 'status','bar', '',(6,4)
        else:
            raise ValueError('Specificy valid plot type.')
        self._plotGroupby(param,kind,marker,figsize)

#------------------------------------------------------------------------------
if __name__=='__main__':
    from argparse import ArgumentParser
    par = ArgumentParser(description="Simple Load Tester")
    par.add_argument('url', type=str, help="url to test") 
    par.add_argument('--calls', type=int, default=100, help="number of calls to url [default 100]")
    par.add_argument('--concurrent', type=int, default=25, help="number of concurrent calls [default 25]")
    args = par.parse_args()
    urls = args.url.split(',') if ',' in args.url else [args.url]
    # instantiate test object and run test
    test = SimpleLoadTest(urls)
    test.run(args.calls, args.concurrent)
    test.plotGroup('rate')
    test.plotGroup('code')
#    test.plotParam('code')
    test.df.to_csv('simpleloadtestresponses.csv',index=False)