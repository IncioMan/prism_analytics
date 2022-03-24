from audioop import add
import base64
import json
import requests
import pandas as pd
import datetime
from multiprocessing.dummy import Pool as ThreadPool 


def get_prices():
    """
    Parse json data from ET into a DataFrame
    """

    url = "https://api.extraterrestrial.money/v1/api/prices"

    response = requests.get(url).json()

    df = pd.json_normalize(pd.DataFrame.from_dict(response)["prices"]).set_index(
        "symbol"
    )

    luna_price = df.loc["LUNA", "price"]
    yluna_price = df.loc["yLUNA", "price"]
    prism_price = df.loc["PRISM", "price"]
    xprism_price = df.loc["xPRISM", "price"]

    return luna_price, yluna_price, prism_price, xprism_price


def get_oracle_rewards(luna_price):

    # oracle address
    response = requests.get(
        " https://lcd.terra.dev/bank/balances/terra1jgp27m8fykex4e4jtt0l7ze8q528ux2lh4zh0f",
    ).json()

    # convert to dataframe
    df = pd.DataFrame.from_dict(response["result"]).set_index("denom")

    # parse for ust and luna rewards
    ust_rewards = int(df.loc["uusd", "amount"]) / 1e6
    luna_rewards = int(df.loc["uluna", "amount"]) / 1e6

    # add ust and value of luna
    oracle_rewards = ust_rewards + luna_rewards * luna_price

    return oracle_rewards



def get_staked_luna():

    # staking pool
    response = requests.get(
        " https://lcd.terra.dev/cosmos/staking/v1beta1/pool",
    ).json()

    # convert to dataframe
    df = pd.DataFrame.from_dict(response)

    # parse number of staked luna
    staked_luna = round(int(df.loc["bonded_tokens", "pool"]) / 1e6, -6)

    return staked_luna



def get_staking_yield(luna_price, staked_luna):

    # amount of oracle rewards in UST
    oracle_rewards = get_oracle_rewards(luna_price)

    avg_validator_commission = 0.05

    # oracle rewards paid over two years, distributed to staked luna, divided my current luna price, minus validator commissions
    staking_yield = (
        oracle_rewards / 2 / staked_luna / luna_price * (1 - avg_validator_commission)
    )

    return staking_yield


def dict_to_b64(data: dict) -> str:
    """Converts dict to ASCII-encoded base64 encoded string."""
    return base64.b64encode(bytes(json.dumps(data), "ascii")).decode()


# query xPRISM balance in AMPS vault

def get_amps_vault_xprism():

    query_message = dict_to_b64(
        {"balance": {"address": "terra1pa4amk66q8punljptzmmftf6ylq3ezyzx6kl9m"}}
    )

    response = requests.get(
        f"https://lcd.terra.dev/terra/wasm/v1beta1/contracts/terra1042wzrwg2uk6jqxjm34ysqquyr9esdgm5qyswz/store?query_msg={query_message}",
    ).json()

    xprism_balance = float(response["query_result"]["balance"]) / 1e6

    return xprism_balance


# query user's pledged pledged xPRISM

def get_user_amps(user_address):

    query_message = dict_to_b64({"get_boost": {"user": user_address}})

    response = requests.get(
        f"https://lcd.terra.dev/terra/wasm/v1beta1/contracts/terra1pa4amk66q8punljptzmmftf6ylq3ezyzx6kl9m/store?query_msg={query_message}",
    ).json()

    user_xprism = float(response["query_result"]["amt_bonded"]) / 1e6
    user_amps = float(response["query_result"]["total_boost"]) / 1e6
    boost_accrual_start_time = float(response["query_result"]["boost_accrual_start_time"])
    boost_accrual_last_updated = float(response["query_result"]["last_updated"])

    return user_xprism, user_amps, boost_accrual_start_time, boost_accrual_last_updated


# query user's AMPS amount

def get_user_prism_farm(user_address):

    query_message = dict_to_b64({"reward_info": {"staker_addr": user_address}})

    response = requests.get(
        f"https://lcd.terra.dev/terra/wasm/v1beta1/contracts/terra1ns5nsvtdxu53dwdthy3yxs6x3w2hf3fclhzllc/store?query_msg={query_message}",
    ).json()


    user_yluna = float(response["query_result"]["bond_amount"]) / 1e6
    user_weight = float(response["query_result"]["boost_weight"]) / 1e6
    active_boost = float(response["query_result"]["active_boost"])
    pending_reward = float(response["query_result"]["pending_reward"])

    return user_yluna, user_weight, active_boost, pending_reward


# query amount of yLUNA in PRISM Farm

def get_yluna_staked():

    query_message = dict_to_b64(
        {"reward_info": {"staker_addr": "terra1ns5nsvtdxu53dwdthy3yxs6x3w2hf3fclhzllc"}}
    )

    response = requests.get(
        f"https://lcd.terra.dev/terra/wasm/v1beta1/contracts/terra1p7jp8vlt57cf8qwazjg58qngwvarmszsamzaru/store?query_msg={query_message}",
    ).json()

    yluna_staked = float(response["query_result"]["staked_amount"]) / 1e6

    return yluna_staked


# query user's AMPS weight

def get_total_boost_weight():

    query_message = dict_to_b64({"distribution_status": {}})

    response = requests.get(
        f"https://lcd.terra.dev/terra/wasm/v1beta1/contracts/terra1ns5nsvtdxu53dwdthy3yxs6x3w2hf3fclhzllc/store?query_msg={query_message}",
    ).json()

    total_boost_weight = float(response["query_result"]["boost"]["total_weight"]) / 1e6

    return total_boost_weight

df_claim = pd.read_json(
            "https://api.flipsidecrypto.com/api/v2/queries/ad513cbc-7e40-4bd0-a115-31e9b95459a1/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"],
        )

# initial parameters
luna_price, yluna_price, prism_price, xprism_price = get_prices()
staked_luna = get_staked_luna()
staking_yield = get_staking_yield(luna_price, staked_luna) * 100
yluna_yield = (luna_price / yluna_price) * staking_yield

# pool parameters
total_rewards = 130_000_000
ratio = 0.8
base_rewards = total_rewards * ratio
boost_rewards = total_rewards * (1 - ratio)

# protocol queries
xprism_pledged = get_amps_vault_xprism()
total_boost_weight = get_total_boost_weight()
yluna_staked = get_yluna_staked()
total_amps = total_boost_weight**2 / yluna_staked

today = datetime.datetime.now().strftime("%Y%m%d")
today_str = datetime.datetime.now().strftime("%Y-%m-%d")
def get_amps_data(user_address):
    # user queries
    try:
        user_xprism, user_amps, \
        boost_accrual_start_time, boost_accrual_last_updated = get_user_amps(user_address)
        user_yluna, user_weight, active_boost, pending_reward = get_user_prism_farm(user_address)
    except Exception as e:
        print(e)
        print(f'Error obtaining data for {user_address}')
        today = datetime.datetime.now().strftime("%Y%m%d")
        with open(f"data/amps/errors_{today}.txt", "a") as errorfile:
            errorfile.write(user_address + "\n")
        return None
    current_position_size = (user_yluna * yluna_price) + (user_xprism * xprism_price)

    # intial rewards
    base_rewards = 104_000_000 * user_yluna / yluna_staked
    base_apr = (base_rewards * prism_price) / (user_yluna * yluna_price) * 100
    boost_rewards = 26_000_000 * user_weight / total_boost_weight
    boost_apr = (boost_rewards * prism_price) / (user_yluna * yluna_price) * 100
    total_apr = base_apr + boost_apr
    current_daily_rewards = (base_rewards + boost_rewards) * prism_price / 365

    return (today_str, user_address, user_xprism, user_amps, user_yluna, user_weight, base_apr, 
    boost_apr, total_apr, current_daily_rewards, current_position_size, yluna_price, prism_price,
    yluna_staked, total_boost_weight, boost_accrual_start_time, boost_accrual_last_updated,
    active_boost, pending_reward)

cols = ['date', 'addr', 'user_xprism', 'user_amps', 'user_yluna', 'user_weight', 'base_apr', 
    'boost_apr', 'total_apr', 'current_daily_rewards', 'current_position_size', 'yluna_price', 'prism_price',
    'yluna_staked', 'total_boost_weight', 'boost_accrual_start_time', 'boost_accrual_last_updated',
    'active_boost', 'pending_reward']
# sidebar assumptions
i = 1
data = []
print(len(df_claim))
pool = ThreadPool(4)  # Make the Pool of workers
addresses = []
for _, user_address in df_claim['USER_ADDR'].iteritems():
    addresses.append(user_address) 
    if(i%100==0):
        pool = ThreadPool(4)  # Make the Pool of workers
        print(f"{str(datetime.datetime.now()).split('.')[0]} - Processing {len(addresses)} addresses", flush=True)
        results = pool.map(get_amps_data, addresses) #Open the urls in their own threads
        data = [*data,*results]
        pool.close() #close the pool and wait for the work to finish 
        pool.join()
        addresses = []
    if(i%1000==0):
        print(f"{str(datetime.datetime.now()).split('.')[0]} - Processed {i} out of {len(df_claim)}", flush=True)
        df = pd.DataFrame(data, columns=cols)
        df.to_csv(f'data/amps/amps_{today}.csv')
    i+=1
pool = ThreadPool(4)  # Make the Pool of workers
print(f"{str(datetime.datetime.now()).split('.')[0]} - Processing {len(addresses)} addresses", flush=True)
results = pool.map(get_amps_data, addresses) #Open the urls in their own threads
data = [*data,*results]
df = pd.DataFrame(data, columns=cols)
df.to_csv(f'data/amps/amps_{today}.csv')
