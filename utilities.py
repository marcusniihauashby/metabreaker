import requests
import json
import time
from datetime import datetime
from pprint import pprint
from utilities import *
from globals import *


'''
*** LIST OF UTILITIES ***
api_request(url, max_retries, retry_delay)
get_challenger_players(region)
get_grandmaster_players(region)
get_master_players(region)
get_puuids(players)
get_matches(region, puuid, count)
get_archetype_items(archetype)
'''

def api_request(url, max_retries=10, retry_delay=10):
    """
    Makes an API request with retry logic for 403 errors.

    Parameters:
        url (str): The API endpoint to call.
        max_retries (int): Number of times to retry on failure.
        retry_delay (int): Time in seconds to wait between retries.

    Returns:
        dict: JSON response if successful, None if failed after retries.
    """
    retries = 0

    while retries < max_retries:
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"429 Forbidden - Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retries += 1
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None  # Exit early for other errors

    print("Max retries reached. Request failed.")
    return None

def region_to_neoregion(region):
    region_mapping = {
        "americas": {"na1", "br1", "la1", "la2"},
        "asia": {"kr", "jp1"},
        "europe": {"eun1", "euw1", "me1", "tr1", "ru"},
        "sea": {"oc1", "sg2", "tw2", "vn2"},
    }
    
    region = region.lower()
    
    for neoregion, regions in region_mapping.items():
        if region in regions:
            return neoregion
    
    return "unknown"  # Return unknown if the region is not found



def get_challenger_players(region = 'na1'):
    '''
    Returns challenger players sorted by LP in descending order
    ** REGIONS **

    ** ELEMENTS **
    "summonerId" - encrypted summoner ID
    "puuid" - encrypted puuid
    "wins" - wins
    "losses" - losses
    "rank" - string
    "leaguePoints" - int
    "hotStreak" - boolean
    "veteran" - boolean
    "freshBlood" - boolean
    '''
    call = (
        "https://"
        + region
        + ".api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key="
        + api_key
    )

    data = api_request(call)
    if data and 'entries' in data:
        return data['entries']
    
    return []



def get_grandmaster_players(region = 'na1'):
    '''
    Returns grandmaster players sorted by LP in descending order
    ** ELEMENTS **
    "summonerId" - encrypted summoner ID
    "puuid" - encrypted puuid
    "wins" - wins
    "losses" - losses
    "rank" - string
    "leaguePoints" - int
    "hotStreak" - boolean
    "veteran" - boolean
    "freshBlood" - boolean
    '''
    call = (
        "https://"
        + region
        + ".api.riotgames.com"
        + "/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key="
        + api_key
    )
    
    data = api_request(call)
    if data and 'entries' in data:
        return data['entries']
    
    return []

def get_master_players(region = 'na1'):
    '''
    Returns grandmaster players sorted by LP in descending order
    ** ELEMENTS **
    "summonerId" - encrypted summoner ID
    "puuid" - encrypted puuid
    "wins" - wins
    "losses" - losses
    "rank" - string
    "leaguePoints" - int
    "hotStreak" - boolean
    "veteran" - boolean
    "freshBlood" - boolean
    '''
    call = f"https://{region}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}"

    
    data = api_request(call)
    if data and 'entries' in data:
        return data['entries']
    
    return []

def get_puuids(players):
    # method necessary to extract puuid's from get_x_players function
    lst = []
    for player in players:
        lst.append(player['puuid'])
    return lst


def get_matches(region = str, puuid = str, count = int):
    '''
    Returns a list of 100 most recent match IDs from puuid.
    ** REGION OPTIONS **
    "AMERICAS", "ASIA", "EUROPE", "SEA"
    '''
    neoregion = region_to_neoregion(region)
    call = f"https://{neoregion}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count={count}&api_key={api_key}"

    data = api_request(call)
    return [] if not data else data
    
def get_archetype_items(archetype = 'All'):
    meraki_items_url = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/items.json"
    items = requests.get(meraki_items_url).json()

    Fighter = []
    Marksman = []
    Assassin = []
    Mage = []
    Tank = []
    Support = []


    for key in items.keys():
        item = items[key]
        tags = item['shop']['tags']
        iname = item['name']
        for tag in tags:
            match tag:
                case 'FIGHTER':
                    Fighter.append(iname)
                case 'MARKSMAN':
                    Marksman.append(iname)
                case 'ASSASSIN':
                    Assassin.append(iname)
                case 'MAGE':
                    Mage.append(iname)
                case 'TANK':
                    Tank.append(iname)
                case 'SUPPORT':
                    Tank.append(iname)


    match archetype:
        case 'Fighter':
            return Fighter
        case 'Marksman':
            return Marksman
        case 'Assassin':
            return Assassin
        case 'Mage':
            return Mage
        case 'Tank':
            return Tank
        case 'Support':
            return Support
        case 'All':
            return [Fighter, Marksman, Assassin, Mage, Tank, Support]
        case _:
            return 'Boy what the hell boy'
        
def get_summoner(region, puuid):
    '''
    Returns summoner from puuid
    ** ELEMENTS ** 
    id - Encrypted summoner ID. Max length 63 characters.
    accountId - Encrypted account ID. Max length 56 characters.
    puuid - Encrypted PUUID. Exact length of 78 characters.
    profileIconId - ID of the summoner icon associated with the summoner.
    revisionDate - Date summoner was last modified specified as epoch milliseconds.
    summonerLevel - Summoner level associated with the summoner.
    '''

    call = (
    "https://" + 
   region + 
    ".api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + 
    puuid + 
    "?api_key=" + 
    api_key
    )

    data = api_request(call)
    return {} if not data else data

def get_account(neoregion, puuid):
    call = (
        "https://" + 
        neoregion + 
        ".api.riotgames.com/riot/account/v1/accounts/by-puuid/" + 
        puuid + 
        "?api_key=" + 
        api_key
    )

    data = api_request(call)
    return 'Nothing found' if not data else (data['gameName'] + '#' + data['tagLine'])


def seconds_to_date(epoch_seconds, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Converts seconds from epoch time to a formatted date string.

    Parameters:
        epoch_seconds (int): The number of seconds since Unix epoch (1970-01-01 00:00:00 UTC).
        fmt (str): The desired format for the output date (default: "%Y-%m-%d %H:%M:%S").

    Returns:
        str: The formatted date string.
    """
    return datetime.fromtimestamp(epoch_seconds / 1000).strftime(fmt)

def get_match_data(region, matchId):
    neoregion = region_to_neoregion(region)
    call = f'https://{neoregion}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={api_key}'
    match_data = api_request(call)
    return {} if not match_data else match_data
    


'''
Want to take a list of challenger/grandmaster matches, and then we find a game where someone builds something weird.
# count weird items that are not in category
# if > 1, then we check account
# grab 100 games from that account, scan them for that character in particular.
# for now, just return the amount of games and the winrates.
'''
  
with open("archetype_items.json", "r") as file:
    archetype_items = json.load(file)

with open("champ_classes.json", "r") as file:
    classes = json.load(file)

with open("champ_items.json", "r") as file:
    champ_items = json.load(file)

with open("champ_positions.json", "r") as file:
    positions = json.load(file)

with open("item_to_id.json", "r") as file:
    item_to_id = json.load(file)

def check_for_anomalies(region = 'AMERICAS', matchId = str):
    '''
    scan each player.
        get champ, items built, role played, classes.
    '''
    weirdplayers = []

    match_data = get_match_data(region, matchId)

    if not match_data:
        print("Match data not found.")
        return weirdplayers
    
    players = match_data['info']['participants']

    for player in players:

        champ = player['championName']
        position = player['teamPosition']
        
        supportFlag = False
        if position == "UTILITY":
            supportFlag = True

        summonerId = player['riotIdGameName']
        summonerTagLine = player['riotIdTagline']
        playerId = summonerId + '#' + summonerTagLine
        
        if position not in positions[champ]:
                weirdo = {'player': playerId, 'champion': champ, 'position': position}
                weirdplayers.append(weirdo)
                continue
        
        offmetaitemcount = 0
        items = []
        
        for i in range(6):
            items.append(player['item' + str(i)])
        
        tags = classes[champ]
        print('PLAYER ID: ', playerId)
        print('Champ: ', champ, '| Role: ', position)

        weirditems = []
        for itemid in items:
            iflag = False
            if itemid == 0:
                continue


            if supportFlag:
                if item in archetype_items['SupportStarter']:
                    iflag = True
            item = item_to_id[str(itemid)]

            if item in archetype_items['Miscellaneous']:
                iflag = True
            
            for tag in tags:
                allowed_class_items = archetype_items[tag]
                
                if item in allowed_class_items:
                    iflag = True

            if item in champ_items[champ]:
                iflag = True

            if iflag == True:
                continue

            else: # this is a weird item
                print()
                print("FOUND WEIRD ITEM")
                print(item)
                print()
                weirditems.append(item)
                offmetaitemcount += 1
        
        if offmetaitemcount >= 3:
            print("OFF META DETECTED")
            # make dict to append
            weirdo = {'player': playerId, 'champ': champ, 'position': position, 'items': weirditems}
            weirdplayers.append(weirdo)
        else:
            print("Normal player.")
        print()
        

        
    return weirdplayers


def find_meta_breakers(region = 'na1'):
    playerlist = get_puuids(get_challenger_players(region))
    ten = playerlist[-10:]
    playersfound = []
    for player in ten:
        matches = get_matches(region, player, 5)
        for match in matches:
            anomalies = check_for_anomalies(region, match)
            playersfound.extend(anomalies)
    
    with open("mostrecent.json", "w") as file:
        file.write(json.dumps(playersfound, indent = 4))


    return playersfound