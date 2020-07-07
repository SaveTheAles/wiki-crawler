import pandas as pd
from config import *
import wikipedia
import ipfshttpclient
import os
from tqdm import tqdm
import requests
# import re
import math
import time
from transaction import *
from datetime import datetime

def create_IPFS_client():
    return ipfshttpclient.connect(IPFS_HTTP_CLIENT)

def get_titles(query):
    results = wikipedia.search(query)
    return results

def get_article_url(query):
    query = query.replace(' ', '_')
    return '{}/wiki/{}.html'.format(WIKI_IPFS, query)

def get_string_hash(string):
    client = ipfshttpclient.connect(IPFS_HTTP_CLIENT)
    cid = client.add_str(string)
    return cid

def load_df(path):
    df = pd.read_csv(path, index_col=None)
    frame = { 'kw_from': df['kw_from'],
              'kw_to': df['kw_to'],
              'cid_from': df['cid_from'],
              'cid_to': df['cid_to'],
              'isLinked': df['isLinked']
              }
    df = pd.DataFrame(frame)
    return df

def if_file_exist(path):
    if os.path.isfile(path):
        ifExist = True
    else:
        print("Links file not exist. Creating ./data/links.csv file...")
        ifExist = False
    return ifExist

def add_data(_from, _to, df):
    _df = pd.DataFrame(columns=['kw_from', 'kw_to', 'cid_from', 'cid_to', 'isLinked'])
    tqdm.pandas()
    if type(_from) is list:
        _df['kw_from'] = _from
        _df['kw_to'] = _to
    elif type(_to) is list:
        _df['kw_to'] = _to
        _df['kw_from'] = _from
    elif type(_to) is str and type(_from) is str:
        _df['kw_to'] = [_to]
        _df['kw_from'] = [_from]
    _df['isLinked'] = False
    df = add_to_df(df, _df)
    df['cid_from'] = df.progress_apply(lambda x: get_string_hash(x.kw_from) if x.isLinked == False and pd.isnull(x.cid_from) else x.cid_from, axis=1)
    df['cid_to'] = df.progress_apply(lambda x: get_string_hash(x.kw_to) if x.isLinked == False and pd.isnull(x.cid_to) else x.cid_to, axis=1)
    return df

def to_lower_case(items):
    if type(items) is list:
        res = list(map(lambda x: x.lower(), items))
    elif type(items) is str:
        res = items.lower()
    return res

def create_link_file(path):
    df = pd.DataFrame(columns=['kw_from', 'kw_to', 'cid_from', 'cid_to', 'isLinked'])
    df.to_csv(path, index=None)

def save_to_csv(df, path):
    if df is None:
        pass
    else:
        df.to_csv(path)

def add_to_df(df, _df):
    df = pd.concat([df, _df], sort=True).reset_index(drop=True)
    return df

def get_wiki_links(query):
    title = wikipedia.page(query)
    links = title.links
    # links = [x for x in links if re.compile(query, re.IGNORECASE).search(x)]
    links = list(filter(lambda x: query in x, links))
    return links

def clear_dublicates(df):
    df = df.drop_duplicates(subset=['cid_from', 'cid_to'], keep="first")
    indexNames = df[df['cid_from'] == df['cid_to']].index
    if (indexNames.empty):
        pass
    else:
        df = df.drop(indexNames)
    return df

def create_links_df(query, csv_path):
    df = load_df(csv_path)

    # get links query -> [titles]
    print('get links query -> [titles]')
    titles = get_titles(query)
    df = add_data(to_lower_case(query), to_lower_case(titles), df)
    save_to_csv(df, PATH_TO_DF)

    # get links [titles] -> query
    print('get links [titles] -> query')
    df = add_data(to_lower_case(titles), to_lower_case(query), df)
    save_to_csv(df, PATH_TO_DF)

    # get links [titles] -> [urls]
    print('get links [titles] -> [urls]')
    for title in titles:
        url = get_article_url(title)
        df = add_data(to_lower_case(title), url, df)
    save_to_csv(df, PATH_TO_DF)

    # get links [urls] -> [links]
    print('get links [urls] -> [links]')
    for title in titles:
        url = get_article_url(title)
        # if df['kw_from'].str.contains(url).any():
        #     pass
        # else:
        wiki_links = get_wiki_links(title)
        df = add_data(url, to_lower_case(wiki_links), df)
        save_to_csv(df, PATH_TO_DF)

    df = clear_dublicates(df)
    save_to_csv(df, PATH_TO_DF)

    return df

def get_sequence(address):
    request = requests.get(LCD_API+'/auth/accounts/{}'.format(address))
    return request.json()['result']['value']['sequence']

def get_number(address):
    request = requests.get(LCD_API+'/auth/accounts/{}'.format(address))
    return request.json()['result']['value']['account_number']

def sign(account, df, memo):
    tx = Transaction(
           privkey=account['privkey'],
           account_num=account['number'],
           sequence=account['sequence'],
           fee=0,
           gas=200000,
           memo=memo,
           chain_id=CHAIN_ID,
           sync_mode="block",
       )
    subset = df[df['isLinked'] == False].head(CHUNK)
    for index, row in subset.iterrows():
        tx.add_cyberlink(cid_from=row['cid_from'], cid_to=row['cid_to'])
        df['isLinked'].loc[index] = True
    pushable_tx = tx.get_pushable()
    return pushable_tx

def broadcast(tx, account):
    res = requests.post(url=LCD_API+'/txs', data=tx)
    if res.status_code == 200:
        res = res.json()
    else:
        raise Exception("Broadcact failed to run by returning code of {}".format(res.status_code))
    if res['height'] != '0':
        print('block #', res['height'])
        print('tx hash:', res['txhash'])
    elif res['raw_log'] == 'not enough personal bandwidth':
        est = get_recover_estimate(tx, account)
        if est == False:
            print('You can\'t broadcast such huge transaction. Increase you balance or decrease chunk variable.')
            time.sleep(10)
            sys.exit()
        else:
            print(datetime.now().strftime("%H:%M:%S"), 'Not enough personal bandwidth. Sleep for', '~' + str(math.ceil(est / 60)), 'minutes before the next attempt')
            print('Also, you can increase you balance or decrease chunk variable.')
            time.sleep(est)
            broadcast(tx, account)



def processor(query, account, memo):
    if (if_file_exist(PATH_TO_DF)):
        df = create_links_df(query, PATH_TO_DF)
        while (False in df['isLinked'].values):
            tx = sign(account, df, memo)
            save_to_csv(df, PATH_TO_DF)
            broadcast(tx, account)
            account['sequence'] += 1
    else:
        create_link_file(PATH_TO_DF)
        df = create_links_df(query, PATH_TO_DF)
        while (False in df['isLinked'].values):
            tx = sign(account, df, memo)
            save_to_csv(df, PATH_TO_DF)
            broadcast(tx, account)
            account['sequence'] += 1
    save_to_csv(df, PATH_TO_DF)

def get_recover_estimate(tx, account):
    _tx = json.loads(tx)
    links = len(_tx['tx']['msg'])
    price = requests.get(RPC_API + '/current_bandwidth_price?').json()['result']['price']
    band = (links * 100 + 300) * price
    r_band = int(requests.get(RPC_API + '/account_bandwidth?address={}'.format(json.dumps(account['address']))).json()['result']['remained'])
    m_band = int(requests.get(RPC_API + '/account_bandwidth?address={}'.format(json.dumps(account['address']))).json()['result']['max_value'])
    if band > m_band:
        res = False
    else:
        rec_speed = m_band / (16000 * 5.8)
        est = (band - r_band) / rec_speed
        res = int(math.ceil(est))
    return res
