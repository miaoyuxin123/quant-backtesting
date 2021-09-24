"""
Created on Thu Sep 16 18:15:12 2021
选取一定的参数进行回测
"""
#%% 引用模块
from WindPy import *
w.start()
import numpy as np
import pandas as pd 
from datetime import datetime
from pandas.tseries.offsets import DateOffset


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
        
        for i in i_date_ser.index:#i = 245 246 247
            #计算有效回测日期
            if i + past_month > i_date_ser.index[-1]:#过去数据不完整
                break
            
            past_date = i_date_ser[i]
            now_date = i_date_ser[i + past_month]            
            if i + past_month + future_month > i_date_ser.index[-1]:
                future_date = i_date_ser.iloc[-1]
            else:
                future_date = i_date_ser[i + past_month + future_month]
                        
            close_df_past = close_df.loc[past_date : now_date].dropna(axis = 1)
            close_df_future = close_df.loc[now_date : future_date,close_df_past.columns].dropna(axis = 1)
        
            #计算收益和波动率
            return_past_ser = close_df_past.iloc[-1,:] / close_df_past.iloc[0,:] - 1
            std_past_ser = close_df_past.pct_change().std()
            return_futurn_ser = close_df_future.iloc[-1,:] / close_df_future.iloc[0,:] - 1
            #std_future_ser = close_df_future.pct_change().std()
            
            #计算筛选
            select_past_ser = return_past_ser[std_past_ser < std_past_ser.mean()*std_param].sort_values(ascending = False)[:select_num]
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
            
            strategy_once_df.loc[now_date,['past_month','future_month','std_param','select_num',\
                                              'return_strategy', 'return_hs300','return_sz001','index_code','index_name']] = \
                [past_month, future_month, std_param, select_num,\
                 return_strategy,return_hs300,return_sz001,index_code,index_name]
        self.strategy_once_df = strategy_once_df
        return strategy_once_df
    
    def strategy_many(self):
        past_month = 12
        future_month = 3
        std_param = 1.2
        select_num = [1,2,3,4,5,7,10,15,50][0]
        for select_num in [1,2,3,4,5,7,10,15,50]:
            strategy_once_df = self.strategy_once(past_month, future_month, std_param, select_num)
            strategy_once_df.to_excel('DataSave\\5.趋势跟踪参数回测\\1.原始数据\\' + \
                          'past_month={}&future_month={}&std_param={}&select_num={}.xlsx'.\
                    format(past_month, future_month, std_param, select_num))
ib = IndexBackTesting(close_df) 
#strategy_once_df = ib.strategy_once_df

#%% 回测数据
def nav_df(start_date = '2010-12-31'):
    """
    计算净值
    """
    past_month = 12
    future_month = 3
    std_param = 1.2
    select_num = [1,2,3,4,5,7,10,15,50]
    strategy_many_df = pd.DataFrame(dtype = np.float64)
    
    for select_num in select_num:
        strategy_once_df = pd.read_excel('DataSave\\5.趋势跟踪参数回测\\1.原始数据\\'+\
                                         'past_month={}&future_month={}&std_param={}&select_num={}.xlsx'.\
                                         format(past_month, future_month, std_param, select_num), index_col = 0)
        strategy_once_df_part = strategy_once_df.loc[start_date:,:]
        back_ser = range(0,len(strategy_once_df_part),future_month)
        back_df = strategy_once_df_part.iloc[back_ser,:].copy()
        back_df_nav = (back_df.loc[:,['return_strategy', 'return_hs300', 'return_sz001']]+1).cumprod()
        #back_df_nav.plot(title = select_num)
        back_df.loc[:,['net_strategy', 'net_hs300', 'net_sz001']] = back_df_nav.values
        strategy_many_df['select_num={}'.format(select_num)] = back_df['net_strategy']
    strategy_many_df.loc[:,['net_hs300', 'net_sz001']] = back_df.loc[:,['net_hs300', 'net_sz001']]
    return strategy_many_df

       
strategy_many_df = nav_df()
strategy_many_df.plot()
max_draw_down = (strategy_many_df / strategy_many_df.cummax() - 1).min()
print(max_draw_down)
strategy_many_df.to_excel('合成净值数据.xlsx')

#%% 统计筛选的指数和对应收益率
def statistics_df(start_date = '2010-12-31'):
    """统计筛选的指数和对应收益率"""
    past_month = 12
    future_month = 3
    std_param = 1.2
    select_num = [1,2,3,4,5,7,10,15,50]#select_num=1
    statistics_df = pd.DataFrame(dtype = np.float64)
    
    for select_num in select_num:
        strategy_once_df = pd.read_excel('DataSave\\5.趋势跟踪参数回测\\1.原始数据\\'+\
                                         'past_month={}&future_month={}&std_param={}&select_num={}.xlsx'.\
                                         format(past_month, future_month, std_param, select_num), index_col = 0)
        strategy_once_df_part = strategy_once_df.loc[start_date:,:]
        back_ser = range(0,len(strategy_once_df_part))
        back_df = strategy_once_df_part.iloc[back_ser,:].copy()
        statistics_df['select_num={}'.format(select_num)] = back_df['return_strategy']
    add_code_list = ['return_hs300', 'return_sz001','index_code','index_name'] 
    statistics_df.loc[:,add_code_list] = back_df.loc[:,add_code_list]
    return statistics_df

statistics_df = statistics_df()





















