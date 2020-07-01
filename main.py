from methods import *
from config import *
from wallet import *
import warnings

warnings.filterwarnings("ignore")

queries = [line.strip() for line in open(QUERIES)]

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

for query in queries:
    print('the progress:', queries.index(query)+1, 'of', len(queries))
    print('collecting data for', '\n', '***********', query, ' ***********', '\n', 'keyword')
    memo = 'crawled by wiki crawler'
    processor(query, account, memo)
