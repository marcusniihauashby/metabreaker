import requests
import json
import time
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

def api_request(url, max_retries=10, retry_delay=5):
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
        elif response.status_code == 403:
            print(f"403 Forbidden - Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retries += 1
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None  # Exit early for other errors

    print("Max retries reached. Request failed.")
    return None


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
    call = (
        "https://"
        + region
        + ".api.riotgames.com"
        + "/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key="
        + api_key
    )
    
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
    call = (
        "https://"
        + region
        + ".api.riotgames.com"
        + "/lol/match/v5/matches/by-puuid/"
        + puuid
        + "/ids?type=ranked&start=0&count="
        + str(count)
        + "&api_key="
        + api_key
    )

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
        
# 


playerdata = get_challenger_players()
chall_puuids = get_puuids(playerdata)
pprint(chall_puuids)