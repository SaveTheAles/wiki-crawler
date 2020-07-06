from wallet import *
from methods import *
import warnings

warnings.filterwarnings("ignore")


memo = 'crawled by wiki crawler'

privkey = seed_to_privkey(SEED, path="m/44'/118'/0'/0/0")
address = privkey_to_address(privkey)
number = get_number(address)
sequence = get_sequence(address)

account = {
    "address": address,
    "privkey": privkey,
    "number": number,
    "sequence": sequence
}

def convert(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct

keywords = [line.strip(':\n') for line in open(KEY_WORDS)]

kw_dict = convert(keywords)

for key in kw_dict:
    kw_dict[key] = kw_dict[key].split(',')
    while ('' in kw_dict[key]):
        kw_dict[key].remove('')

if (if_file_exist(PATH_TO_DF)):
    df = load_df(PATH_TO_DF)
    for key in kw_dict:
        key = to_lower_case(key)
        kw_dict[key] = to_lower_case(kw_dict[key])
        df = add_data(key, kw_dict[key], df)
        while (False in df['isLinked'].values):
            tx = sign(account, df, memo)
            save_to_csv(df, PATH_TO_DF)
            broadcast(tx, account)
            account['sequence'] += 1
else:
    create_link_file(PATH_TO_DF)
    df = load_df(PATH_TO_DF)
    for key in kw_dict:
        key = to_lower_case(key)
        kw_dict[key] = to_lower_case(kw_dict[key])
        df = add_data(key, kw_dict[key], df)
        while (False in df['isLinked'].values):
            tx = sign(account, df, memo)
            save_to_csv(df, PATH_TO_DF)
            broadcast(tx, account)
            account['sequence'] += 1
save_to_csv(df, PATH_TO_DF)
