# -*- coding:utf-8 -*-
####################################################################################################################
'''
从wind采集原始数据，存储到mysql中
'''
####################################################################################################################
import pandas as pd
from WindPy import *
from sqlalchemy import create_engine
import datetime,time
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class WindStock():

    def getCurrentTime(self):
        # 获取当前时间
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def getCurrentDate(self):
        # 获取当前日期
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def error_log(self,trade_date,symbol,start_date,end_date,table_name,e,engine):
        error_log_df=pd.DataFrame()
        error_log_df['trade_date']=trade_date
        error_log_df['stock_code']=symbol
        error_log_df['start_date']=start_date
        error_log_df['end_date']=end_date
        error_log_df['table']=table_name
        error_log_df['args']='Symbol: '+symbol+' From '+start_date+' To '+end_date
        error_log_df['error_info']=e
        error_log_df['created_date']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        error_log_df.to_sql('stock_error_log',engine,if_exists='append')

    def GetSaveStockHisData(self,symbols,start_date,end_date):
        '''
        逐个股票代码查询行情数据
        wsd代码可以借助 WindNavigator自动生成copy即可使用
        '''
        print self.getCurrentTime(),": Download Stock Starting:"
        for symbol in symbols:
             w.start()
             try:
                 #stock=w.wsd(symbol,'trade_code,open,high,low,close,volume,amt',start_date,end_date)
                 '''
                 wsd代码可以借助 WindNavigator自动生成copy即可使用;
                 时间参数不设，默认取当前日期，可能是非交易日没数据;
                 只有一个时间参数，默认为起始时间到最新；如设置两个时间参数则依次为起止时间
                '''
                 table_name = 'table_try'
                 #wgsd_com_eq
                 stock=w.wsd("600012.SH", "ev2_to_ebitda,val_evtoebitda2", "2016-03-31", "2017-06-01", "Period=M;PriceAdj=F")
                 index_data = pd.DataFrame()
                 index_data['trade_date']=stock.Times
                 index_data['stock_code'] =symbol
                 index_data['ev2_to_ebitda']=stock.Data[0]
                 index_data['val_evtoebitda2']=stock.Data[1]
                 index_data['data_source']='Wind'
                 index_data['created_date']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                 # index_data.fillna(0)
                 try:
                    index_data.to_sql(table_name,engine,if_exists='append');
                 except Exception as e:
                     #如果写入数据库失败，写入日志表，便于后续分析处理
                     self.error_log(self,str(stock.Times).split(' ')[0],symbol,start_date,end_date,table_name,e,engine)
                     print   self.getCurrentTime(),": SQL Exception :%s" % (e)
                     continue
                 w.start()
             except Exception as e:
                     #如果读取处理失败，可能是网络中断、频繁访问被限、历史数据缺失等原因。写入相关信息到日志表，便于后续补充处理
                     self.error_log(self,str(stock.Times).split(' ')[0],symbol,start_date,end_date,table_name,e,engine)
                     print  self.getCurrentTime(),":index_data %s : Exception :%s" % (symbol,e)
                     time.sleep(sleep_time)
                     w.start()
                     continue
             print  self.getCurrentTime(),": Downloading [",symbol,"] From "+start_date+" to "+end_date

        print  self.getCurrentTime(),": Download A Stock Has Finished ."

def main():
    '''
    主调函数，可以通过参数调整实现分批下载
    '''
    global engine,sleep_time,symbols
    sleep_time=5
    windStock=WindStock()
    engine = create_engine('mysql://root:zjz4818774@localhost/invest?charset=utf8')
    #start_date='20100101'
    #end_date='20131231'
    #symbols=windStock.getAStockCodesFromCsv()#通过文件获取股票代码
    #symbols=windStock.getAStockCodesWind()
    #通过Wind API获取股票代码,默认取最新的，可以指定取历史某一日所有A股代码
    symbols=['000001.SZ']#通过直接赋值获取股票代码用于测试
    print symbols
    #windStock.AStockHisData(symbols,start_date,end_date)

    # for i in range(2013,1990,-1):
    #      start_date=str(i)+'0101'
    #      end_date=str(i)+'1231'
    #      print start_date,end_date,'Starting'
    #      symbols=windStock.getAStockCodesWind()
    #      windStock.AStockHisData(symbols,start_date,end_date)
    #      print start_date,end_date,'Finished'
    start_date="2016-03-31"
    end_date="2017-06-01"

    print 'Starting'
    windStock.GetSaveStockHisData(symbols,start_date,end_date)
    print 'Finished'


if __name__ == "__main__":
    # my_windstock = WindStock()
    # current_time = my_windstock.getCurrentTime()
    # print current_time
    # current_date = my_windstock.getCurrentDate()
    # print current_date
    main()