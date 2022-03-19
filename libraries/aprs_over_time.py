#!/usr/bin/env python
# coding: utf-8

# In[92]:


import pandas as pd
import altair as alt
import warnings
import requests
warnings.filterwarnings("ignore")
alt.renderers.set_embed_options(theme='light')
pd.set_option("display.max_colwidth", 400)
pd.set_option("display.max_rows", 400)


# In[93]:


def claim(claim_hash):
    df = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"])
    df.columns = [c.lower() for c in df.columns]
    return df


# In[138]:


class APRDataProvider:
    
    def __init__(self, claim):
        self.yluna_price = 'e49168df-26f3-4972-b8c2-309e34e41072'
        self.luna_price = '571e7540-b3cb-458f-82c3-43aae00feae7'
        self.claim = claim
        
    def load(self):
        yluna_price_df = self.claim(self.yluna_price)
        yluna_price_df.columns = [c.lower() for c in yluna_price_df.columns]
        luna_price_df = self.claim(self.luna_price)
        luna_price_df.columns = [c.lower() for c in luna_price_df.columns]
        luna_price_df = luna_price_df.rename(columns={'price':'luna_price'})
        self.yluna_price_df = yluna_price_df
        self.luna_price_df = luna_price_df
        
    def parse(self):
        yluna = self.yluna_price_df[self.yluna_price_df.offer_asset=='yLuna']
        prism = self.yluna_price_df[self.yluna_price_df.offer_asset=='PRISM']
        df = yluna.merge(prism, on='day', suffixes=['_yluna','_prism'])
        df['yluna_price'] = (1/df.belief_price_prism) / df.belief_price_yluna
        prices = df
        prices = prices.merge(self.luna_price_df, on='day')[['day','yluna_price','luna_price']]
        prices['day'] = prices['day'].apply(lambda x: x[:-13])
        self.prices = prices
        
        df = pd.DataFrame(requests.get('https://api.terra.dev/chart/staking-return/annualized').json())
        df['date'] = pd.to_datetime(df['datetime'], unit='ms')
        df = df[df['date'] > '2021-07-05 15:00:00']
        df['day'] = df.date.apply(str)
        df.value = df.value.apply(float).apply(lambda x: x*100)
        self.staking_apr = df
        self.staking_apr = self.staking_apr.rename(columns={'value':'apr'})
        self.staking_apr['day'] = self.staking_apr['day'].apply(lambda x: x[:-9])
        
        prices_apr = self.prices.merge(self.staking_apr, on='day')
        prices_apr['yluna_apr'] = prices_apr.apr * prices_apr.luna_price / prices_apr.yluna_price
        yluna_apr = prices_apr[['day','yluna_apr']]
        yluna_apr.columns = ['Day','APR (%)']
        yluna_apr['Asset'] = 'yLUNA'
        luna_apr = prices_apr[['day','apr']]
        luna_apr.columns = ['Day','APR (%)']
        luna_apr['Asset'] = 'LUNA'
        self.aprs = yluna_apr.append(luna_apr)


# In[142]:


class APRSChart:
    
    def chart(aprs):
        return alt.Chart(aprs).mark_line(point=True).encode(
                 x=alt.X('Day:T', sort=alt.EncodingSortField(order='ascending')),
                 y="APR (%):Q",
                color=alt.Color('Asset:N', 
                                scale=alt.Scale(scheme='set2'),
                                legend=alt.Legend(
                                        orient='top-right',
                                        padding=5,
                                        legendY=0,
                                        direction='vertical')),
                tooltip=[alt.Tooltip('Day:T', format='%Y-%m-%d'), 'Asset', 'APR (%)']
            ).properties(width=700).configure_axisX(
                labelAngle=0
            ).configure_view(strokeOpacity=0)

