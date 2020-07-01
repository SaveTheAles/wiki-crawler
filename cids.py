from methods import load_df
from config import PATH_TO_DF

df = load_df(PATH_TO_DF)

s1 = df['cid_from']
s2 = df['cid_to']

res = s1.append(s2)
res = res.to_frame()
res = res.drop_duplicates()
res.to_csv('./data/cids.txt', sep='\n', index=False, header=None)

