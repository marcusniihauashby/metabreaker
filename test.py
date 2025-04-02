import requests
import json
from pprint import pprint
from utilities import *
from globals import *
from datetime import datetime
import pandas as pd

# dd_champ_url = "https://ddragon.leagueoflegends.com/cdn/15.6.1/data/en_US/champion.json"
# ddchamps = requests.get(dd_champ_url).json()['data']

# tags = {}
# for champ in ddchamps:
#     tags[champ] = ddchamps[champ]['tags']

# pprint.pprint(tags)


for i in range(5):
    print(' ')

# find_meta_breaker()

# print(get_matches(neo_regions[0], my_puuid, 6))

# dd_items = "https://ddragon.leagueoflegends.com/cdn/15.6.1/data/en_US/item.json"

# items = requests.get(dd_items).json()['data']


# itemtoid = {}
# for key in items:
#     itemtoid[key] = items[key]['name']

# # pprint(json.dumps(itemtoid))

# with open("item_to_id.json", "w") as file:
#     file.write(json.dumps(itemtoid, indent = 4))


# meraki_items = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/items.json"

# items = requests.get(meraki_items).json()

# arr = []
# for item in items:
#     print(items[item]['rank'])
#     if items[item]['rank'] == ['BOOTS']:
#         arr.append(items[item]["name"])

# print(json.dumps(arr, indent = 2))



with open("archetype_items.json", "r") as file:
    archetype_items = json.load(file)

with open("champ_classes.json", "r") as file:
    classes = json.load(file)

with open("champ_items.json", "r") as file:
    champ_items = json.load(file)

with open("champ_positions.json", "r") as file:
    positions = json.load(file)

with open("mostrecent.json", "r") as file:
    recent = json.load(file)

findplayers = find_meta_breakers()

pprint(findplayers)