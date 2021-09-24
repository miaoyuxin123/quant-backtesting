# quant-backtesting
#量化投资回测，python，wind，股票基金

import numpy as np
import pandas as pd 
from datetime import date,time,datetime
from scipy import optimize


class DataManager():
    """
    数据下载：load_data，code_df
    添加信号：signal_add
    按照信号分割数据：code_df_split
    计算分割数据指标：code_df_index_count
    """
    def __init__(self,
                 start_date,
                 end_date,
                 code=None,
                 interval = 'quarter_first',**kw):
        """interval_position_pre:指标计算是往前推几个信号周期"""
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        
        self.init_kw(kw)
        self.init_engine()
                
    def init_kw(self,kw):
        """调仓和其他信号"""
        for k,v in kw.items():
            if k == 'interval_position':
                self.interval_position = v
            elif k == 'interval_position_pre':
                self.interval_position_pre = v

    def init_engine(self):
        #self.init_kw()
        self.load_data()#下载数据
        print(1)
        self.code_df()#切片回测数据
        print(2)
        self.signal_add()#添加交易信号
        print(3)
        self.code_df_split()#拆分表格
        print(4)
        self.code_df_index_count()#计算
        print(5)    
        

        
    def load_data(self):
        """下载所有基金数据"""
        data_path = 'D:\\BackTesting\\DataManager\\复权净值_股票+混合基金.csv'
        self.load_data_df = pd.read_csv(data_path, index_col = 0)
        error_code_list = ['160620.OF']
        self.load_data_df.drop(error_code_list,axis = 1, inplace = True)
        
    def code_df(self):
        """根据回测股票代码和日期生成目标回测df"""
        code = self.code
        
        if code == None or code == []:
            code_list = list(self.load_data_df.columns)
        elif type(code) != list:
            code_list = [code]
        else:
            code_list = code
        
        #根据start_date计算前推时间点start_date_pre   
        try: 
            date_path = 'D:\\BackTesting\\DataManager\\date.csv'
            date_df = pd.read_csv(date_path, index_col = 0)
            if self.interval_position not in date_df.columns:
                print('参数self.interval_position有误')
                return
            first_signal = date_df.loc[self.start_date:self.end_date,self.interval_position].index[0]
            date_df_part = date_df.loc[:first_signal,self.interval_position]
            start_date_pre = date_df_part[date_df_part == 1].index[(self.interval_position_pre+1)*-1]
        except:
            start_date_pre = self.start_date
        self.start_date_pre = start_date_pre
        
        #取交集，剔除不存在的code
        code_list = list(set(code_list) & set(self.load_data_df.columns))
        code_df = self.load_data_df.loc[self.end_date:self.start_date_pre,code_list].copy()
        
        if type(code_df.index[0]) == str:#将日期字符串转换成标准时间
            new_index = [datetime.strptime(d,"%Y-%m-%d").date() for d in code_df.index]
            code_df.index = new_index    
        code_df.sort_index(axis = 0,ascending = True,inplace = True)#索引重新排序
        #code_df.fillna(method='bfill',inplace = True)#针对可能出现的缺失值向下填充    
        self.code_df = code_df

    def signal_add(self):
        """日期作为信号的序列"""
        date_path = 'D:\\BackTesting\\DataManager\\date.csv'
        date_df = pd.read_csv(date_path, index_col = 0)
        date_df.index = [datetime.strptime(d,'%Y-%m-%d').date() for d in date_df.index]
        #添加定投信号
        if self.interval in date_df.columns:
            self.code_df['signal'] = date_df.loc[self.code_df.index,self.interval]
        else:
            print('定投周期有误')
            return
        #添加调仓信号
        try:               
            if self.interval_position in date_df.columns:
                self.code_df['signal_position'] = date_df.loc[self.code_df.index,self.interval_position]
            else:
                print('调仓周期有误')
                return
        except:
            self.code_df['signal_position'] = 0

    def code_df_split(self):
        """按照调仓信号，分割code_df，分出来两个列表
        code_df_trade_list:交易的df列表
        code_df_index_list:用于计算交易信号的df列表"""
        code_df = self.code_df
        date_signal_position_list = list(code_df[code_df['signal_position'] == 1].index)#所有换仓信号[1,2,3,4，5]
        #如果不调仓，交易列表为开始-结束时间内的数据切片
        if not date_signal_position_list:
            self.code_df_trade_list = [code_df]
            self.code_df_index_list = []
            return
            
        date_trade_list = date_signal_position_list[self.interval_position_pre:]#换仓信号[3,4，5]
        date_index_list = date_signal_position_list[:self.interval_position_pre*-1]#换仓计算信号[1,2,3],1-3计算3,3-4计算4
        
        date_trade_next_num = 1
        date_trade_next = date_trade_list[1]
        code_df_trade_list = []
        code_df_index_list = []
        
        for date_trade,date_index in zip(date_trade_list,date_index_list):
            #print('if前{}{}'.format(date_trade,date_trade_next))
            if date_trade == date_trade_list[-1]:#如果日期为最后一个
                code_df_trade = code_df.loc[date_trade:,:]
                code_df_index = code_df.loc[date_index:date_trade,:][:-1].copy()

            else:
                code_df_trade = code_df.loc[date_trade:date_trade_next,:][:-1].copy()#最后一行信号重叠
                code_df_index = code_df.loc[date_index:date_trade,:][:-1].copy()
                date_trade_next_num = min(date_trade_next_num + 1,len(date_trade_list)-1)#倒数第二个时候，date_trade_next的位置用到了最后一个
                date_trade_next = date_trade_list[date_trade_next_num]
            #print("if后{}{}".format(date_trade,date_trade_next))
            code_df_trade_list.append(code_df_trade)
            code_df_index_list.append(code_df_index)    
            
        self.code_df_trade_list = code_df_trade_list
        self.code_df_index_list = code_df_index_list

    def code_df_index_count(self):
        """计算分割数据指标：
        总收益率：'rate_total'
        最大回撤：'max_drawdown'
        """
        if not self.code_df_index_list:
            self.code_df_index_count_list = []
            return
        
        code_df_index_count_list = []   
        for df_one in self.code_df_index_list:
            df_new = df_one.copy()
            df_index = pd.DataFrame()
            #删除不用统计的列
            for col in ['signal','signal_position']:
                try:
                    df_new.drop(col,axis = 1,inplace = True)
                except:
                    pass

            #注意：下面程序删除了所有带空值的列
            df_new.dropna(axis = 1, inplace = True)
            df_index['rate_total'] = self.rate_total(df_new)
            df_index['max_drawdown'] = self.max_drawdown(df_new)
            code_df_index_count_list.append(df_index)
        self.code_df_index_count_list = code_df_index_count_list

    def rate_total(self,df):
        """给定df区间的收益率"""
        last_row = df.iloc[-1,:]
        first_row = df.iloc[0,:]
        rate_total_ser = (last_row - first_row)/first_row
        return rate_total_ser
    
    def max_drawdown(self,df):
        """给定df区间的最大回撤"""
        df_cummax = df.cummax()
        drawdown_df = (df - df_cummax)/df_cummax
        max_drawdown_ser = drawdown_df.min()
        return max_drawdown_ser 






class BackTestingEngine(DataManager):
    """
    """        
    def nav_ratio(self,df_list):
        """给分割的trade_df添加净值比率列"""
        ndf_list = []
        #单独处理第一个，只需要简单处理即可
        ndf = df_list[0].copy()
        ndf_part = ndf.drop(["signal","signal_position"],axis = 1)
        ndf['比率_累计净值今日/前日'] = \
            (ndf_part/ndf_part.shift(1)).apply(lambda x:x.mean(),axis = 1).fillna(1)
        
        ndf_list.append(ndf)
        ndf_part_last = ndf_part
        
        for df in df_list[1:]:
            ndf = df.copy()
            ndf_part = ndf.drop(["signal","signal_position"],axis = 1)
            ratio_df = ndf_part/ndf_part.shift(1) 
            for col in ndf_part.columns:
                if col in ndf_part_last.columns:
                    ratio_df[col][0] = ndf_part[col][0]/ndf_part_last[col][-1]
            ratio_df.fillna(1)
            ndf['比率_累计净值今日/前日'] = \
                ratio_df.apply(lambda x:x.mean(),axis = 1).fillna(1)
            ndf_list.append(ndf)
            ndf_part_last = ndf_part
            
        return ndf_list
        
    def xirr(self,ser):
        """ser是series格式，日期为索引的现金流，
        本函数用于计算不规则投资的年华收益率"""
        ser_clean = ser[ser != 0]#剔除值为0的数值 
        if ser_clean.min() * ser_clean.max() >= 0:
            return np.nan#全为正或者负则数据错误
        
        ser_clean.index = (ser_clean.index - ser_clean.index.min()).days / 365.0#单笔投资时间转年
        result = np.nan
        try:#牛顿梯度方法，尝试计算出一个r，使得各期投资*（1+r）**（年）加和为0     
            result = optimize.newton(lambda r: (ser_clean / ((1 + r) ** ser_clean.index)).sum(), x0=0, rtol=1e-4)
        except (RuntimeError, OverflowError):#布伦特方法求解       
            result = optimize.brentq(lambda r: (ser_clean / ((1 + r) ** ser_clean.index)).sum(), a=-0.999999999999999, b=100, maxiter=10**4)
    
        if not isinstance(result, complex):#确定result不是复数
            return result
        else:
            return np.nan     
    
    def count_xirr(self,nav_df):
        """必要列：['定投_金额','定投_持仓基金市值']
        必要索引：时间索引"""
        xirr_list = [0]
        for date in nav_df.index[1:]:
            ser = nav_df['定投_金额'][:date]*(-1)
            pv = nav_df.loc[date,'定投_持仓基金市值'] - nav_df.loc[date,'定投_金额']
            ser[-1] = pv    
            xirr = self.xirr(ser) 
            days = (date - list(nav_df.index)[0]).days    
            xirr_list.append(xirr)
        nav_df['定投_年化收益率'] = xirr_list
        return nav_df
    
    def merge_strategy_data(self):
        """合并回测策略的数据"""
        merge_df = pd.DataFrame()
        fixed_money = 1000
        last_value = fixed_money
        for df in self.strategy_df_list:
            #df = strategy_df_list[0]
            df_part = df.loc[:,['signal','signal_position','比率_累计净值今日/前日']].copy()
            
            #所有的code合并在一起
            only_code_df = df.drop(['signal','signal_position', '比率_累计净值今日/前日'],axis = 1)
            code_dir = ''
            for col in only_code_df.columns:
                code_dir = code_dir + col +','
            code_dir = code_dir[:-1]
            df_part['code'] = code_dir
            
            #计算拆分区间内的定投数据
            df_part_idst = list(df_part[df_part['signal'] ==1].index)#调仓区间内的定投
            for date in df_part_idst:
                if date == df_part_idst[-1]:#如果日期为最后一个
                    df_part_split = df_part.loc[date:].copy()
                else:
                    date_next = df_part_idst[df_part_idst.index(date) + 1]
                    df_part_split  = df_part.loc[date:date_next][:-1].copy()
                df_part_split['定投_金额'] = fixed_money * df_part_split['signal']
                df_part_split['定投_持仓基金市值'] = df_part_split['比率_累计净值今日/前日'].cumprod()*last_value
                last_value = df_part_split['定投_持仓基金市值'][-1] + fixed_money
                merge_df = pd.concat([merge_df,df_part_split])
                   
        merge_df['累计净值'] = merge_df['比率_累计净值今日/前日'].cumprod()
        merge_df['定投_金额_累计'] = merge_df['定投_金额'].cumsum()
        merge_df['定投_持仓基金市值_最大回撤_金额'] = \
            merge_df['定投_持仓基金市值'] - merge_df['定投_持仓基金市值'].cummax()
        merge_df['定投_持仓基金市值_最大回撤_比率'] = \
            merge_df['定投_持仓基金市值_最大回撤_金额']/merge_df['定投_持仓基金市值'].cummax()
        merge_df['定投_累计收益率'] = merge_df['定投_持仓基金市值']/merge_df['定投_金额_累计'] -1
        merge_df['定投_累计收益率_最大回撤_比率'] = \
            (merge_df['定投_累计收益率'] + 1)/(merge_df['定投_累计收益率'].cummax() + 1) - 1
        merge_df = self.count_xirr(merge_df)
        self.merge_df = merge_df
    

class RateStrategy(BackTestingEngine):
    """exapmple"""
    def __init__(self,start_date,end_date,code=None,interval = 'quarter_first',**kw):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.init_kw(kw)
        self.init_engine()
        
        self.init_kw_add(kw)
        self.strategy()
        self.merge_strategy_data()
    
    def init_kw_add(self,kw):
        """在这里添加策略专属参数"""
        for k,v in kw.items():
            if k == 'fund_num':
                self.fund_num = v
            elif k == 'rate_limit':
                self.rate_limit = v
                
    def strategy(self):
        """给定筛选好的df列表，计算回测"""
        if not self.code_df_index_count_list:
            strategy_df_list = self.code_df_trade_list
            self.strategy_df_list = self.nav_ratio(strategy_df_list)
            return
        
        strategy_df_list = []
        for trade_df,index_count_df in zip(self.code_df_trade_list,self.code_df_index_count_list):
            index_count_df_new = index_count_df.copy()
            #设定筛选条件
            index_count_df_new.sort_values('rate_total',ascending = False,inplace = True)
            index_count_df_new.dropna(inplace = True)
            select_df = index_count_df_new.iloc[:self.fund_num,:].copy()
            select_code_list = list(select_df.index)
            select_code_list.extend(['signal','signal_position'])
            #筛选数据
            strategy_df = trade_df.loc[:,select_code_list]
            strategy_df_list.append(strategy_df)
        strategy_df_list = self.nav_ratio(strategy_df_list)
        self.strategy_df_list = strategy_df_list
                




                
    







