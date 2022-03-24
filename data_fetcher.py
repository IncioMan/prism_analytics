import streamlit as st
import pandas as pd
import altair as alt
import requests
import datetime
from PIL import Image
from libraries.prism_analytics import DataProvider, ChartProvider, LPDataProvider, SwapsDataProvider, RefractDataProvider, CollectorDataProvider, YLunaStakingDataProvider
from libraries.prism_emitted import PrismEmittedChartProvider, PrismEmittedDataProvider
from libraries.xPrismAmps_from_urls import xPrismAmpsChart, xPrismAMPsDP
from libraries.aprs_over_time import APRSChart, APRDataProvider
from libraries.amps_analytics import AMPSDataProvider

def claim(claim_hash, cols_claim=[]):
    df_claim = pd.read_json(
        f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
        convert_dates=["BLOCK_TIMESTAMP"],
    )
    return df_claim

def get_url(url):
    return pd.read_csv(url, index_col=0)

print("Starting...")
ystake_dp = YLunaStakingDataProvider(claim,get_url,'./data')
refract_dp = RefractDataProvider(claim,get_url,'./data')
swaps_dp = SwapsDataProvider(claim,get_url,'./data')
lp_dp = LPDataProvider(claim,get_url,'./data')
collector_dp = CollectorDataProvider(claim,get_url,'./data')
xprism_amps_dp = xPrismAMPsDP(claim)
aprs_dp = APRDataProvider(claim)
amps_dp = AMPSDataProvider('https://raw.githubusercontent.com/IncioMan/prism_analytics/main/data/amps/amps_{}.csv')
ydp = DataProvider('yLuna')
pdp = DataProvider('pLuna')
pe_dp = PrismEmittedDataProvider()


print("{} - Loading data: ystake_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
ystake_dp.load()
print("{} - Loading data: refract_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
refract_dp.load()
print("{} - Loading data: swaps_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
swaps_dp.load()
print("{} - Loading data: lp_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
lp_dp.load()
print("{} - Loading data: collector_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
collector_dp.load()
print("{} - Loading data: xprism_amps_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
xprism_amps_dp.load()
print("{} - Loading data: aprs_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
aprs_dp.load()
print("{} - Loading data: amps_dp...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
amps_dp.load()
print("{} - Data Loaded...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)


print("{} - Parsing data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True) 
ystake_dp.parse()
refract_dp.parse()
swaps_dp.parse()
lp_dp.parse()
collector_dp.parse(lp_dp.withdraw_, lp_dp.provide_, swaps_dp.swaps_df_all)
xprism_amps_dp.parse()
aprs_dp.parse(ystake_dp.ystaking_farm_df)
amps_dp.parse()
print("{} - Data parsed...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)

ydp.lp_delta(lp_dp.withdraw_[lp_dp.withdraw_.asset=='yLuna'],
        lp_dp.provide_[lp_dp.provide_.asset=='yLuna'], 
        swaps_dp.yluna_swaps, collector_dp.collector_pyluna[collector_dp.collector_pyluna.asset=='yLuna'])
ydp.stk_delta(ystake_dp.ystaking_df)
ydp.stk_farm_delta(ystake_dp.ystaking_farm_df)
ydp.refact_delta(refract_dp.all_refreact)
ydp.all_delta()
ydp.all_deltas = ydp.fill_date_gaps(ydp.all_deltas)
ydp.unused_asset(ydp.all_deltas)

pdp.lp_delta(lp_dp.withdraw_[lp_dp.withdraw_.asset=='pLuna'],
        lp_dp.provide_[lp_dp.provide_.asset=='pLuna'], 
        swaps_dp.yluna_swaps, collector_dp.collector_pyluna[collector_dp.collector_pyluna.asset=='pLuna'])
pdp.refact_delta(refract_dp.all_refreact)
pdp.all_delta()
pdp.all_deltas = pdp.fill_date_gaps(pdp.all_deltas)
pdp.unused_asset(pdp.all_deltas)

last_farm_apr = aprs_dp.last_yluna_farm
df = ydp.daily_delta_stk_farm
last_yluna_farm= round(df[(df.Time==df.Time.max())\
        &(df['Type']=='yLuna Farm staked')]\
        ['Amount'].values[0]/1000000,2)

pe_dp.prism_emitted.to_csv('./data/processed/prism_emitted.csv')
pe_dp.prism_emitted_so_far.to_csv('./data/processed/prism_emitted_so_far.csv')
pe_dp.dates_to_mark.to_csv('./data/processed/pe_dp_dates_to_mark.csv')
pe_dp.extra_dates_to_mark.to_csv('./data/processed/extra_dates_to_mark.csv')
pdp.dates_to_mark.to_csv('./data/processed/pdp_dates_to_mark.csv')
pdp.asset_used.to_csv('./data/processed/pdp_asset_used.csv')
pdp.asset_unused.to_csv('./data/processed/pdp_asset_unused.csv')
ydp.dates_to_mark.to_csv('./data/processed/ydp_dates_to_mark.csv')
ydp.asset_used.to_csv('./data/processed/ydp_asset_used.csv')
ydp.asset_unused.to_csv('./data/processed/ydp_asset_unused.csv') 
refract_dp.all_refreact.to_csv('./data/processed/all_refreact.csv')
xprism_amps_dp.perc_amps_n_user.to_csv('./data/processed/perc_amps_n_user.csv')
aprs_dp.aprs.to_csv('./data/processed/aprs.csv') 
amps_dp.amps.to_csv('./data/processed/amps.csv')

pd.Series([ystake_dp.ystaking_farm_df.sender.nunique(),
            last_yluna_farm, last_farm_apr,
            amps_dp.boost_apr_median,
            pe_dp.up_to_today_emission
        ],index=['farm_participants','last_yluna_farm',
        'last_farm_apr','boost_apr_median','up_to_today_emission']).to_csv('./data/processed/single_metrics.csv')




        