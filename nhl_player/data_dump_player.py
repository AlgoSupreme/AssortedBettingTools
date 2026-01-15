import nhl_team_list as tcl
from nhlpy import NHLClient
from datetime import datetime
import json
import os

save_dir = "data_dump"

class data_dump():

    def __init__(self):

        self.roster = {}
        self.player_data = {}
        self.player_record = {}

        self.position = ["forwards","defensemen"]

        if datetime.now().date().month < 6:
            self.season = f"{int(datetime.now().date().year)-1}{int(datetime.now().date().year)}"
            self.StartDate = str(datetime.now().date().year-1) + "-10-01"
        else:
            self.season = f"{int(datetime.now().date().year)}{int(datetime.now().date().year)+1}"
            self.StartDate = str(datetime.now().date().year-1) + "-10-01"

        self.client = NHLClient(debug=True)

        for team in tcl.TeamThreeCodes:
            self.roster[team] = self.client.teams.team_roster(team, "current")
            for pos in self.position:
                for player in self.roster[team][pos]:
                    self.player_data[player["id"]] = {
                        "game" : self.client.stats.player_game_log(player_id=player["id"], season_id=self.season, game_type=2),
                        "name" : f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
                    }

        for player in self.player_data:
            self.player_record[player] = {
                "Name" : self.player_data[player]["name"],
                "shots" : [],
                "goals" : [],
                "assists" : [],
            }
            for game in self.player_data[player]["game"]:
                self.player_record[player]["shots"].append(game.get("shots", 0))
                self.player_record[player]["goals"].append(game.get("goals", 0))
                self.player_record[player]["assists"].append(game.get("assists", 0))
        
        # Save the compiled list
        output_filename = f'player_analysis{datetime.now().date()}.json'
        with open(os.path.join(save_dir, output_filename), 'w', encoding='utf-8') as f:
            json.dump(self.player_record, f, indent=4, ensure_ascii=False)

        print(f"--- Analysis Complete. Data saved to {output_filename} ---")


data_dump()