#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import altair as alt
import warnings
import numpy as np
import requests
import datetime
warnings.filterwarnings("ignore")
alt.renderers.set_embed_options(theme='dark')
pd.set_option("display.max_colwidth", 400)
pd.set_option("display.max_rows", 400)


# In[88]:


class AMPSDataProvider:
    def __init__(self, path='../data/amps'):
        self.path = path
        self.amps = None
        self.boost_apr_median = None
        pass
        
    def load(self):
        today = datetime.datetime.today().date()
        df = None
        for i in range(100):
            date = today-datetime.timedelta(days=int(i))
            date = date.strftime("%Y%m%d")
            #https://raw.githubusercontent.com/IncioMan/prism_analytics/main/data/amps_20220322.csv
            file_name = f'{self.path}/amps_{date}.csv'
            try:
                df = pd.read_csv(file_name).drop(columns=['Unnamed: 0'])
                print(f'File found: {file_name}')
                break
            except:
                print(f'File not found: {file_name}')
        df.columns = [c.lower() for c in df.columns]
        self.amps = df
        self.boost_apr_median =  df[df.boost_apr>0].boost_apr.median()
        
    def parse(self):
        df = self.amps
        df = df[~df.addr.isna()]
        df['boost_accrual_start_date'] = pd.to_datetime(df['boost_accrual_start_time'], unit='s')
        df['boost_accrual_start_time_days'] = df['boost_accrual_start_date'].apply(lambda x: pd.Timestamp.today() - x)
        df['boost_accrual_start_time_days'] = df['boost_accrual_start_time_days'].dt.days
        df['boost_accrual_start_time_days'] = df['boost_accrual_start_time_days'].apply(lambda x: 0 if x >  400 else x)
        df['boost_accrual_start_time_days_int'] = df['boost_accrual_start_time_days'].fillna(0).apply(int)
        df['user_yluna'] = df.user_yluna.apply(lambda x: round(x,2))
        df['user_xprism'] = df.user_xprism.apply(lambda x: round(x,2))
        self.amps = df
        


# In[89]:


class AMPSChart:
    
    def __init__(self):
        self.cols_dict = {
            'user_xprism': 'Amount of xPRISM ',
            'user_xprism_label': 'Amount of xPRISM',
            'boost_accrual_start_time_days_int': 'Number of days pledged for',
            'index': 'Number of users',
            'boost_accrual_start_time_days': 'Current number of days pledged for',
            'user_yluna': 'Amount of yLUNA',
            'addr': 'User address',
            'current_daily_rewards': 'Current daily rewards (PRISM)',
            'n_addr': 'Number of users',
            'boost_apr': 'Boost APR (%)'
        }
    def current_daily_rewards_cat(self, x):
        if x<1:
            return '1'
        if x < 100:
            v = (int(x/10)+1)*10
            return f'{v-9}-{v}'
        if x < 1000:
            v = (int(x/100)+1)*100
            return f'{v-99}-{v}'
        if x>=1000:
            return '> 1000'

    def time_xprism_yluna(self, df):
        cols_dict = self.cols_dict
        df['url'] = 'https://finder.extraterrestrial.money/mainnet/address/'+df['addr']
        if(len(df)>5000):
            df = df.sample(n=5000, random_state=1)
        else:
            df = df
        df2 = df.rename(columns=cols_dict)
        chart =alt.Chart(df2).mark_point(opacity=1, filled=True).encode(
            y=alt.Y(cols_dict['user_xprism']+":Q"),
            x=alt.X(cols_dict['boost_accrual_start_time_days']+":Q"),
            href='url:N',
            color=alt.Color(cols_dict['user_yluna'],
                scale=alt.Scale(scheme='redpurple', domain=[0,df2[cols_dict['user_yluna']].max()/5]),
                legend=alt.Legend(
                            orient='top-left',
                            padding=0,
                            legendY=0,
                            direction='vertical')),
            tooltip=[cols_dict['addr'],cols_dict['user_xprism'],cols_dict['user_yluna'],
                     cols_dict['boost_accrual_start_time_days']]
        ).configure_view(strokeOpacity=0).interactive()
        return chart.properties(width=600)
    
    def users_daily_rewards(self, df):
        cols_dict = self.cols_dict
        s = ['1']
        for i in range(1,11):
            v = i*10
            s.append(f'{v-9}-{v}')
        for i in range(2,11):
            v = i*100
            s.append(f'{v-99}-{v}')
        s.append('>1000')
        df2 = df.copy()
        df2['current_daily_rewards'] = df2['current_daily_rewards'].apply(lambda x: 1 if int(x/10)*10 == 0 else int(x/10)*10)
        df2['current_daily_rewards'] = df2.current_daily_rewards.apply(self.current_daily_rewards_cat)
        #print(df2.current_daily_rewards.value_counts())
        df2['n_addr'] = df2['addr']
        df2 = df2.groupby('current_daily_rewards').n_addr.count().reset_index()
        df2 = df2.rename(columns=cols_dict)
        chart = alt.Chart(df2).mark_bar().encode(
            x=alt.X(cols_dict['current_daily_rewards']+':N', \
                    sort=s,\
                    axis=alt.Axis(tickCount=10, labelAngle=-30, tickBand = 'center')),
            y=cols_dict['n_addr']+':Q',
            tooltip=[cols_dict['current_daily_rewards'],cols_dict['n_addr']+':Q']
        ).configure_mark(
            color='#DAFD91'
        ).configure_view(strokeOpacity=0)
        return chart.properties(width=600)
    
    def users_boost_apr(self, df):
        cols_dict = self.cols_dict
        df2 = df.copy().fillna(0)
        df2['boost_apr'] = df2['boost_apr'].apply(lambda x: 0 if int(x/10)*10 == 0 else int(x/10)*10)
        df2 = df2[df2['boost_apr']>0]
        df2['n_addr'] = df2['addr']
        df2 = df2.groupby('boost_apr').n_addr.count().reset_index()
        df2 = df2.rename(columns=cols_dict)
        chart = alt.Chart(df2).mark_bar().encode(
            x=alt.X(cols_dict['boost_apr']+':N', \
                    axis=alt.Axis(tickCount=10, labelAngle=-90, tickBand = 'center')),
            y=cols_dict['n_addr']+':Q',
            tooltip=[cols_dict['boost_apr'],cols_dict['n_addr']+':Q']
        ).configure_mark(
            color='#ccf4ed'
        ).configure_view(strokeOpacity=0)
        return chart.properties(width=600)
    
    def users_days_pledged(self,df):
        cols_dict = self.cols_dict
        df2 = df.boost_accrual_start_time_days.apply(int).value_counts().reset_index()
        df2.columns = ['Current number of days pledged for','Number of users']
        chart = alt.Chart(df2).mark_bar().encode(
            x=alt.X('Current number of days pledged for'+':N', \
                    scale=alt.Scale(domain=list(range(df2['Current number of days pledged for'].max()+1))),\
                    axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y='Number of users'+":Q",
            tooltip=['Current number of days pledged for','Number of users'+":Q"]
        ).configure_mark(
            color='#DAFD91'
        ).configure_view(strokeOpacity=0)
        return chart.properties(width=600)
    
    def xprisms_days_pledged(self,df):
        cols_dict = self.cols_dict
        df2 = df.groupby('boost_accrual_start_time_days_int').user_xprism.sum().reset_index()
        df2 = df2.rename(columns=cols_dict)
        df2[cols_dict['user_xprism_label']] = df2[cols_dict['user_xprism']].apply(lambda x: str(round(x/1000000,2))+'M')
        chart = alt.Chart(df2).mark_bar().encode(
            x=alt.X(cols_dict['boost_accrual_start_time_days_int']+':N', \
                    scale=alt.Scale(domain=list(range(df2[cols_dict['boost_accrual_start_time_days_int']].max()+1))),\
                    axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y=cols_dict['user_xprism']+':Q',
            tooltip=[cols_dict['boost_accrual_start_time_days_int'],cols_dict['user_xprism_label']+':N']
        ).configure_mark(
            color='#ccf4ed'
        ).configure_view(strokeOpacity=0)
        return chart.properties(width=600)
