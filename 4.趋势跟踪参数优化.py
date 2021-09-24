"""
Created on Wed Sep 15 16:27:38 2021
研究指数趋势跟踪的各个参数
"""
#%% 引用模块
from WindPy import *
w.start()
import numpy as np
import pandas as pd 

import matplotlib.pyplot as plt
plt.rcParams['animation.embed_limit'] = 2**64
plt.rcParams['font.sans-serif'] = ['SimHei']#中文标签
plt.rcParams['axes.unicode_minus'] = False #正负号
plt.rc('axes',axisbelow = True)

#%% 读取指数的收盘价和pepb数据
close_df_original = pd.read_excel(r'DataBase\指数收盘价.xlsx', index_col = 0)
pe_df_original = pd.read_excel(r'DataBase\PEPB基础数据.xlsx',sheet_name = 'PE', index_col = 0)
pb_df_original = pd.read_excel(r'DataBase\PEPB基础数据.xlsx',sheet_name = 'PB', index_col = 0)
code_name_ser = pe_df_original['指数名称']

close_df = pd.read_excel(r'DataBase\close2000.xlsx', index_col = 0)
pe_df = pd.read_excel(r'DataBase\pe2000.xlsx', index_col = 0)
pb_df = pd.read_excel(r'DataBase\pb2000.xlsx', index_col = 0)

#%%
class IndexBackTesting():
    def __init__(self, close_df):
        self.close_df = close_df
        #self.strategy_once()
        self.strategy_many()
            
    def strategy_once(self,past_month = 12, future_month = 3, std_param = 1, select_num = 5):#12-0.35 36-0.4
        close_df = self.close_df
        i_date_ser = pd.Series(close_df.index)
        #date_i_ser = pd.Series(range(len(close_df)),index = close_df.index)
        strategy_once_df = pd.DataFrame()
        
        for i in i_date_ser.index:#i = 120
            #计算有效回测日期
            if i + past_month + future_month > i_date_ser.index[-1]:
                break
            past_date = i_date_ser[i]
            now_date = i_date_ser[i + past_month]
            future_date = i_date_ser[i + past_month + future_month]
            close_df_past = close_df.loc[past_date : now_date].dropna(axis = 1)
            close_df_future = close_df.loc[now_date : future_date,close_df_past.columns].dropna(axis = 1)
        
            #计算收益和波动率
            return_past_ser = close_df_past.iloc[-1,:] / close_df_past.iloc[0,:] - 1
            std_past_ser = close_df_past.pct_change().std()
            return_futurn_ser = close_df_future.iloc[-1,:] / close_df_future.iloc[0,:] - 1
            #std_future_ser = close_df_future.pct_change().std()
            
            #计算筛选
            select_past_ser = return_past_ser[std_past_ser < std_past_ser.mean()*std_param].sort_values()[select_num*-1:]
            select_future_ser = return_futurn_ser.loc[select_past_ser.index]
            return_select = select_future_ser.mean()
            if '000300.SH' in return_futurn_ser.index:  
                return_hs300 = return_futurn_ser['000300.SH']
            else:
                return_hs300 = np.nan
                
            if '000001.SH' in return_futurn_ser.index:
                return_sz001 = return_futurn_ser['000001.SH']
            else:
                return_sz001 = 0 
                
            #保存数据
            return_strategy = return_select
            index_code = str(select_future_ser.index.to_list())
            index_name = str(list(code_name_ser[select_future_ser.index]))
            
            strategy_once_df.loc[future_date,['past_month','future_month','std_param','select_num',\
                                              'return_strategy', 'return_hs300','return_sz001','index_code','index_name']] = \
                [past_month, future_month, std_param, select_num,\
                 return_strategy,return_hs300,return_sz001,index_code,index_name]
         
        strategy_once_df.to_excel('DataSave\\4.趋势跟踪参数优化\\1.原始数据\\' + \
                                  'past_month={}&future_month={}&std_param={}&select_num={}.xlsx'.\
                            format(past_month, future_month, std_param, select_num))
        self.strategy_once_df = strategy_once_df
        return strategy_once_df
    
    def strategy_many(self):
        strategy_many_df = pd.DataFrame(columns =['past_month','future_month','std_param','select_num',\
                                                  'profit_annual_strategy', 'profit_annual_hs300','profit_annual_sz001',\
                                                      'std_annual_strategy', 'std_annual_hs300','std_annual_sz001',\
                                                        'sharp_ratio_strategy', 'sharp_ratio_hs300','sharp_ratio_sz001'] )
        i = 0
        for past_month in [12,24,36]:
            
            for future_month in [3]:
                for std_param in np.arange(0.5,3,0.05):
                    for select_num in [1,2,3,4,5,7,10,15,50]:
                        i = i+1
                        strategy_once_df = self.strategy_once(past_month, future_month, std_param, select_num)
                        return_df = strategy_once_df.loc[:,['return_strategy', 'return_hs300','return_sz001']]
                        profit_annual_ser = pow(return_df.mean() + 1, 12/future_month) - 1
                        std_annual_ser = return_df.std() * np.sqrt(12/future_month)
                        sharp_ratio_ser = profit_annual_ser / std_annual_ser
                        strategy_many_df.loc[i,:] = [past_month, future_month, std_param, select_num] +\
                            list(profit_annual_ser) + list(std_annual_ser) + list(sharp_ratio_ser)
 
        self.strategy_many_df = strategy_many_df
                
        
    
#ib = IndexBackTesting(close_df) 
#strategy_once_df = ib.strategy_once_df
#strategy_many_df = ib.strategy_many_df
#strategy_many_df.to_excel('DataSave\\4.趋势跟踪参数优化\\' + '原始数据汇总.xlsx')  

#%% 结果分析
def read_data(start_date = '2011-01-31'):
    strategy_many_df = pd.DataFrame(\
            columns =['past_month','future_month','std_param','select_num',\
                      'profit_annual_strategy', 'profit_annual_hs300','profit_annual_sz001',\
                      'std_annual_strategy', 'std_annual_hs300','std_annual_sz001',\
                      'sharp_ratio_strategy', 'sharp_ratio_hs300','sharp_ratio_sz001'] )
    i = 0
    for past_month in [12,24,36]:
        for future_month in [3]:
            for std_param in np.arange(0.5,3,0.05):
                for select_num in [1,2,3,4,5,7,10,15,50]:
                    i = i+1
                    file_name = 'past_month={}&future_month={}&std_param={}&select_num={}.xlsx'.\
                            format(past_month, future_month, std_param, select_num)
                    strategy_once_df = pd.read_excel('DataSave\\4.趋势跟踪参数优化\\1.原始数据\\' + file_name, index_col = 0)
                    strategy_once_df = strategy_once_df.loc[start_date:,:].copy()
                    return_df = strategy_once_df.loc[:,['return_strategy', 'return_hs300','return_sz001']]
                    profit_annual_ser = pow(return_df.mean() + 1, 12/future_month) - 1
                    std_annual_ser = return_df.std() * np.sqrt(12/future_month)
                    sharp_ratio_ser = profit_annual_ser / std_annual_ser
                    strategy_many_df.loc[i,:] = [past_month, future_month, std_param, select_num] +\
                        list(profit_annual_ser) + list(std_annual_ser) + list(sharp_ratio_ser)
    strategy_many_df.to_excel('DataSave\\4.趋势跟踪参数优化\\' + '{}至今数据分析.xlsx'.format(start_date))  
    return strategy_many_df
strategy_many_df = read_data(start_date = '2016-01-31')

def rename_file():
    for past_month in [12,24,36]:
        for future_month in [3]:
            for std_param in np.arange(0.5,3,0.05):
                for select_num in [1,2,3,4,5,7,10,15,50]:
                    file_name = 'past_month={}&future_month={}&std_param={}&select_num={}.xlsx'.\
                            format(past_month, future_month, std_param, select_num)
                    strategy_once_df = pd.read_excel('DataSave\\4.趋势跟踪参数优化\\1.原始数据\\' + file_name, index_col = 0)
                    
                    file_name_new = 'past_month={}&future_month={}&std_param={:.2f}&select_num={}.xlsx'.\
                            format(past_month, future_month, std_param, select_num)
                    strategy_once_df.to_excel('DataSave\\4.趋势跟踪参数优化\\2.原始数据重命名\\' + file_name_new)
                    

























