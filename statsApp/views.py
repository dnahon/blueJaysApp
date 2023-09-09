from django.shortcuts import render
from django.http import HttpResponse
import requests
import feedparser
import calendar
from bs4 import BeautifulSoup

BASE_API_URL = "https://statsapi.mlb.com"

#Create a dictionary to map the full team name to the team abbreviation
teams_dict = {
    "Arizona Diamondbacks" : "AZ",
    "Atlanta Braves" : "ATL", 
    "Baltimore Orioles" : "BAL", 
    "Boston Red Sox" : "BOS",
    "Chicago Cubs" : "CHC",
    "Chicago White Sox" : "CWS",
    "Cincinnati Reds" : "CIN",
    "Cleveland Guardians" : "CLE",
    "Cleveland Indians" : "CLE",
    "Colorado Rockies" : "COL", 
    "Detroit Tigers" : "DET", 
    "Florida Marlins" : "FLA", 
    "Miami Marlins" : "MIA", 
    "Houston Astros" : "HOU", 
    "Kansas City Royals" : "KC",
    "Los Angeles Angels" : "LAA",
    "Los Angeles Dodgers" : "LAD",
    "Milwaukee Brewers" : "MIL",
    "Minnesota Twins" : "MIN",
    "New York Mets" : "NYM",
    "New York Yankees" : "NYY",
    "Oakland Athletics" : "OAK",
    "Philadelphia Phillies" : "PHI",
    "Pittsburgh Pirates" : "PIT",
    "San Diego Padres" : "SD",
    "San Francisco Giants" : "SF",
    "Seattle Mariners" : "SEA",
    "St. Louis Cardinals" : "STL", 
    "Tampa Bay Rays" : "TB",
    "Texas Rangers" : "TEX",
    "Toronto Blue Jays" : "TOR",
    "Washington Nationals" : "WAS"
}

#Create a dictionary to map the leader category for the API call to the actual leader category name
categories_dict = {
    "battingAverage" : "Batting Average",
    "runsBattedIn" : "RBI", 
    "homeRuns" : "Home Runs", 
    "stolenBases" : "Stolen Bases",
    "wins" : "Wins",
    "era" : "ERA",
    "whip" : "WHIP",
    "saves" : "Saves",
}

def home(request):

    # Initialize an empty dictionary to hold standings by division
    division_standings_map = {}

    # Fetch standings data from the API
    standings_response = requests.get(BASE_API_URL + "/api/v1/standings?leagueId=103,104")
    records_by_div = standings_response.json().get("records")

    # Process standings data by division
    for div in records_by_div:
        division_response = requests.get(BASE_API_URL + div.get("division").get("link"))
        division_name = division_response.json().get("divisions")[0].get("nameShort")

        #Get the records for each team
        records_by_team = div.get("teamRecords")

        #Initialize an empty list to story all the team data
        list_of_team_dicts = []

        #Iterate through every team in the division, extract relevant team information
        for team in records_by_team:
            team_id = team.get("team").get("id")
            team_name = team.get("team").get("name")
            team_abbreviation = teams_dict.get(team_name)
            team_wins = team.get("leagueRecord").get("wins")
            team_losses = team.get("leagueRecord").get("losses")
            pct = team.get("leagueRecord").get("pct")
            games_back = team.get("gamesBack")
            records = team.get("records")
            last_ten_dict = [element for element in records.get("splitRecords") if element['type'] == "lastTen"][0]
            last_ten_wins = last_ten_dict.get("wins")
            last_ten_losses = last_ten_dict.get("losses")
            run_differential = team.get("runDifferential")

            team_dict = {"id" : team_id, "name" : team_abbreviation, "wins": team_wins, "losses" : team_losses, "pct" : pct, "games_back" : games_back, "last_ten_wins" : last_ten_wins, "last_ten_losses" : last_ten_losses,  "run_differential" : run_differential}
            list_of_team_dicts.append(team_dict)
        division_standings_map[division_name] = list_of_team_dicts

    # Fetch and process news data
    url = 'https://www.mlb.com/feeds/news/rss.xml'
    news = feedparser.parse(url)
    soup = BeautifulSoup(requests.get(url).text, features="xml")

    #Extract image links from the XML file
    images = soup.find_all('image')

    #Initialize an empty list to hold news entry data
    list_of_news_entries = []

    #Iterate through the news entries, extracting relevant information
    for idx, entry in enumerate(news.get("entries")):
        news_entry_dict = {}
        news_entry_dict["title"] = entry.get("title")
        news_entry_dict["author"] = entry.get("author")
        time_unparsed = entry.get("published_parsed")
        news_entry_dict["time"] = str(calendar.month_abbr[time_unparsed.tm_mon]) + " " + str(time_unparsed.tm_mday) + " " + str(time_unparsed.tm_year)
        news_entry_dict["link"] = entry.get("link")
        news_entry_dict["image"] = images[idx].get('href')

        list_of_news_entries.append(news_entry_dict)

        #We only want 4 news entries 
        if len(list_of_news_entries) > 3:
            break

    #Create a list of categories that we want to get the leaders for
    categories = ['homeRuns', 'stolenBases', 'runsBattedIn', 'battingAverage', 'wins', 'era', 'whip', 'saves']

    #Create a dictionary to story the leaders data
    leaders_data = {}

    #Iterate through the categories
    for category in categories:

        #Get the leaders data for this category from the API
        leader_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=" + category)
        leaders_list = []

        #Iterate through each leader, extractng the relevant data
        for player in leader_response.json().get("leagueLeaders")[0].get("leaders"):
            player_info = {}
            player_info["player"] = player.get("person").get("fullName")
            player_info["player_id"] = player.get("person").get("id")
            player_info["team"] = teams_dict.get(player.get("team").get("name"))
            player_info["team_id"] = player.get("team").get("id")
            player_info["value"] = player.get("value")

            leaders_list.append(player_info)

        #Handle ties in the leaderboard
        if len(leaders_list) > 5:
            last_dict = leaders_list[4]
            after_last_dict = leaders_list[5]
            if (last_dict.get("value") == after_last_dict.get("value") ):
                last_dict["player"] = last_dict["player"] + " & " + str(len(leaders_list) - 5) + " more"

            leaders_list[4] = last_dict
            leaders_list = leaders_list[0:5]

        leaders_data[categories_dict.get(category)] = leaders_list
 
    desired_order_list = ["Home Runs", "Wins", "Stolen Bases", "ERA", "RBI", "WHIP", "Batting Average", "Saves"]
    reordered_leaders_data = {k: leaders_data[k] for k in desired_order_list}
    #Render the page with relevant data
    return render(request,'v2/index.html', {'data': division_standings_map, 'news' : list_of_news_entries, 'leaders_data' : reordered_leaders_data})

def roster(request, team_id):
    test= requests.get(BASE_API_URL + "/api/v1/teams/" + str(team_id) + "/coaches")
    print(test.json())

    initial_team_response = requests.get(BASE_API_URL + "/api/v1/teams/" + str(team_id))

    roster_response = requests.get(BASE_API_URL + "/api/v1/teams/" + str(team_id) + "/roster")
    team_name = initial_team_response.json().get("teams")[0].get("name")

    list_of_hitter_dicts = []
    list_of_pitcher_dicts = []
    for player in roster_response.json().get("roster"):
        player_id = player.get("person").get("id")
        number = player.get("jerseyNumber")
        position = player.get("position").get("abbreviation")

        player_dict = {"number" : number, "position" : position, "id" : player_id}
        if position == "P":
            player_response = requests.get(BASE_API_URL + "/api/v1/people/" + str(player_id) + "?hydrate=stats(group=[pitching],type=[yearByYear])")
            last_season_stats = [element for element in player_response.json().get("people")[0].get("stats")[0].get("splits")if element['season'] == "2023"][0].get("stat")
            innings = last_season_stats.get("inningsPitched")
            era = last_season_stats.get("era")
            strikeouts = last_season_stats.get("strikeOuts")
            walks = last_season_stats.get("baseOnBalls")
            batters = last_season_stats.get("battersFaced")
            strikeout_percentage = round(100 * strikeouts / batters, 2)
            walk_percentage = round(100 * walks / batters, 2)
            home_runs = last_season_stats.get("homeRunsPer9")
            ops = last_season_stats.get("ops")

            player_dict["innings"] = innings
            player_dict["era"] = era
            player_dict["strikeouts"] = strikeouts
            player_dict["walks"] = walks
            player_dict["home_runs"] = home_runs
            player_dict["strikeout_percentage"] = strikeout_percentage
            player_dict["walk_percentage"] = walk_percentage
            player_dict["home_runs"] = home_runs
            player_dict["ops"] = ops
            
            list_of_pitcher_dicts.append(player_dict)
        else: 
            player_response = requests.get(BASE_API_URL + "/api/v1/people/" + str(player_id) + "?hydrate=stats(group=[hitting],type=[yearByYear])")
            last_season_stats = [element for element in player_response.json().get("people")[0].get("stats")[0].get("splits")if element['season'] == "2023"][0].get("stat")
            plate_appearances = last_season_stats.get("plateAppearances")
            hits = last_season_stats.get("hits")
            doubles = last_season_stats.get("doubles")
            triples = last_season_stats.get("triples")
            home_runs = last_season_stats.get("homeRuns")
            steals = last_season_stats.get("stolenBases")
            strikeout_percentage = round(100 * last_season_stats.get("strikeOuts") / int(plate_appearances), 2)
            walk_percentage = round(100 * last_season_stats.get("baseOnBalls") / int(plate_appearances), 2)
            average = last_season_stats.get("avg")
            obp = last_season_stats.get("obp")
            ops = last_season_stats.get("ops")

            player_dict["plate_appearances"] = plate_appearances
            player_dict["hits"] = hits
            player_dict["doubles"] = doubles
            player_dict["triples"] = triples
            player_dict["home_runs"] = home_runs
            player_dict["steals"] = steals
            player_dict["strikeout_percentage"] = strikeout_percentage
            player_dict["walk_percentage"] = walk_percentage
            player_dict["average"] = average
            player_dict["obp"] = obp
            player_dict["ops"] = ops
  
            list_of_hitter_dicts.append(player_dict)

        bats = player_response.json().get("people")[0].get("batSide").get("code")
        throws = player_response.json().get("people")[0].get("pitchHand").get("code")
        name = player_response.json().get("people")[0].get("lastFirstName")
        age = player_response.json().get("people")[0].get("currentAge")
        player_dict["name"] = name
        player_dict["age"] = age
        player_dict["bats"] = bats
        player_dict["throws"] = throws

    return render(request,'v2/roster.html', {'pitcher_data': list_of_pitcher_dicts, 'hitter_data' : list_of_hitter_dicts, "team_id" : team_id, 'team_name' : team_name})

def player(request, player_id):
    basic_player_attributes_response = requests.get(BASE_API_URL + "/api/v1/people/" + str(player_id))
    player = basic_player_attributes_response.json().get("people")[0]

    height = player.get("height")
    weight = player.get("weight")
    bats = player.get("batSide").get("code")
    throws = player.get("pitchHand").get("code")
    age = player.get("currentAge")
    drafted = 'Undrafted'
    if player.get("draftYear") is not None:
        drafted = player.get("draftYear")
    position = player.get("primaryPosition").get("abbreviation")

    if (position !='P'):
        player_stats_response = requests.get(BASE_API_URL + "/api/v1/people/" + str(player_id) + "?hydrate=stats(group=[hitting],type=[yearByYear])")
    else:
        player_stats_response = requests.get(BASE_API_URL + "/api/v1/people/" + str(player_id) + "?hydrate=stats(group=[pitching],type=[yearByYear])")

    player_stats = player_stats_response.json().get("people")[0]
    name = player_stats.get("fullName")
    player_id = player_stats.get("id")
    stats = player_stats.get("stats")[0].get("splits")
    list_of_season_stats = []
    for season in stats:
        if (season.get("numTeams") != None):
            continue
        season_stats = season.get("stat")
        season_stats["season"] = season.get("season")
        #hardship
        if (season.get("numTeams") == None):
            season_stats["team"] = teams_dict.get(season.get("team").get("name"))
            season_stats["team_name"] = season.get("team").get("name")
            season_stats["team_id"] = season.get("team").get("id")

        else:
            season_stats["team"] = "Multiple"
        list_of_season_stats.append(season_stats)

    current_team = list_of_season_stats[-1].get("team_name")
    current_team_id = list_of_season_stats[-1].get("team_id")

    return render(request, 'v2/player.html', {'team_id' : current_team_id, 'team' : current_team, 'name':name, 'id' : player_id, 'height' : height, 'weight' : weight, 'bats' : bats, 'throws' : throws, 'age' : age, 'drafted' : drafted, 'position': position, "list_of_stats":list_of_season_stats})
