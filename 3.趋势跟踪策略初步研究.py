"""
Created on Thu Sep  9 18:23:12 2021
研究指数特点，寻找盈利策略
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
code_name_ser = pe_df_original['指数名称']

close_df = pd.read_excel(r'DataBase\close2000.xlsx', index_col = 0)
pe_df = pd.read_excel(r'DataBase\pe2000.xlsx', index_col = 0)
pb_df = pd.read_excel(r'DataBase\pb2000.xlsx', index_col = 0)

#%%
class IndexBackTesting():
    def __init__(self, close_df):
        self.close_df = close_df
        #self.back_many()
        self.strategy_once()
        #self.strategy_many()
        
    def back_once(self,past_parameter = 12, future_parameter = 3):
        #时间计算工具
        close_df = self.close_df
        i_date_ser = pd.Series(close_df.index)
        date_i_ser = pd.Series(range(len(close_df)),index = close_df.index)
        back_df = pd.DataFrame()
        
        
        for start_date in close_df.index:#start_date = close_df.index[200]
            #提取过去和未来时间段收盘价
            if date_i_ser[start_date] + past_parameter +future_parameter <= date_i_ser.max():
                now_date = i_date_ser[date_i_ser[start_date] + past_parameter]
                future_date = i_date_ser[date_i_ser[now_date] + future_parameter]        
            else:
                break
            close_df_past = close_df.loc[start_date : now_date].dropna(axis = 1)
            close_df_future = close_df.loc[now_date : future_date,close_df_past.columns].dropna(axis = 1)
            
            #计算收益和波动率
            return_past_ser = close_df_past.iloc[-1,:] / close_df_past.iloc[0,:] - 1
            std_past_ser = close_df_past.pct_change().std()
            
            return_futurn_ser = close_df_future.iloc[-1,:] / close_df_future.iloc[0,:] - 1
            std_future_ser = close_df_future.pct_change().std()
            
            #计算相关系数
            corr_return = return_past_ser.corr(return_futurn_ser)
            corr_std = std_past_ser.corr(std_future_ser)
            
            #保存结果
            back_df.loc[now_date,['收益相关性','波动相关性']] = [corr_return, corr_std]
            
        self.back_df = back_df
        return back_df
        
    def back_many(self):
        back_many_df = pd.DataFrame(columns = ['过去月份','未来月份','收益相关系数','波动相关系数'])
        for past_parameter in range(1,60,1):
            future_parameter = 3
            back_df = self.back_once(past_parameter = past_parameter,future_parameter = future_parameter)
            back_many_df.loc[past_parameter,:] = [past_parameter, future_parameter] + list(back_df.mean())
            
        self.back_many_df = back_many_df
        
        
    def strategy_once(self,past_parameter = 12, future_parameter = 3, select_num = 5):#12-0.35 36-0.4
        close_df = self.close_df
        i_date_ser = pd.Series(close_df.index)
        #date_i_ser = pd.Series(range(len(close_df)),index = close_df.index)
        strategy_once_df = pd.DataFrame()
        
        
        for i in i_date_ser.index:#i = 120
            #计算有效回测日期
            if i + past_parameter + future_parameter > i_date_ser.index[-1]:
                break
            past_date = i_date_ser[i]
            now_date = i_date_ser[i + past_parameter]
            future_date = i_date_ser[i + past_parameter + future_parameter]
            close_df_past = close_df.loc[past_date : now_date].dropna(axis = 1)
            close_df_future = close_df.loc[now_date : future_date,close_df_past.columns].dropna(axis = 1)
        
            #计算收益和波动率
            return_past_ser = close_df_past.iloc[-1,:] / close_df_past.iloc[0,:] - 1
            std_past_ser = close_df_past.pct_change().std()
            return_futurn_ser = close_df_future.iloc[-1,:] / close_df_future.iloc[0,:] - 1
            #std_future_ser = close_df_future.pct_change().std()
            
            #计算筛选
            select_past_ser = return_past_ser[std_past_ser < std_past_ser.mean()*1].sort_values()[select_num*-1:]
            select_future_ser = return_futurn_ser.loc[select_past_ser.index]
            return_select = select_future_ser.mean()
            if '000300.SH' in return_futurn_ser.index:  
                return_300 = return_futurn_ser['000300.SH']
            else:
                return_300 = np.nan
                
            #保存数据
            future_date_name = '策略收益_Past={}M_Future={}M_Select={}'.format(past_parameter,future_parameter, select_num)
            select_index_code = '{}_index_code'.format(select_num)
            select_index_name = '{}_index_name'.format(select_num)
            strategy_once_df.loc[future_date,[future_date_name, '沪深300收益',select_index_code,select_index_name]] = \
                [return_select,return_300,\
                 str(select_future_ser.index.to_list()),\
                     str(list(code_name_ser[select_future_ser.index]))]
            
        #strategy_once_df.to_excel('past_parameter={}&future_parameter={}&select_num={}.xlsx'.format(past_parameter,future_parameter,select_num))
        self.strategy_once_df = strategy_once_df
        return strategy_once_df
    
    def strategy_many(self):
        strategy_many_df = pd.DataFrame()
        for select_num in range(1,51,1):
            print(select_num)
            strategy_once_df = self.strategy_once(past_parameter = 12, future_parameter = 3, select_num = select_num)
            for col in strategy_once_df.columns:
                #col = '过去月份参数'
                if col not in strategy_many_df.columns:
                    strategy_many_df[col] = strategy_once_df[col]
        self.strategy_many_df = strategy_many_df
                
        
    
ib = IndexBackTesting(close_df) 
strategy_once_df = ib.strategy_once_df
#strategy_many_df = ib.strategy_many_df
#strategy_many_df.to_excel('过去12月未来3月选择1-50指数的回测.xlsx')  




#%% 结果分析
pepb_df = pd.read_excel(r'E:\Project\0.新基金评分\DataBase\StockIndex\DataSave\PEPB研究\pepb过去7年未来3月回测.xlsx',\
                         index_col = 0)
trend_df = pd.read_excel(r'E:\Project\0.新基金评分\DataBase\StockIndex\DataSave\趋势跟踪策略\过去12月未来3月选择1-50指数的回测.xlsx',\
                         index_col = 0)

all_df = trend_df.loc[pepb_df.index[:-3],:].iloc[:,2:].copy()
all_df['pepb收益'] = pepb_df['3月后收益']
all_df.mean().sort_values(ascending = False)
all_df.std().sort_values()
sharp_ser = (all_df.mean() / all_df.std()).sort_values()


#%% 提取数据
#return_df = all_df.drop(columns = '沪深300收益').copy()
#select_col = ['pepb收益', '沪深300收益', '3月5指数收益', '3月10指数收益', '3月15指数收益', '3月20指数收益']
#return_df = all_df.loc[:,select_col]
select_col = ['pepb收益','3月5指数收益','沪深300收益']
return_df = all_df.loc[:,select_col].copy()

#用马科维茨理论研究最佳组合
back_num = 10000
return_mean_arr = np.array(return_df.mean())
return_df_long = return_df.shape[1]
#np.random.seed(return_df_long)#设置一个种子，保证每次生成的随机数序列一致
back_result_arr = np.empty((back_num, return_df_long + 2))
for i in range(back_num):
    random_arr = np.random.random(return_df_long)#生成0-1之间的随机数，数量同基金数量
    weight_arr = random_arr / random_arr.sum()#用上面的随机数计算得随机权重
    
    por_return = np.dot(return_mean_arr, weight_arr)
    cov_mat = return_df.cov()#协方差矩阵（两两之间的协方差，协方差代表了两列变量的总体误差）
    #VAR_组合 = weight.T 点乘 （cov_mat 点乘 weight）
    por_std = np.sqrt(np.dot(weight_arr.T,np.dot(cov_mat,weight_arr)))
    
    #保存数据
    back_result_arr[i][: return_df_long] = weight_arr
    back_result_arr[i][return_df_long] = por_std
    back_result_arr[i][return_df_long + 1] = por_return
columns_name_list = [name + '-权重' for name in return_df.columns] + ['por_std','por_return']
result_df = pd.DataFrame(back_result_arr, columns = columns_name_list)
result_df['por_sharp'] = result_df['por_return'] / result_df['por_std']

#绘图
result_df.plot('por_std','por_return', kind='scatter',alpha=0.3)
std_min_index = result_df.por_std.idxmin()#最小方差的索引
sharp_max_index = result_df.por_sharp.idxmax()#最大夏普

#波动率最小
x_std_min = result_df.loc[std_min_index, 'por_std']
y_std_min = result_df.loc[std_min_index, 'por_return']
plt.scatter(x_std_min, y_std_min, color = 'red')
plt.text(x_std_min, \
         y_std_min, \
         str((np.round(x_std_min,4),np.round(y_std_min,4))) + '-波动率最小',\
         ha='left',va='bottom',fontsize=10)

#夏普率最大    
x_sharp_max = result_df.loc[sharp_max_index, 'por_std']
y_sharp_max = result_df.loc[sharp_max_index, 'por_return']
plt.scatter(x_sharp_max, y_sharp_max, color = 'red')
plt.text(x_sharp_max, \
         y_sharp_max, \
         str((np.round(x_sharp_max,4),np.round(y_sharp_max,4))) + '-夏普率最大',\
         ha='left',va='bottom',fontsize=10)    
 
plt.show()
print('波动率最小：\r\n',result_df.loc[std_min_index,:])
print('\r\n夏普率最大：\r\n',result_df.loc[sharp_max_index,:])





    
    