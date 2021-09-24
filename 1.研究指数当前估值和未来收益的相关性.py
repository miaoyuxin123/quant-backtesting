"""
Created on Wed Sep  8 10:24:28 2021
查看指数估值和未来收益的相关性
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

#%%计算7年历史百分位
pb_percent_df  = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
percent_parameter = 12*7#在过往7年的历史百分位
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



#%% 计算pe/pb和未来收益的关系
i_date_ser = pd.Series(pe_percent_df.index)
date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)

close_df_long = close_df.shape[0]
result_df = pd.DataFrame(columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
for future_parameter in range(1,120,1):
    #future_parameter = 1
    corr_df = pd.DataFrame(index = close_df.index, columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
    corr_df['未来月份参数'] = future_parameter
    
    for start_date in pe_percent_df.index:
        #start_date = pe_percent_df.index[200]
        if date_i_ser[start_date] + future_parameter > date_i_ser.max():
            break
        future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
        #确认pe，pb，close不是全空的
        pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
        pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
        close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
        if pe_start_ser.empty | pb_start_ser.empty | close_df_select.empty:
            continue
        
        #确认筛选出来的code列表非空
        code_select = []
        for code in pe_start_ser.index:
            if (code in pb_start_ser.index) & (code in close_df_select.columns):
                code_select.append(code)#len(code_select)
        if len(code_select) < 10:
            continue
        
        #计算code_select对应的pe，pb，未来收益
        pe_start_ser = pe_start_ser.loc[code_select].copy()
        pb_start_ser = pb_start_ser.loc[code_select].copy()
        return_future_ser = close_df_select.loc[future_date,code_select] \
            / close_df_select.loc[start_date,code_select] - 1
        
        len(pe_start_ser)
        len(return_future_ser)
        #close_df_select = close_df_select.loc[:,code_select].copy()
        #return_future_ser = (close_df_select.iloc[-1] / close_df_select.iloc[0]) - 1
        
        #计算相关性
        corr_pe = pe_start_ser.corr(return_future_ser)
        corr_pb = pb_start_ser.corr(return_future_ser)
        
        #保存计算结果
        corr_df.loc[future_date, ['pe-未来收益-相关系数','pb-未来收益-相关系数']] = [corr_pe, corr_pb]
    result_df.loc[future_parameter,:] = corr_df.mean()

#result_df.iloc[:,1:].plot(title = '7年百分位所有数据回测')    
#result_df.to_excel('7年百分位所有数据回测.xlsx')

    
    
    
#%%计算5年历史百分位
pb_percent_df  = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
percent_parameter = 12*10#在过往7年的历史百分位
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
    
    
    
i_date_ser = pd.Series(pe_percent_df.index)
date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)

close_df_long = close_df.shape[0]
result_df = pd.DataFrame(columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
for future_parameter in range(1,120,1):
    #future_parameter = 1
    corr_df = pd.DataFrame(index = close_df.index, columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
    corr_df['未来月份参数'] = future_parameter
    
    for start_date in pe_percent_df.index[-120:]:
        #start_date = pe_percent_df.index[200]
        if date_i_ser[start_date] + future_parameter > date_i_ser.max():
            break
        future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
        #确认pe，pb，close不是全空的
        pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
        pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
        close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
        if pe_start_ser.empty | pb_start_ser.empty | close_df_select.empty:
            continue
        
        #确认筛选出来的code列表非空
        code_select = []
        for code in pe_start_ser.index:
            if (code in pb_start_ser.index) & (code in close_df_select.columns):
                code_select.append(code)#len(code_select)
        if len(code_select) < 10:
            continue
        
        #计算code_select对应的pe，pb，未来收益
        pe_start_ser = pe_start_ser.loc[code_select].copy()
        pb_start_ser = pb_start_ser.loc[code_select].copy()
        return_future_ser = close_df_select.loc[future_date,code_select] \
            / close_df_select.loc[start_date,code_select] - 1
        
        len(pe_start_ser)
        len(return_future_ser)
        #close_df_select = close_df_select.loc[:,code_select].copy()
        #return_future_ser = (close_df_select.iloc[-1] / close_df_select.iloc[0]) - 1
        
        #计算相关性
        corr_pe = pe_start_ser.corr(return_future_ser)
        corr_pb = pb_start_ser.corr(return_future_ser)
        
        #保存计算结果
        corr_df.loc[future_date, ['pe-未来收益-相关系数','pb-未来收益-相关系数']] = [corr_pe, corr_pb]
    result_df.loc[future_parameter,:] = corr_df.mean()

#result_df.iloc[:,1:].plot(title = '5年百分位近10年数据回测')    
#result_df.to_excel('5年百分位所有数据回测.xlsx')    
    
     
    
#%%计算10年历史百分位
pb_percent_df  = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
percent_parameter = 12*10#在过往7年的历史百分位
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
    
    
    
i_date_ser = pd.Series(pe_percent_df.index)
date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)

close_df_long = close_df.shape[0]
result_df = pd.DataFrame(columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
for future_parameter in range(1,120,1):
    #future_parameter = 1
    corr_df = pd.DataFrame(index = close_df.index, columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
    corr_df['未来月份参数'] = future_parameter
    
    for start_date in pe_percent_df.index:
        #start_date = pe_percent_df.index[200]
        if date_i_ser[start_date] + future_parameter > date_i_ser.max():
            break
        future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
        #确认pe，pb，close不是全空的
        pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
        pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
        close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
        if pe_start_ser.empty | pb_start_ser.empty | close_df_select.empty:
            continue
        
        #确认筛选出来的code列表非空
        code_select = []
        for code in pe_start_ser.index:
            if (code in pb_start_ser.index) & (code in close_df_select.columns):
                code_select.append(code)#len(code_select)
        if len(code_select) < 10:
            continue
        
        #计算code_select对应的pe，pb，未来收益
        pe_start_ser = pe_start_ser.loc[code_select].copy()
        pb_start_ser = pb_start_ser.loc[code_select].copy()
        return_future_ser = close_df_select.loc[future_date,code_select] \
            / close_df_select.loc[start_date,code_select] - 1
        
        len(pe_start_ser)
        len(return_future_ser)
        #close_df_select = close_df_select.loc[:,code_select].copy()
        #return_future_ser = (close_df_select.iloc[-1] / close_df_select.iloc[0]) - 1
        
        #计算相关性
        corr_pe = pe_start_ser.corr(return_future_ser)
        corr_pb = pb_start_ser.corr(return_future_ser)
        
        #保存计算结果
        corr_df.loc[future_date, ['pe-未来收益-相关系数','pb-未来收益-相关系数']] = [corr_pe, corr_pb]
    result_df.loc[future_parameter,:] = corr_df.mean()

#result_df.iloc[:,1:].plot(title = '10年百分位所有数据回测')    
#result_df.to_excel('10年百分位所有数据回测.xlsx')        
    
#%%计算6年历史百分位
pb_percent_df  = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
percent_parameter = 12*6#在过往7年的历史百分位
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
    
    
    
i_date_ser = pd.Series(pe_percent_df.index)
date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)

close_df_long = close_df.shape[0]
result_df = pd.DataFrame(columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
for future_parameter in range(1,120,1):
    #future_parameter = 1
    corr_df = pd.DataFrame(index = close_df.index, columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
    corr_df['未来月份参数'] = future_parameter
    
    for start_date in pe_percent_df.index:
        #start_date = pe_percent_df.index[200]
        if date_i_ser[start_date] + future_parameter > date_i_ser.max():
            break
        future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
        #确认pe，pb，close不是全空的
        pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
        pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
        close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
        if pe_start_ser.empty | pb_start_ser.empty | close_df_select.empty:
            continue
        
        #确认筛选出来的code列表非空
        code_select = []
        for code in pe_start_ser.index:
            if (code in pb_start_ser.index) & (code in close_df_select.columns):
                code_select.append(code)#len(code_select)
        if len(code_select) < 10:
            continue
        
        #计算code_select对应的pe，pb，未来收益
        pe_start_ser = pe_start_ser.loc[code_select].copy()
        pb_start_ser = pb_start_ser.loc[code_select].copy()
        return_future_ser = close_df_select.loc[future_date,code_select] \
            / close_df_select.loc[start_date,code_select] - 1
        
        len(pe_start_ser)
        len(return_future_ser)
        #close_df_select = close_df_select.loc[:,code_select].copy()
        #return_future_ser = (close_df_select.iloc[-1] / close_df_select.iloc[0]) - 1
        
        #计算相关性
        corr_pe = pe_start_ser.corr(return_future_ser)
        corr_pb = pb_start_ser.corr(return_future_ser)
        
        #保存计算结果
        corr_df.loc[future_date, ['pe-未来收益-相关系数','pb-未来收益-相关系数']] = [corr_pe, corr_pb]
    result_df.loc[future_parameter,:] = corr_df.mean()

#result_df.iloc[:,1:].plot(title = '6年百分位所有数据回测')    
#result_df.to_excel('6年百分位所有数据回测.xlsx')         
    
#%%计算8年历史百分位
pb_percent_df  = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
percent_parameter = 12*8#在过往7年的历史百分位
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
    
    
    
i_date_ser = pd.Series(pe_percent_df.index)
date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)

close_df_long = close_df.shape[0]
result_df = pd.DataFrame(columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
for future_parameter in range(1,120,1):
    #future_parameter = 1
    corr_df = pd.DataFrame(index = close_df.index, columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
    corr_df['未来月份参数'] = future_parameter
    
    for start_date in pe_percent_df.index:
        #start_date = pe_percent_df.index[200]
        if date_i_ser[start_date] + future_parameter > date_i_ser.max():
            break
        future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
        #确认pe，pb，close不是全空的
        pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
        pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
        close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
        if pe_start_ser.empty | pb_start_ser.empty | close_df_select.empty:
            continue
        
        #确认筛选出来的code列表非空
        code_select = []
        for code in pe_start_ser.index:
            if (code in pb_start_ser.index) & (code in close_df_select.columns):
                code_select.append(code)#len(code_select)
        if len(code_select) < 10:
            continue
        
        #计算code_select对应的pe，pb，未来收益
        pe_start_ser = pe_start_ser.loc[code_select].copy()
        pb_start_ser = pb_start_ser.loc[code_select].copy()
        return_future_ser = close_df_select.loc[future_date,code_select] \
            / close_df_select.loc[start_date,code_select] - 1
        
        len(pe_start_ser)
        len(return_future_ser)
        #close_df_select = close_df_select.loc[:,code_select].copy()
        #return_future_ser = (close_df_select.iloc[-1] / close_df_select.iloc[0]) - 1
        
        #计算相关性
        corr_pe = pe_start_ser.corr(return_future_ser)
        corr_pb = pb_start_ser.corr(return_future_ser)
        
        #保存计算结果
        corr_df.loc[future_date, ['pe-未来收益-相关系数','pb-未来收益-相关系数']] = [corr_pe, corr_pb]
    result_df.loc[future_parameter,:] = corr_df.mean()

#result_df.iloc[:,1:].plot(title = '8年百分位所有数据回测')    
#result_df.to_excel('8年百分位所有数据回测.xlsx')             
    
#%%计算9年历史百分位
pb_percent_df  = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
pe_percent_df = pd.DataFrame(index = pe_df.index, columns = pe_df.columns, dtype = np.float64)
percent_parameter = 12*9#在过往7年的历史百分位
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
    
    
    
i_date_ser = pd.Series(pe_percent_df.index)
date_i_ser = pd.Series(range(len(pe_percent_df)),index = pe_percent_df.index)

close_df_long = close_df.shape[0]
result_df = pd.DataFrame(columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
for future_parameter in range(1,120,1):
    #future_parameter = 1
    corr_df = pd.DataFrame(index = close_df.index, columns = ['未来月份参数','pe-未来收益-相关系数','pb-未来收益-相关系数'], dtype = np.float64)
    corr_df['未来月份参数'] = future_parameter
    
    for start_date in pe_percent_df.index:
        #start_date = pe_percent_df.index[200]
        if date_i_ser[start_date] + future_parameter > date_i_ser.max():
            break
        future_date = i_date_ser[date_i_ser[start_date] + future_parameter]
        #确认pe，pb，close不是全空的
        pe_start_ser = pe_percent_df.loc[start_date, :].dropna()
        pb_start_ser = pb_percent_df.loc[start_date, :].dropna()
        close_df_select = close_df.loc[start_date : future_date].dropna(axis = 1)
        if pe_start_ser.empty | pb_start_ser.empty | close_df_select.empty:
            continue
        
        #确认筛选出来的code列表非空
        code_select = []
        for code in pe_start_ser.index:
            if (code in pb_start_ser.index) & (code in close_df_select.columns):
                code_select.append(code)#len(code_select)
        if len(code_select) < 10:
            continue
        
        #计算code_select对应的pe，pb，未来收益
        pe_start_ser = pe_start_ser.loc[code_select].copy()
        pb_start_ser = pb_start_ser.loc[code_select].copy()
        return_future_ser = close_df_select.loc[future_date,code_select] \
            / close_df_select.loc[start_date,code_select] - 1
        
        len(pe_start_ser)
        len(return_future_ser)
        #close_df_select = close_df_select.loc[:,code_select].copy()
        #return_future_ser = (close_df_select.iloc[-1] / close_df_select.iloc[0]) - 1
        
        #计算相关性
        corr_pe = pe_start_ser.corr(return_future_ser)
        corr_pb = pb_start_ser.corr(return_future_ser)
        
        #保存计算结果
        corr_df.loc[future_date, ['pe-未来收益-相关系数','pb-未来收益-相关系数']] = [corr_pe, corr_pb]
    result_df.loc[future_parameter,:] = corr_df.mean()

#result_df.iloc[:,1:].plot(title = '9年百分位所有数据回测')    
#result_df.to_excel('9年百分位所有数据回测.xlsx')     