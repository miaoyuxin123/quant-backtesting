# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 18:42:48 2021

@author: 25156
"""

"""
Created on Wed Sep  8 18:08:47 2021
基于7年pepb百分比的回测
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

close_df = pd.read_excel(r'DataBase\close2000.xlsx', index_col = 0)
pe_df = pd.read_excel(r'DataBase\pe2000.xlsx', index_col = 0)
pb_df = pd.read_excel(r'DataBase\pb2000.xlsx', index_col = 0)

aniu_df = pd.read_excel(r'D:\Aniu\1.1 指数基金策略_基础数据.xlsx',index_col = 0)
code_select = []
for code in aniu_df.index:
    if code in close_df.columns:
        code_select.append(code)
        
close_df = close_df.loc[:,code_select] 
pe_df = pe_df.loc[:,code_select] 
pb_df = pb_df.loc[:,code_select]  

#%%
class PePbBackTesting():
    def __init__(self, pe_df, pb_df,close_df, percent_history_year = 7, select_num = 4):
        self.pe_df = pe_df
        self.pb_df = pb_df
        self.close_df = close_df
        self.percent_history_year = percent_history_year
        self.select_num = select_num
        
        self.pepb_percent()
        self.back_once()
        #self.back_many()

    def pepb_percent(self):
        pb_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
        pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
        percent_parameter = 12*self.percent_history_year#在过往7年的历史百分位
        for i in range(percent_parameter,pe_df.shape[0] + 1,1):
            #i = percent_parameter
            start_date = i - percent_parameter
            pe_df_select = pe_df.iloc[start_date : i,:].dropna(axis = 1)#必须数据满n年
            pe_percent_ser = (pe_df_select.rank() /  pe_df_select.rank().max()).iloc[-1,:]
            
            pb_df_select = pb_df.iloc[start_date : i,:].dropna(axis = 1)
            pb_percent_ser = (pb_df_select.rank() /  pb_df_select.rank().max()).iloc[-1,:]
            
            i_date = pe_df_select.index[-1]
            pe_percent_df.loc[i_date,:] = pe_percent_ser
            pb_percent_df.loc[i_date,:] = pb_percent_ser
        self.pe_percent_df, self.pb_percent_df = pe_percent_df, pb_percent_df
        
    def back_once(self, future_parameter = 3):   
        pe_percent_df = self.pe_percent_df
        pb_percent_df = self.pb_percent_df
        back_df = pd.DataFrame(index = close_df.index, \
                               columns = ['未来月份参数','pe百分位均值','pb百分位均值','上证指数收益',\
                                          '沪深300收益','策略{}个月收益'.format(future_parameter),'选择指数'], dtype = np.float64)
        back_df['未来月份参数'] = future_parameter
        i_date_ser = pd.Series(pe_percent_df.index)
        date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)
        
        for start_date in pe_percent_df.index:
            #start_date = pe_percent_df.index[200]
            if date_i_ser[start_date] + future_parameter <= date_i_ser.max():
                future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
            else:
                break
            
            #确认pe，pb，close不是全空的
            pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
            pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
            close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
            if '000300.SH' in close_df_select.columns:
                return_300 = close_df_select['000300.SH'][-1] / close_df_select['000300.SH'][0] - 1
            else:
                return_300 = 0
            
            if '000001.SH' in close_df_select.columns:
                return_001 = close_df_select['000001.SH'][-1] / close_df_select['000001.SH'][0] - 1
            else:
                return_001 = 0                
            
                   
            #确认筛选出来的code列表非空
            code_select = []
            for code in pe_start_ser.index:
                if (code in pb_start_ser.index) & (code in close_df_select.columns):
                    code_select.append(code)#len(code_select)
            if len(code_select) == 0:
                back_df.loc[future_date, 'pe百分位均值':] =  [np.nan, np.nan, np.nan, np.nan, np.nan, '指数为空']
                continue
            
            #筛选pe/pb百分位都在0.4以下的数据
            pe_start_ser = pe_start_ser.loc[code_select].copy()
            pb_start_ser = pb_start_ser.loc[code_select].copy()
            
            
            select_ser = pe_start_ser[(pe_start_ser < 0.4) & (pb_start_ser < 0.4)].sort_values()[:self.select_num]
            code_select = list(select_ser.index)
            
            if len(code_select) == 0:
                back_df.loc[future_date, 'pe百分位均值':] =  [np.nan, np.nan, np.nan, np.nan, np.nan,'0.4分位下为空']
                continue
            
            #计算筛选的pe pb return
            pe_start_ser = pe_start_ser.loc[code_select].copy()
            pb_start_ser = pb_start_ser.loc[code_select].copy()
            return_future_ser = close_df_select.loc[future_date,code_select] \
                / close_df_select.loc[start_date,code_select] - 1
        
            
            #保存计算结果
            back_df.loc[future_date, 'pe百分位均值':] = \
                [pe_start_ser.mean(), pb_start_ser.mean(), return_001, return_300, return_future_ser.mean(), str(tuple(code_select))]

        self.back_df = back_df
        return back_df
    
    def back_many(self):
        result_df = pd.DataFrame(dtype = np.float64, columns = ['未来月份参数','上证指数收益','同期沪深300收益','策略平均收益'])
        for future_parameter in range(1,3,1):
            back_df = self.back_once(future_parameter = future_parameter)
            result_df.loc[future_parameter,:] = list(back_df.iloc[:,[0,3,4]].mean())
        self.result_df = result_df
            


#pp = PePbBackTesting(pe_df, pb_df,close_df)
#pp.result_df.to_excel('总回测.xlsx')
#back_df = pp.back_df
#back_df.to_excel('基金回测.xlsx')

    
#%% 回测结果分析
back_df = pp.back_df
class ResultAnalysis():
    def __init__(self, back_df):
        self.back_df = back_df
        self.month_delta = 3
        self.end_date = '2021-08-31'
        self.back_df_long = len(back_df)
        self.i_date_ser = pd.Series(back_df.index)
        self.date_i_ser = pd.Series(range(0,len(back_df),1), index = back_df.index)
        self.return_dict = {}
        
        self.sta_once()
    
    def sta_once(self, start_date = '2011-01-31'):
        i = self.date_i_ser[start_date]
        i_ser = range(i, self.back_df_long, self.month_delta)
        date_ser = self.i_date_ser[i_ser]
        back_df_part = self.back_df.loc[date_ser,['上证指数收益','沪深300收益', '策略3个月收益']].fillna(0)
        back_df_part.iloc[0,:] = 0
        sta_once_df = (back_df_part + 1).cumprod()
        self.sta_once_df = sta_once_df
    

#ra = ResultAnalysis(back_df)
#sta_once_df = ra.sta_once_df
#%% 主函数
def main():
    for percent_history_year in [5,6,7,8,9,10]:
        for select_num in [1,2,3,4,5,7,10]:
            pp = PePbBackTesting(pe_df, pb_df,close_df,percent_history_year,select_num)
            back_df = pp.back_df
            back_df.to_excel('DataSave\\PEPB研究\\n年m指数-原始-旧指数库\\'+'history={}year&num={}_原始数据.xlsx'.format(percent_history_year,select_num))
            ra = ResultAnalysis(back_df)
            ra.sta_once_df.to_excel('DataSave\\PEPB研究\\n年m指数-净值-旧指数库\\'+'history={}year&num={}.xlsx'.format(percent_history_year,select_num))
          
        
#main()   

#%% 读取保存的数据
sta_many_df = pd.DataFrame(columns = ['历史n年','选择指数',\
    '收益-上证001','收益-沪深300','收益-策略',\
    '波动-上证001','波动-沪深300','波动-策略',\
    '夏普-上证001','夏普-沪深300','夏普-策略'])
return_many_df = pd.DataFrame()
std_many_df = pd.DataFrame()
sharp_many_df = pd.DataFrame()

i = 1
for percent_history_year in [5,6,7,8,9,10]:
    for select_num in [1,2,3,4,5,7,10]:
        sta_once_df = pd.read_excel('DataSave\\PEPB研究\\n年m指数-净值-旧指数库\\'+'history={}year&num={}.xlsx'.\
                                    format(percent_history_year,select_num),index_col = 0)
        sta_once_df.plot(title = '{}年{}个指数'.format(percent_history_year, select_num))
        return_ser = (sta_once_df.iloc[-1,:] / sta_once_df.iloc[0,:])**(1/((len(sta_once_df) - 1)/4)) - 1
        std_ser = sta_once_df.pct_change().std()*np.sqrt(4)
        sharp_ser = return_ser / std_ser
        sta_many_df.loc[i,:] = [percent_history_year,select_num] + list(return_ser) + list(std_ser)+ list(sharp_ser)
        i += 1

#sta_many_df.to_excel('n年m个指数-旧指数库.xlsx')

    
    
    