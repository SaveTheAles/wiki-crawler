# wiki-crawler

The toolkit for moving IPFS wikipedia articles to the Great Web.

Status: alpha

## Very Important Section!!!

- This is very alpha soft. Highly recommend to create special account for this crawler.
- Keep `data/links.csv` and don't remove it to avoid invalid transactions to network

## Requirements

- [x] ipfs version 0.4.22
- [x] python3

## Preparations

0. Clone this repo and got into it:
```
git clone https://github.com/SaveTheAles/wiki-crawler.git
cd wiki-crawler
```
1. Install all requirements
2. Install python packages:
```
pip3 install -r requirements.txt
```
3. Fill `config.py` with your personal credentials. 
4. Fill `data/queries.txt` with keywords you interested in for parsing. Every word from the new line.

## Launch

1. Launch IPFS daemon
```
ifps daemon
```

2. Run:

```
python3 main.py
```

## What's going on?!?!?!

The crawler gets keywords from your `data/queries.txt` and search for article titles on wikipedia by those keywords and create cyberlinks:

```
query -> [titles]
[titles] -> query
```

After that crawler gets every article in distributed wikipedia by the title it found and create cyberlinks:

```
[titles] -> [articles]
```

And finally, it gets links from the articles with query keyword and cyberlink them too:

```
[articles] -> [links]
```

All you created cyberlinks storing at `data/links.csv`

## Extra tools

1. `cids.py` - tool for extracting all CIDs you crawled to `data/cids.txt`. Should be usefu if you need to pin your CIDs to the remote machine with IPFS node or IPFS cluster.

2. `rpc_check.py` - tool for extra check if your address cyberlinked some cyberlinks. You can use it to avoid invalid transactions with already links existed.

## Whishlist

1. Move `wallet.py` and `transaction.py` to cyber-py library and refactor
2. Add Mongo or another db as local storage for cyberlinks
3. Include `rpc_check.py` as a parallel process

## All contributions are welcome