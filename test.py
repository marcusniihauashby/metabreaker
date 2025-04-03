from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os
from pprint import pprint
from utilities import *
import pandas as pd
import pygsheets

api_key = os.environ.get('riot_api_key')
my_puuid = os.environ.get('my_puuid')
test_match = os.environ.get('test_match')
json_dir = "JSONs"

with open(os.path.join(json_dir, "archetype_items.json"), "r") as file:
    archetype_items = json.load(file)

with open(os.path.join(json_dir, "champ_classes.json"), "r") as file:
    classes = json.load(file)

with open(os.path.join(json_dir, "champ_items.json"), "r") as file:
    champ_items = json.load(file)

with open(os.path.join(json_dir, "champ_positions.json"), "r") as file:
    positions = json.load(file)

with open(os.path.join(json_dir, "most_recent.json"), "r") as file:
    recent = json.load(file)

with open(os.path.join(json_dir, "item_to_id.json"), "r") as file:
    item_to_id = json.load(file)

with open(os.path.join(json_dir, "perk_to_id.json"), "r") as file:
    perk_to_id = json.load(file)

findplayers = find_meta_breakers()

pprint(findplayers)