from nhlpy import NHLClient
from datetime import datetime, timedelta
import nhl_team_list as tcl
import time
import os
import json

class DataDumper():
    TeamData = {}
    Roster = {}

    def __init__(self):

        #
        # General Variable Initializations
        #
        print(int(datetime.now().date().year))
        self.SaveDir = "data_dump_goals"
        if datetime.now().date().month < 6:
            self.season = f"{int(datetime.now().date().year)-1}{int(datetime.now().date().year)}"
            self.StartDate = str(datetime.now().date().year-1) + "-10-01"
        else:
            self.season = f"{int(datetime.now().date().year)}{int(datetime.now().date().year)+1}"
            self.StartDate = str(datetime.now().date().year-1) + "-10-01"
        self.EndDate = (datetime.now().date() - timedelta(days=1))
        self.Roster = {}

        # Load NHL Client API
        self.client = NHLClient(debug=True)

        #Load in all the possible players via the rosters
        for team in tcl.TeamThreeCodes:
            self.Roster[team] = self.client.teams.team_roster(team, self.season)
            self.TeamData[team] = {
                "period1Goals" : 0,
                "period2Goals" : 0,
                "period3Goals" : 0,
                "totalGoals" : 0,
                "date-data" : [],
            }
            time.sleep(0.1)

        self.RetrievalDate = datetime.strptime(self.StartDate, "%Y-%m-%d").date()

        while self.RetrievalDate <= self.EndDate:

            self.DateStr = self.StartDate

            self.DailySchedule = self.client.schedule.daily_schedule(date=str(self.RetrievalDate))

            # Handle API response structure
            self.GamesList = self.DailySchedule.get("games", [])

            for game in self.GamesList:

                # Identify Winner and Loser (for internal logic)
                self.HomeTeam = game["homeTeam"]
                self.AwayTeam = game["awayTeam"]

                #Make containers inside object if not present
                if not self.HomeTeam["abbrev"] in self.TeamData:
                    self.TeamData[self.HomeTeam["abbrev"]] = {}
                if not self.AwayTeam["abbrev"] in self.TeamData:
                    self.TeamData[self.AwayTeam["abbrev"]] = {}

                # Get game data from PlayByPlay
                # Only way to get Offensive, Hits and Goalie Stats all at once.
                self.TempHomeData, self.TempAwayData = self.PlayByPlay(game["id"])

                # Accumulate stats in dictionary
                for key in self.TeamData[self.HomeTeam["abbrev"]].items():
                    key = key[0]
                    if not key == "date-data" and not key == "outcome":
                        self.TeamData[self.HomeTeam["abbrev"]][key] += self.TempHomeData[key]
                for key in self.TeamData[self.AwayTeam["abbrev"]].items():
                    key = key[0]
                    if not key == "date-data" and not key == "outcome":
                        self.TeamData[self.AwayTeam["abbrev"]][key] += self.TempAwayData[key]

                # Save the date data for later
                # Useful for predictive models
                self.TeamData[self.HomeTeam["abbrev"]]["date-data"].append(self.TempHomeData)
                self.TeamData[self.AwayTeam["abbrev"]]["date-data"].append(self.TempAwayData)

            self.RetrievalDate += timedelta(days=1)

        if not os.path.exists(self.SaveDir):
            os.makedirs(f"{self.SaveDir}")

        # Save the compiled list
        self.OutputFile = f'team_analysis_goalBreakdown{datetime.now().date()}.json'
        with open(os.path.join(self.SaveDir, self.OutputFile), 'w', encoding='utf-8') as f:
            json.dump(self.TeamData, f, indent=4, ensure_ascii=False)


    def PlayByPlay(self, game_id):

        #
        # Initialize the stats
        #

        HomeTeamStats = {            
                "period1Goals" : 0,
                "period2Goals" : 0,
                "period3Goals" : 0,
                "totalGoals" : 0,
        }

        AwayTeamStats = {
                "period1Goals" : 0,
                "period2Goals" : 0,
                "period3Goals" : 0,
                "totalGoals" : 0,
        }
        
        #
        # Obtain the play-by-play
        #

        PlayByPlay = self.client.game_center.play_by_play(game_id)

        HomeTeam = PlayByPlay["homeTeam"]["id"]
        AwayTeam = PlayByPlay["awayTeam"]["id"]

        for play in PlayByPlay["plays"]:
            match play["typeCode"]:
                case 505:
                    match play["periodDescriptor"]["number"]:
                        case 1:
                            # Goal Code
                            if play["details"]["eventOwnerTeamId"] == HomeTeam:
                                HomeTeamStats["period1Goals"]+=1
                            else:
                                AwayTeamStats["period1Goals"]+=1
                        case 2:
                            # Goal Code
                            if play["details"]["eventOwnerTeamId"] == HomeTeam:
                                HomeTeamStats["period2Goals"]+=1
                            else:
                                AwayTeamStats["period2Goals"]+=1
                        case 3:
                            # Goal Code
                            if play["details"]["eventOwnerTeamId"] == HomeTeam:
                                HomeTeamStats["period3Goals"]+=1
                            else:
                                AwayTeamStats["period3Goals"]+=1
        
        #Return the calculated stats
        return HomeTeamStats, AwayTeamStats


DataDumper()