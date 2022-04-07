#!/usr/bin/env python
# coding: utf-8

# In[226]:


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


# In[227]:


    def __init__(self, claim, path='../data'):
        self.path = path
        self.claim = claim
        self.prism_claim = '3622a25b-bce9-4d69-8153-3681d2fd1c6a'
        pass
        
    def load(self):
        self.actions = {
                'Prism':'Claim',
                'Xprism': 'Claim and Stake',
                'Amps':'Claim and Stake and Pledge'
            }
        if(self.prism_claim):
            self.prism_claim_df = self.claim(self.prism_claim)
        if(len(self.prism_claim_df.columns) == 0):
            self.prism_claim_df = pd.DataFrame([
                    ['2022-03-11 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs5vs',
                     'Prism',2000000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                    ['2022-03-11 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs3vs',
                     'xPrism',3000000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                    ['2022-03-11 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs4vs',
                     'xPrism',4000000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                    ['2022-03-12 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs5vs',
                     'AMPS',2000000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                    ['2022-03-12 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs5vs',
                     'Prism',1000000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                    ['2022-03-12 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs5vs',
                     'AMPS',500000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                    ['2022-03-12 17:45:27.509','terra1persuahr6f8fm6nyup0xjc7aveaur89nwgs6vs',
                     'xPrism',12000000000,'4E8269A29F8FCA39742D30171DDEF4F70D470553521A268A7BAA150E80FED333'],
                ], columns=['block_timestamp','user','action','amount','tx_id'])
        
    def parse(self):
        df = self.prism_claim_df
        df.amount = df.amount
        df.block_timestamp=df.block_timestamp.apply(str).apply(lambda x: x[:-4] if len(x) == 23 else x)
        df.block_timestamp=df.block_timestamp.apply(str).apply(lambda x: x[:-3] if len(x) == 22 else x)
        df.block_timestamp=df.block_timestamp.apply(str).apply(lambda x: x[:-7] if len(x) == 26 else x)
        df['hr'] = df.block_timestamp.str[:-5] + '00:00.000'
        df['day'] = df.block_timestamp.str[:-9]
        df.action = df.action.map(self.actions)
        self.prism_claim_df = df
        


# In[228]:


def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df


# In[307]:


class ClaimPrismFarmChart:
    
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
        self.domain = ['Claim','Claim and Stake','Claim and Stake and Pledge']
        self.range=['#ccf4ed','#dafd91','#fbb7bd']
        
    def amount_actions_total(self, prism_claim_df):
        df = prism_claim_df
        #df = ((dp.prism_claim_df.groupby('action').amount.sum()/dp.prism_claim_df.amount.sum()).apply(lambda x: round(x,2))*100).reset_index()
        df = (dp.prism_claim_df.groupby('action').amount.sum().apply(lambda x: round(x,2))).reset_index()
        df.columns = ['Claim Action','Amount of PRISM']
        df['Amount of PRISM (k)'] = df['Amount of PRISM'].apply(lambda x: str(round(x/1000,2))+'k')
        chart = alt.Chart(df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="Amount of PRISM", type="quantitative"),
            color=alt.Color(field="Claim Action", type="nominal",
                    #sort=['MARS & UST','MARS','UST'],
                    scale=alt.Scale(domain=self.domain, range=self.range),
                    legend=alt.Legend(
                    orient='none',
                    padding=10,
                    legendY=-10,
                    direction='vertical')),
            tooltip=['Claim Action','Amount of PRISM (k)']
        ).configure_view(strokeOpacity=0)
        return chart
   
    def n_users_actions(self, prism_claim_df):
        df = prism_claim_df.groupby(['action','day']).user.nunique().reset_index()
        n_data = 20
        if df.day.nunique() < n_data:
            extra_data = []
            for i in range(n_data-df.day.nunique()):
                extra_data.append(['Claim',(pd.to_datetime(df.day.max())+datetime.timedelta(days=i)).strftime("%Y-%m-%d"),0])
            df2 = df.append(pd.DataFrame(extra_data, columns=df.columns))
        else:
            df2 = df
        df2.columns = ['Claim Action','Day','Number of users']
        chart = alt.Chart(df2).mark_bar().encode(
            x=alt.X('Day:T', sort=alt.EncodingSortField(order='ascending')),
            y="Number of users:Q",
            color=alt.Color('Claim Action', 
                            #scale=alt.Scale(scheme='set2'),
                            scale=alt.Scale(domain=self.domain, range=self.range),
                            legend=alt.Legend(
                                    orient='top-right',
                                    padding=5,
                                    legendY=0,
                                    direction='vertical'))
            ,tooltip=[alt.Tooltip('Day:T', format='%Y-%m-%d %H:%M'), 'Claim Action', 'Number of users']
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0)
        return chart
    
    def n_users_actions_total(self, prism_claim_df):
        df = prism_claim_df
        #df = ((dp.prism_claim_df.groupby('action').user.nunique()/dp.prism_claim_df.user.nunique()).apply(lambda x: round(x,2))*100).reset_index()
        df = (dp.prism_claim_df.groupby('action').user.nunique()).reset_index()
        df.columns = ['Claim Action','Number of users']
        df['Number of users'] = df['Number of users'].apply(lambda x: round(x,2))
        chart = alt.Chart(df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="Number of users", type="quantitative"),
            color=alt.Color(field="Claim Action", type="nominal",
                    #sort=['MARS & UST','MARS','UST'],
                    scale=alt.Scale(domain=self.domain, range=self.range),
                    legend=alt.Legend(
                    orient='none',
                    padding=10,
                    legendY=-10,
                    direction='vertical')),
            tooltip=['Claim Action','Number of users']
        ).configure_view(strokeOpacity=0)
        return chart
    
    def amount_actions(self, prism_claim_df):
        df = prism_claim_df.groupby(['action','day']).amount.sum().reset_index()
        n_data = 20
        if df.day.nunique() < n_data:
            extra_data = []
            for i in range(n_data-df.day.nunique()):
                extra_data.append(['Claim',(pd.to_datetime(df.day.max())+datetime.timedelta(days=i)).strftime("%Y-%m-%d"),0])
            df2 = df.append(pd.DataFrame(extra_data, columns=df.columns))
        else:
            df2 = df
        df2.columns = ['Claim Action','Day','Amount']
        df2['Amount of PRISM (k)'] = df2['Amount'].apply(lambda x: str(round(x/1000,2))+'k')
        chart = alt.Chart(df2).mark_bar().encode(
            x=alt.X('Day:T', sort=alt.EncodingSortField(order='ascending')),
            y="Amount:Q",
            color=alt.Color('Claim Action', 
                            scale=alt.Scale(domain=self.domain, range=self.range),
                            legend=alt.Legend(
                                    orient='top-right',
                                    padding=5,
                                    legendY=0,
                                    direction='vertical'))
            ,tooltip=[alt.Tooltip('Day:T', format='%Y-%m-%d %H:%M'),'Claim Action', 'Amount of PRISM (k)']
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0)
        return chart