from django.shortcuts import render
from django.http import HttpResponse
import requests
import feedparser
import calendar

BASE_API_URL = "https://statsapi.mlb.com"

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

    dict_to_render = {}

    standings_response = requests.get(BASE_API_URL + "/api/v1/standings?leagueId=103,104")

    records_by_div = standings_response.json().get("records")

    for div in records_by_div:
        division_response = requests.get(BASE_API_URL + div.get("division").get("link"))
        division_name = division_response.json().get("divisions")[0].get("nameShort")
        records_by_team = div.get("teamRecords")

        list_of_team_dicts = []
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
        dict_to_render[division_name] = list_of_team_dicts

    url = 'https://www.mlb.com/feeds/news/rss.xml'
    news = feedparser.parse(url)
    list_of_news_entries = []
    for entry in news.get("entries"):
        news_entry_dict = {}
        news_entry_dict["title"] = entry.get("title")
        news_entry_dict["author"] = entry.get("author")
        time_unparsed = entry.get("published_parsed")
        news_entry_dict["time"] = str(calendar.month_abbr[time_unparsed.tm_mon]) + " " + str(time_unparsed.tm_mday) + " " + str(time_unparsed.tm_year)
        news_entry_dict["link"] = entry.get("link")

        list_of_news_entries.append(news_entry_dict)

        if len(list_of_news_entries) > 3:
            break

    categories = ['homeRuns', 'stolenBases', 'runsBattedIn', 'battingAverage', 'wins', 'era', 'whip', 'saves']

    leaders_data = {}
    for category in categories:
        leader_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=" + category)
        leaders_list = []
        for player in leader_response.json().get("leagueLeaders")[0].get("leaders"):
            player_info = {}
            player_info["player"] = player.get("person").get("fullName")
            player_info["player_id"] = player.get("person").get("id")
            player_info["team"] = teams_dict.get(player.get("team").get("name"))
            player_info["team_id"] = player.get("team").get("id")
            player_info["value"] = player.get("value")

            leaders_list.append(player_info)
        if len(leaders_list) > 5:
            last_dict = leaders_list[4]
            after_last_dict = leaders_list[5]
            if (last_dict.get("value") == after_last_dict.get("value") ):
                last_dict["player"] = last_dict["player"] + " & " + str(len(leaders_list) - 5) + " more"

            leaders_list[4] = last_dict
            leaders_list = leaders_list[0:5]

        leaders_data[categories_dict.get(category)] = leaders_list
 
    return render(request,'index.html', {'data': dict_to_render, 'news' : list_of_news_entries, 'leaders_data' : leaders_data})

def roster(request, team_id):
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

    return render(request,'roster.html', {'pitcher_data': list_of_pitcher_dicts, 'hitter_data' : list_of_hitter_dicts, "team_id" : team_id, 'team_name' : team_name})

def leaders(request):
    home_runs_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=homeRuns")
    home_runs_leaders = []
    for player in home_runs_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        home_runs = {}
        home_runs["player"] = player.get("person").get("fullName")
        home_runs["team"] = teams_dict.get(player.get("team").get("name"))
        home_runs["home_runs"] = player.get("value")
        home_runs_leaders.append(home_runs)


    steals_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=stolenBases")
    steals_leaders = []
    for player in steals_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        steals = {}
        steals["player"] = player.get("person").get("fullName")
        steals["team"] = teams_dict.get(player.get("team").get("name"))
        steals["steals"] = player.get("value")
        steals_leaders.append(steals)


    rbi_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=runsBattedIn")
    rbi_leaders = []
    for player in rbi_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        rbi = {}
        rbi["player"] = player.get("person").get("fullName")
        rbi["team"] = teams_dict.get(player.get("team").get("name"))
        rbi["rbi"] = player.get("value")
        rbi_leaders.append(rbi)


    avg_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=battingAverage")
    avg_leaders = []
    for player in avg_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        avg = {}
        avg["player"] = player.get("person").get("fullName")
        avg["team"] = teams_dict.get(player.get("team").get("name"))
        avg["avg"] = player.get("value")
        avg_leaders.append(avg)

    wins_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=wins")
    wins_leaders = []
    for player in wins_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        wins = {}
        wins["player"] = player.get("person").get("fullName")
        wins["team"] = teams_dict.get(player.get("team").get("name"))
        wins["wins"] = player.get("value")
        wins_leaders.append(wins)


    era_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=era")
    era_leaders = []
    for player in era_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        era = {}
        era["player"] = player.get("person").get("fullName")
        era["team"] = teams_dict.get(player.get("team").get("name"))
        era["era"] = player.get("value")
        era_leaders.append(era)


    whip_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=whip")
    whip_leaders = []
    for player in whip_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        whip = {}
        whip["player"] = player.get("person").get("fullName")
        whip["team"] = teams_dict.get(player.get("team").get("name"))
        whip["whip"] = player.get("value")
        whip_leaders.append(whip)
        
    saves_leaders_response = requests.get(BASE_API_URL + "/api/v1/stats/leaders?leaderCategories=saves")
    saves_leaders = []
    for player in saves_leaders_response.json().get("leagueLeaders")[0].get("leaders"):
        saves = {}
        saves["player"] = player.get("person").get("fullName")
        saves["team"] = teams_dict.get(player.get("team").get("name"))
        saves["saves"] = player.get("value")
        saves_leaders.append(saves)

    return render(request,'leaders.html', {'home_runs': home_runs_leaders, 'steals' : steals_leaders, 'rbi' : rbi_leaders, 'avg': avg_leaders, 'wins': wins_leaders, 'era' : era_leaders, 'whip' : whip_leaders, 'saves' : saves_leaders})

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

    return render(request, 'player.html', {'team' : current_team, 'name':name, 'id' : player_id, 'height' : height, 'weight' : weight, 'bats' : bats, 'throws' : throws, 'age' : age, 'drafted' : drafted, 'position': position, "list_of_stats":list_of_season_stats})
