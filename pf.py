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
from libraries.amps_analytics import AMPSChart, AMPSDataProvider
from libraries.prism_vested_analytics import ClaimPrismFarmChart

ydp = DataProvider('yLuna')
pdp = DataProvider('pLuna')

st.set_page_config(page_title="Prism Farm - Analytics",\
        page_icon=Image.open(requests.get('https://raw.githubusercontent.com/IncioMan/prism_forge/master/images/xPRISM.png',stream=True).raw),\
        layout='wide')

###

@st.cache(ttl=30000, show_spinner=False, allow_output_mutation=True)
def claim(claim_hash, cols_claim=[]):
    df_claim = pd.read_json(
        f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
        convert_dates=["BLOCK_TIMESTAMP"],
    )
    return df_claim

@st.cache(ttl=30000, show_spinner=False, allow_output_mutation=True)
def get_url(url):
    return pd.read_csv(url, index_col=0)
    
cp = ChartProvider()
pe_cp = PrismEmittedChartProvider()
amps_cp = AMPSChart()
prism_farm_claim_cp = ClaimPrismFarmChart()

@st.cache(ttl=30000, show_spinner=False, allow_output_mutation=True)
def get_data():
    url = 'https://raw.githubusercontent.com/IncioMan/prism_analytics/main/data/processed/{}.csv'
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    pe_dp_prism_emitted = pd.read_csv(url.format('prism_emitted'), index_col=0)
    pe_dp_prism_emitted_so_far = pd.read_csv(url.format('prism_emitted_so_far'), index_col=0)
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    pe_dp_dates_to_mark = pd.read_csv(url.format('pe_dp_dates_to_mark'), index_col=0)
    pe_dp_extra_dates_to_mark = pd.read_csv(url.format('extra_dates_to_mark'), index_col=0)
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    pdp_dates_to_mark = pd.read_csv(url.format('pdp_dates_to_mark'), index_col=0)
    pdp_asset_used = pd.read_csv(url.format('pdp_asset_used'), index_col=0)
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    pdp_asset_unused = pd.read_csv(url.format('pdp_asset_unused'), index_col=0)
    ydp_dates_to_mark = pd.read_csv(url.format('ydp_dates_to_mark'), index_col=0)
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    ydp_asset_used = pd.read_csv(url.format('ydp_asset_used'), index_col=0)
    ydp_asset_unused = pd.read_csv(url.format('ydp_asset_unused'), index_col=0)
    refract_dp_all_refreact = pd.read_csv(url.format('all_refreact'), index_col=0)
    xprism_amps_dp_perc_amps_n_user = pd.read_csv(url.format('perc_amps_n_user'), index_col=0)
    aprs_dp_aprs = pd.read_csv(url.format('aprs'), index_col=0)
    amps_dp_amps = pd.read_csv(url.format('amps'), index_col=0)
    amps_activity = pd.read_csv(url.format('amps_activity'), index_col=0)
    single_metrics = pd.read_csv(url.format('single_metrics'), index_col=0)
    prism_vested_claim = pd.read_csv(url.format('prism_vested_claim'), index_col=0)
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    farm_users = single_metrics.loc['farm_participants'].values[0]
    last_yluna_farm = single_metrics.loc['last_yluna_farm'].values[0]
    last_farm_apr = single_metrics.loc['last_farm_apr'].values[0]
    print("{} - Loading data...".format(str(datetime.datetime.now()).split('.')[0]), flush=True)
    boost_apr_median = single_metrics.loc['boost_apr_median'].values[0]
    up_to_today_emission = single_metrics.loc['up_to_today_emission'].values[0]
    print("{} - Data loaded".format(str(datetime.datetime.now()).split('.')[0]), flush=True)

    return pe_dp_prism_emitted, pe_dp_prism_emitted_so_far, pe_dp_dates_to_mark, pe_dp_extra_dates_to_mark,\
    pdp_dates_to_mark, pdp_asset_used, pdp_asset_unused, ydp_dates_to_mark,\
    ydp_asset_used, ydp_asset_unused, refract_dp_all_refreact, xprism_amps_dp_perc_amps_n_user,\
    aprs_dp_aprs, last_farm_apr, last_yluna_farm, up_to_today_emission, amps_dp_amps,\
            boost_apr_median, farm_users, amps_activity, prism_vested_claim
    

pe_dp_prism_emitted, pe_dp_prism_emitted_so_far, pe_dp_dates_to_mark, pe_dp_extra_dates_to_mark,\
pdp_dates_to_mark, pdp_asset_used, pdp_asset_unused, ydp_dates_to_mark,\
ydp_asset_used, ydp_asset_unused, all_refracts, perc_amps_n_user, aprs,\
    last_farm_apr, last_yluna_farm, up_to_today_emission, amps,\
        boost_apr_median, farm_users, amps_activity, prism_vested_claim = get_data()

###
###
all_deltas = ydp_asset_used.append(ydp_asset_unused)
all_deltas = ydp.fill_date_gaps(all_deltas, ['2022-02-11','2022-02-12','2022-02-13'])
c1 = cp.get_yluna_time_area_chart(all_deltas, 
               alt.Scale(scheme='set2'),
               min_date = all_deltas.Time.min(),
               max_date = all_deltas.Time.max(),
               top_padding = 1500000
        )

c2 = alt.Chart(ydp_dates_to_mark).mark_rule(color='#e45756').encode(
    x=alt.X('date'+':T')
)

c3 = alt.Chart(ydp_dates_to_mark).mark_text(
    color='#e45756',
    angle=0
).encode(
    x=alt.X('text_date'+':T',axis=alt.Axis(labels=True,title='')),
    y=alt.Y('height',axis=alt.Axis(labels=True,title='Amount')),
    text='text'
)

yluna_chart = (c1 + c2 + c3).properties(height=350).configure_view(strokeOpacity=0)

all_deltas = pdp_asset_used.append(pdp_asset_unused)
all_deltas = pdp.fill_date_gaps(all_deltas, ['2022-02-11','2022-02-12','2022-02-13'])
c1 = cp.get_yluna_time_area_chart(all_deltas, 
               alt.Scale(scheme='set2'),
               min_date = all_deltas.Time.min(),
               max_date = all_deltas.Time.max(),
               top_padding = 1500000
        )

c2 = alt.Chart(pdp_dates_to_mark).mark_rule(color='#e45756').encode(
    x=alt.X('date'+':T')
)

c3 = alt.Chart(pdp_dates_to_mark).mark_text(
    color='#e45756',
    angle=0
).encode(
    x=alt.X('text_date'+':T',axis=alt.Axis(labels=True,title='')),
    y=alt.Y('height',axis=alt.Axis(labels=True,title='Amount')),
    text='text'
)

pluna_chart = (c1 + c2 + c3).properties(height=350).configure_view(strokeOpacity=0)
perc_amps_chart = xPrismAmpsChart.chart(perc_amps_n_user)
aprs_chart = APRSChart.chart(aprs)
prism_emitted_chart = pe_cp.prism_emitted_chart(pe_dp_prism_emitted, pe_dp_prism_emitted_so_far, 
                       pe_dp_dates_to_mark, pe_dp_extra_dates_to_mark, '2022-05-25')
pf_claim_n_users_actions_total_chart =  prism_farm_claim_cp.n_users_actions_total(prism_vested_claim)
pf_claim_amount_actions_total_chart =  prism_farm_claim_cp.amount_actions_total(prism_vested_claim)
pf_claim_amount_actions_chart =  prism_farm_claim_cp.amount_actions(prism_vested_claim)
pf_claim_n_users_actions_chart =  prism_farm_claim_cp.n_users_actions(prism_vested_claim)

st.markdown(f"""
<div style=\"width: 100%; text-align: center\">
    <a href='https://prismprotocol.app/'><img src="https://raw.githubusercontent.com/IncioMan/prism_analytics/main/images/prism_white_small.png" width=\"35px\" style=\"margin-right:5px\"></a>
    <a href="https://flipsidecrypto.xyz"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/fc.png" width=\"30px\"></a>
    <a href="https://twitter.com/IncioMan"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/twitter.png" width=\"50px\"></a>
</div>
""", unsafe_allow_html=True)

st.text("")
st.text("")
st.text("")
st.text("")

col0,col1,col00,col2,col3,col4 = st.columns([0.1,1,0.25,0.75,0.75,0.25])
with col1:
    st.subheader('PRISM Farm')
    st.markdown("""Prism Farm allows you to stake yLUNA in the 
Prism Farm contract and receive $PRISM tokens in exchange for your yLUNA yield.
130m PRISM tokens (13% of the total supply) will be available in the Prism Farm
 event and will be farmed over a 12 month period. More info [here](https://prism-protocol.medium.com/prism-farm-is-launching-on-7th-march-f15c2f733671).""")
    st.markdown("""How many yLuna have been staked into the Farm? How many days are left in the event?
What is the current APR for participants?""")
with col2:
    st.text("")
    st.text("")
    st.text("")
    days_left = 365-(datetime.date.today() - datetime.date(2022, 3, 5)).days
    st.metric(label="Prism Farm APR", value=f"{round(last_farm_apr,2)}%")
    st.metric(label="Days Left in Prism Farm", value=f"{days_left}")
    st.metric(label="yLuna in Prism Farm", value=f"{last_yluna_farm}M")
with col3:
    st.text("")
    st.text("")
    st.text("")
    days_left = 365-(datetime.date.today() - datetime.date(2022, 3, 5)).days
    st.metric(label="Boost Median APR", value=f"{round(boost_apr_median,2)}%")
    st.metric(label="Prism Farm Participants", value=f"{int(farm_users)}")
    st.metric(label="Prisms emitted so far", value=f"{up_to_today_emission}%")

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('PRISM Farm Emission')
    st.markdown("""The 130m $PRISM tokens have been split into 2 pools, the Base Pool and the AMPS Boosted Pool. Initially 80% of the tokens will be allocated to the Base Pool and 20% of the tokens will be allocated to the AMPS Boosted Pool.""")
    st.markdown("""What percentage has already been allocated? And how close are we to the unlock of the vested PRISM?""")
with col2:
    st.altair_chart(prism_emitted_chart.properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col0,col1,col11,col2 = st.columns([0.1,1,1,1])
with col1:
    st.subheader('Prism Farm Claim Stats')
    st.markdown("""
    Prism tokens farmed in the Prism Farm event vest for 30 days before being claimable.
    In these charts we look at the total amount of Prism tokens claimed and users who have claimed
    and what actions they decided to perform. Prism can either be staked and/or pledged directly or simply
    claimed and possibly dumped or used to arbitrage the xPrism/Prism pair.
    """)
    st.markdown("""Has most of the claimed Prism been staked/pledged or simply claimed?""")
with col11:
    st.altair_chart(pf_claim_n_users_actions_total_chart.properties(height=350), use_container_width=True)
with col2:
    st.altair_chart(pf_claim_amount_actions_total_chart.properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

#------------PRISM CLAIM FARM ----------------

col0,col1,col2 = st.columns([2,1,0.1])
with col1:
    st.subheader('Users Claim Actions Over Time')
    st.markdown("""The trend of what action users have performed on every single day can indicate
    patterns relevant for the Prism tokenomics and users commitment to the project""")
    st.markdown("""Has the trend of users who have pledged their rewards been constant?""")
with col0:
    st.altair_chart(pf_claim_n_users_actions_chart.properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col0,col1, col2 = st.columns([2,1,0.1])
with col1:
    st.subheader('Amount of Prism Claimed Over Time')
    st.markdown("""
    The total amount of Prism for each claim action over time can also indicate patterns and can influence
    the overall price action of the Prism token.""")
    st.markdown("""What day has experienced the highest amount pledged? And only claimed? Does it coincide with 
    days where xPrism/Prism presented arb opportunities or where Prism price action has been negative?""")
with col0:
    st.altair_chart(pf_claim_amount_actions_chart.properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

#------------PRISM PLEDGE DAILY ----------------

col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('xPRISM Pledged Daily')
    st.markdown("""Every day users might pledge or unpledge their xPRISM. 
    This affects the overall amount of AMPs in circulation, as each unpledging resests AMPs and 
    new xPRISM pledge is more value committed into the protocol""")
    st.markdown("""Have we experienced days of high unpledging activity? And what about pledging, is it constant over time?""")
with col2:
    st.altair_chart(amps_cp.pledge_unpledge_daily(amps_activity).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('Users (un)pledging Daily')
    st.markdown("""Looking at the number of users performing pledging/unpledging operations might show some market sentiment.
    Indeed, some external events might lead many users to pledge/unpledge their xPRISM.""")
    st.markdown("""What are the days with most activity? What could be the cause for that?""")
with col2:
    st.altair_chart(amps_cp.number_users_pledging(amps_activity).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")


#------------BOOST APR ----------------

col1,col2, col0 = st.columns([2,1,0.1])
with col2:
    st.subheader('Boost APR')
    st.markdown("""
    AMPS allow to obtain a share of the 26M PRISMs allocated for these boosted rewards.
    The Boost APR is user specific as it depends on the amount of AMPS accumulated and yLUNA staked in the Prism Farm.
    Let's take a look at what Boosted APR do users get. 
    """)
    st.markdown("""What is the most common APR percentage? What is the higher Boost APR recorded?""")
with col1:
    st.altair_chart(amps_cp.users_boost_apr(amps).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")


col1,col2, col0 = st.columns([2,1,0.1])
with col2:
    st.subheader('Daily Rewards')
    st.markdown("""APR can be misleading, since it is expressed in comparison to the amount of value staked
    Let's now look at the actual amount of tokens users receive daily as result of their base + boost rewards. 
    """)
    st.markdown("""
        How many PRISM do users obtain daily? What is the highest amount recorded?
    """)
with col1:
    st.altair_chart(amps_cp.users_daily_rewards(amps).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")


col1,col2, col0 = st.columns([2,1,0.1])
with col2:
    st.subheader('Users Pledging')
    st.markdown("""Prism Farm rewards users which pledge their xPRISM and stake yLUNA. By pledging
    xPRISM users earn AMPs, a non-tradable token. AMPs accumulate as long as the user keeps its 
    xPRISM pledged and resets as soon as she unpledges.""")
    st.markdown("""What users have pledge the most xPRISM? How long have they been pledging for? Have they also staked many yLUNA?""")
with col1:
    st.altair_chart(amps_cp.time_xprism_yluna(amps).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col1,col2, col0 = st.columns([2,1,0.1])
with col2:
    st.subheader('Time Pledged')
    st.markdown("""
        AMPS create an incentive for users to keep their xPRISM pledged,
        since unpledging causes the amount of AMPS accumulated to reset. In this chart
        we look at the distribution of the number of users according to the amount of days 
        they have been pledging for. 
    """)
    st.markdown("""Have most users been pledging since day one? Can we observe many users who have just (re)pledged?""")
with col1:
    st.altair_chart(amps_cp.users_days_pledged(amps).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

#------------PRISM PLEDGE DAILY ----------------


col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('Amount xPRISM Pledged')
    st.markdown("""
    Users who have pledged xPRISM for long time have also accumulated AMPS as a result of it.
    If they were to unpledge their xPRISM, they would loose all their AMPs. This means that the longer users
    have pledged for, the stronger it is the incentive to keep pledging. In a sense, xPRISM which have been pledge
    for long time, are unlikely to be sold on the market in the near future.
    """)
    st.markdown("""
    How many xPRISM have been pledged since day 1?
    """)
with col2:
    st.altair_chart(amps_cp.xprisms_days_pledged(amps).properties(height=350), use_container_width=True)
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")


col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('xPRISM holdings pledged')
    st.markdown("""To align the Prism Farmers' incentives with the incentives of 
    long-term xPRISM holders, 
    Prism has  introduced the amplified yields, called AMPS.
     AMPS enable users to signal their commitment and deposit $xPRISM 
    tokens into a boosting vault.
Committing more xPRISM tokens and over a longer period of time 
will earn more AMPS and consequently earn even higher yields in PRISM 
Farm.""")
    st.markdown("""How much of their xPrism holdings have users committed to AMPs?""")
with col2:
    st.text("")
    st.text("")
    st.altair_chart(perc_amps_chart.properties(height=350), use_container_width=True)

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")


    

col1,col2, col0 = st.columns([2,1,0.1])
with col2:
    st.subheader('Staking APR')
    st.markdown("""Prism allows to stake yLuna in normal staking, or Prism Farm. The two strategies yield different APRs and depend on the price of Luna, yLuna and the Prism token. Rewards from normal staking can be claimed in various tokens while the ones from Prism Farm are paid in PRISM tokens.""")
    st.markdown("""What do the APRs from the different strategies look like over time? What is the most profitable one?""")
with col1:
    st.text("")
    st.altair_chart(aprs_chart.properties(height=350), use_container_width=True)

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col1,col2, col0 = st.columns([2,1,0.1])
with col2:
    st.subheader('Refraction')
    st.markdown("""In order to obtain yLuna and pLuna, users need to refract their Luna. 
    In practice, this means that the refracted Luna is staked with one of Prism associated validators and cLuna is generated. 
    cLuna can then be split in yLuna and pLuna. 
    cLuna can be also obtained from the cLuna/PRISM liquidity pool - this is convinient when it is trading at a premium in the pool.""")
    st.markdown("""How much Luna is refracted over time? 
    What where the days on which most Luna was refracted?
     And which ones saw a high number of Luna unrefracted?""")
with col1:
    st.text("")
    st.text("")
    st.altair_chart(cp.refraction_asset_time(all_refracts).properties(height=350), use_container_width=True)

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('yLUNA Usage')
    st.markdown("""yLuna entitles the owner to the staking rewards of the underlying Luna and the eventual airdrops.
Prism Farm is also a valid way to employ yLuna.
yLuna can be also used to provide liquidity to the yLuna/PRISM pool. The rewards of yLuna which is not staked goes 100% to xPRISM holders.""")
    st.markdown("""Where has yLuna been employed? 
    How much yLuna is sitting idle? 
    Has Prism Farm gained the largest share?""")
with col2:
    st.altair_chart(yluna_chart, use_container_width=True)

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

col0,col1, col2 = st.columns([0.1,1,2])
with col1:
    st.subheader('pLUNA Usage')
    st.markdown("""pLuna represents the principal component of the refracted Luna. 
    Currently, it can only be used as liquidity in the pLuna/PRISM pool, 
    but it will entitle the owner to several rights including the governance voting power in the near future.""")
    st.markdown("""Where is currently pLuna employed? 
    Is most of it sitting unsed in wallets? 
    How much is provided as liquidity in the pool?""")
with col2:
    st.altair_chart(pluna_chart, use_container_width=True)

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

st.markdown(f"""
<div style=\"width: 100%; text-align: center\">
    <a href='https://prismprotocol.app/'><img src="https://raw.githubusercontent.com/IncioMan/prism_analytics/main/images/prism_white_small.png" width=\"35px\" style=\"margin-right:5px\"></a>
    <a href="https://flipsidecrypto.xyz"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/fc.png" width=\"30px\"></a>
    <a href="https://twitter.com/IncioMan"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/twitter.png" width=\"50px\"></a>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    label[data-testid="stMetricLabel"] {
        text-align:center
    }
    header[data-testid='stHeader']{
        visibility: hidden
    }
    div[data-testid="stMetricValue"] {
        text-align:center
    }
    @media (min-width:640px) {
        .block-container {
            padding-left: 5rem;
            padding-right: 5rem;
        }
    }
    @media (min-width:800px) {
        .block-container {
            padding-left: 10rem;
            padding-right: 10rem;
        }
    }
    .block-container
    {
        padding-bottom: 0.01rem;
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.terminated {
    margin-left: 10px;
    width: 10px;
    height: 10px;
    display: inline-block;
    border: 1px solid red;
    background-color: red;
    border-radius: 100%;
    opacity: 0.8;
}

.idle {
    margin-left: 10px;
    width: 10px;
    height: 10px;
    display: inline-block;
    border: 1px solid grey;
    background-color: grey;
    border-radius: 100%;
    opacity: 0.8;
}

.blink_me {
    margin-left: 10px;
    animation: blinker 2s linear infinite;
    width: 10px;
    height: 10px;
    display: inline-block;
    border: 1px solid green;
    background-color: green;
    border-radius: 100%;
    }
    @keyframes blinker {
    50% {
        opacity: 0;
    }
}

@media (min-width:800px) {
    .css-12w0qpk {
        padding-left: 30px;
    }
}
</style>
""", unsafe_allow_html=True)
hide_streamlit_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}
                        </style>
                        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
