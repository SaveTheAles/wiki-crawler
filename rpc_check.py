from methods import *
from wallet import seed_to_privkeyimport warnings

warnings.filterwarnings("ignore")

df = load_df(PATH_TO_DF)

privkey = seed_to_privkey(SEED, path="m/44'/118'/0'/0/0")
address = privkey_to_address(privkey)

def check(cid_from, cid_to, address):
    request = \
        requests.get(RPC_API + '/is_link_exist?from={}&to={}&address={}'.format(
            json.dumps(cid_from), json.dumps(cid_to), json.dumps(address)))
    return request.json()['result']

tqdm.pandas()
df['isLinked'] = df.progress_apply(lambda x: check(x['cid_from'], x['cid_to'], address), axis=1)


print('saving to csv...')
save_to_csv(df, PATH_TO_DF)

