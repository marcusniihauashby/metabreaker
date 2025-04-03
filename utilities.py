from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os
from pprint import pprint
from utilities import *
import pandas as pd
import time
from datetime import datetime
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

with open(os.path.join(json_dir, "other_to_id.json"), "r") as file:
    other_to_id = json.load(file)

item_to_id = {int(k): v for k, v in item_to_id.items()}
perk_to_id = {int(k): v for k, v in perk_to_id.items()}
other_to_id = {int(k): v for k, v in other_to_id.items()}

neo_regions = ["AMERICAS", "ASIA", "EUROPE", "SEA"]


def api_request(url, max_retries=15, retry_delay=10):
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
        return pd.DataFrame(data['entries'])
    
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
        return pd.DataFrame(data['entries'])
    
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
        return pd.DataFrame(data['entries'])
    
    return []

def get_high_elo_players(region = 'na1'):
    chall = get_challenger_players(region)
    gm = get_grandmaster_players(region)
    master = get_master_players(region)
    ladder = pd.concat([chall, gm, master]).reset_index(drop = False).drop(columns='rank').rename(columns={'index': 'rank'})
    ladder['rank'] += 1
    return ladder


def get_match_history(region = str, puuid = str, count = int):
    '''
    Returns a list of 100 most recent match IDs from puuid.
    '''
    neoregion = region_to_neoregion(region)
    call = f"https://{neoregion}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count={count}&api_key={api_key}"

    data = api_request(call)
    return [] if not data else data
    

def assign_perks():
    perks = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json'
    result = requests.get(perks).json()

    perk_ids = extract_json(result, 'id')
    perk_names = extract_json(result, 'name')

    perk_to_dict = dict(map(lambda i, j: (i, j), perk_ids, perk_names))


    with open(os.path.join(json_dir, "perk_to_id.json"), "w") as file:
        json.dump(perk_to_dict, file, indent=4)


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

def extract_json(obj, key):

    arr = []

    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    arr.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, arr, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    
    return extract(obj, arr, key)


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
    
def parse_match_data(region, matchId, puuid):
    neoregion = region_to_neoregion(region)
    call = f'https://{neoregion}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={api_key}'
    match_data = api_request(call)
    metadata = match_data['metadata']
    match_id = metadata['matchId']
    participants = metadata['participants']

    info = match_data['info']
    game_creation = info['gameCreation']
    game_duration = info['gameDuration']
    game_start = info['gameStartTimestamp']
    game_end = info['gameEndTimestamp']

    participant_index = participants.index(puuid)
    player = info['participants'][participant_index]
    '''
    We only want to pull from a singular player, since we only call the function on
    a player that was flagged as weird, then we iterate through their recent games.
    Once these players are added to a database, we can scan through their individual games,
    as they are already flagged.
    below, we get info on the player.
    '''
    
    # KDA Information
    kills = player['kills']
    deaths = player['deaths']
    assists = player['assists']

    # Gameplay
    gold_earned = player['goldEarned']
    gold_spent = player['goldSpent']
    champ_level = player['champLevel']
    neutral_minions_killed = player['neutralMinionsKilled']
    total_minions_killed = player['totalMinionsKilled']
    turret_kills = player['turretKills']
    summoner1_id = player['summoner1Id']
    summoner2_id = player['summoner2Id']

    # Objectives
    damage_dealt_to_objectives = player['damageDealtToObjectives']
    damage_dealt_to_turrets = player['damageDealtToTurrets']
    dragon_kills = player['dragonKills']

    # Off Meta Detection
    item0 = player['item0']
    item1 = player['item1']
    item2 = player['item2']
    item3 = player['item3']
    item4 = player['item4']
    item5 = player['item5']
    item6 = player['item6']
    items_purchased = player['itemsPurchased']

    # Champion Info
    champion_name = player['championName']
    champion_transform = player['championTransform']

    # Misc. Stat Tracking
    bounty_level = player['bountyLevel']
    killing_sprees = player['killingSprees']
    first_blood_assist = player['firstBloodAssist']
    first_blood_kill = player['firstBloodKill']
    first_tower_assist = player['firstTowerAssist']
    first_tower_kill = player['firstTowerKill']
    double_kills = player['doubleKills']
    total_enemy_jungle_minions_killed = player['totalEnemyJungleMinionsKilled']
    largest_killing_spree = player['largestKillingSpree']

    # DPM / HPM
    total_damage_dealt = player['totalDamageDealt']
    total_damage_dealt_to_champions = player['totalDamageDealtToChampions']
    total_damage_shielded_on_teammates = player['totalDamageShieldedOnTeammates']
    total_damage_taken = player['totalDamageTaken']
    total_heal = player['totalHeal']
    total_heals_on_teammates = player['totalHealsOnTeammates']

    # Pings
    all_in_pings = player['allInPings']
    assist_me_pings = player['assistMePings']
    enemy_missing_pings = player['enemyMissingPings']
    enemy_vision_pings = player['enemyVisionPings']
    hold_pings = player['holdPings']
    get_back_pings = player['getBackPings']
    need_vision_pings = player['needVisionPings']
    on_my_way_pings = player['onMyWayPings']
    push_pings = player['pushPings']
    command_pings = player['commandPings']

    # Vision
    detector_wards_placed = player['detectorWardsPlaced']
    vision_score = player['visionScore']
    vision_wards_bought_in_game = player['visionWardsBoughtInGame']
    wards_killed = player['wardsKilled']

    # Game Info
    game_ended_in_early_surrender = player['gameEndedInEarlySurrender']
    game_ended_in_surrender = player['gameEndedInSurrender']

    # Player Info
    participant_id = player['participantId']
    puuid = player['puuid']
    riot_id_game_name = player['riotIdGameName']
    riot_id_tagline = player['riotIdTagline']
    team_id = player['teamId']
    win = player['win']

    # runes i think?
    perks = player['perks']

    stat_perks = perks['statPerks']
    defense = stat_perks['defense']
    flex = stat_perks['flex']
    offense = stat_perks['offense']

    primary = perks['styles'][0]['selections']
    secondary = perks['styles'][1]['selections']
    keystone = primary[0]['perk']
    primary_1 = primary[1]['perk']
    primary_2 = primary[2]['perk']
    primary_3 = primary[3]['perk']
    secondary_1 = secondary[0]['perk']
    secondary_2 = secondary[1]['perk']

    for team in info['teams']:
        if team['teamId'] == team_id:
            obj = team['objectives']
            atakhan = obj['atakhan']['kills']
            baron = obj['baron']['kills']
            champion = obj['champion']['kills']
            dragon = obj['dragon']['kills']
            grubs = obj['horde']['kills']
            inhibitor = obj['inhibitor']['kills']
            tower = obj['tower']['kills']
            rift_herald = obj['riftHerald']['kills']
    
    match_DF = pd.DataFrame({
        'match_id': [match_id],
        'game_creation': [game_creation],
        'game_duration': [game_duration],
        'game_start': [game_start],
        'game_end': [game_end],
        
        # KDA Information
        'kills': [kills],
        'deaths': [deaths],
        'assists': [assists],
        
        # Gameplay
        'gold_earned': [gold_earned],
        'gold_spent': [gold_spent],
        'champ_level': [champ_level],
        'neutral_minions_killed': [neutral_minions_killed],
        'total_minions_killed': [total_minions_killed],
        'turret_kills': [turret_kills],
        'summoner1_id': [summoner1_id],
        'summoner2_id': [summoner2_id],
        
        # Objectives
        'damage_dealt_to_objectives': [damage_dealt_to_objectives],
        'damage_dealt_to_turrets': [damage_dealt_to_turrets],
        'dragon_kills': [dragon_kills],
        
        # Off Meta Detection
        'item0': [item0],
        'item1': [item1],
        'item2': [item2],
        'item3': [item3],
        'item4': [item4],
        'item5': [item5],
        'item6': [item6],
        'items_purchased': [items_purchased],
        
        # Champion Info
        'champion_name': [champion_name],
        'champion_transform': [champion_transform],
        
        # Misc. Stat Tracking
        'bounty_level': [bounty_level],
        'killing_sprees': [killing_sprees],
        'first_blood_assist': [first_blood_assist],
        'first_blood_kill': [first_blood_kill],
        'first_tower_assist': [first_tower_assist],
        'first_tower_kill': [first_tower_kill],
        'double_kills': [double_kills],
        'total_enemy_jungle_minions_killed': [total_enemy_jungle_minions_killed],
        'largest_killing_spree': [largest_killing_spree],
        
        # DPM / HPM
        'total_damage_dealt': [total_damage_dealt],
        'total_damage_dealt_to_champions': [total_damage_dealt_to_champions],
        'total_damage_shielded_on_teammates': [total_damage_shielded_on_teammates],
        'total_damage_taken': [total_damage_taken],
        'total_heal': [total_heal],
        'total_heals_on_teammates': [total_heals_on_teammates],
        
        # Pings
        'all_in_pings': [all_in_pings],
        'assist_me_pings': [assist_me_pings],
        'enemy_missing_pings': [enemy_missing_pings],
        'enemy_vision_pings': [enemy_vision_pings],
        'hold_pings': [hold_pings],
        'get_back_pings': [get_back_pings],
        'need_vision_pings': [need_vision_pings],
        'on_my_way_pings': [on_my_way_pings],
        'push_pings': [push_pings],
        'command_pings': [command_pings],
        
        # Vision
        'detector_wards_placed': [detector_wards_placed],
        'vision_score': [vision_score],
        'vision_wards_bought_in_game': [vision_wards_bought_in_game],
        'wards_killed': [wards_killed],
        
        # Game Info
        'game_ended_in_early_surrender': [game_ended_in_early_surrender],
        'game_ended_in_surrender': [game_ended_in_surrender],
        
        # Player Info
        'participant_id': [participant_id],
        'puuid': [puuid],
        'riot_id_game_name': [riot_id_game_name],
        'riot_id_tagline': [riot_id_tagline],
        'team_id': [team_id],
        'win': [win],
        
        # Runes
        'defense': [defense],
        'flex': [flex],
        'offense': [offense],
        'keystone': [keystone],
        'primary_1': [primary_1],
        'primary_2': [primary_2],
        'primary_3': [primary_3],
        'secondary_1': [secondary_1],
        'secondary_2': [secondary_2],

        # Team Objectives
        'atakhan': [atakhan],
        'baron': [baron],
        'champion': [champion],
        'dragon': [dragon],
        'grubs': [grubs],
        'inhibitor': [inhibitor],
        'tower': [tower],
        'rift_herald': [rift_herald]
    })
    match_DF = match_DF.replace(perk_to_id)
    match_DF = match_DF.replace(item_to_id)
    match_DF = match_DF.replace(other_to_id)
    return match_DF

'''
Want to take a list of challenger/grandmaster matches, and then we find a game where someone builds something weird.
# count weird items that are not in category
# if > 1, then we check account
# grab 100 games from that account, scan them for that character in particular.
# for now, just return the amount of games and the winrates.
'''

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


def find_meta_breakers(region = 'na1', start=0, end=None):

    '''
    get_challenger_players
    get_grandmaster_players
    get_master_players
    '''
    ladder = get_high_elo_players(region)

    playerlist = ladder['puuid'].tolist()
    ten = playerlist[-10:] # the last 10 challenger players
    playersfound = []
    for player in ten:
        matches = get_match_history(region, player, 5) # get 5 matches from each of them
        for match in matches:
            anomalies = check_for_anomalies(region, match) # scan the matches for the weird one-off players
            playersfound.extend(anomalies)
    
    return pd.DataFrame(playersfound)

