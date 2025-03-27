import requests

api_key = "RGAPI-237aa2c7-251e-4f67-871d-72b40b836d98"
api_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Pipeline/iwnl?api_key=RGAPI-237aa2c7-251e-4f67-871d-72b40b836d98"

result = requests.get(api_url)
info = result.json()
mypuuid = info['puuid']

matches_call = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/D4kqwCz-y9dcCdDFcub_0Kv3D6v9Zxtk90nCycAWGm82Z1dXAQAWvOrtjTV0DxhGBg_BbUUOdnDuRQ/ids?start=0&count=20&api_key=RGAPI-237aa2c7-251e-4f67-871d-72b40b836d98"
matches = requests.get(matches_call).json()

recent_match_call = "https://americas.api.riotgames.com/lol/match/v5/matches/NA1_5239361944?api_key=RGAPI-237aa2c7-251e-4f67-871d-72b40b836d98"
match_data = requests.get(recent_match_call).json()

print(match_data['info']['participants'][0])