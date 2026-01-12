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
        self.goalie_sog = {}
        self.goalie_saves = {}

        self.goalie_record = {}

        self.goalie_goalsAllowed = {}
        self.season = "20252026"

        self.client = NHLClient(debug=True)

        for team in tcl.TeamThreeCodes:
            self.roster[team] = self.client.teams.team_roster(team, "current")
            for player in self.roster[team]["goalies"]:
                self.player_data[player["id"]] = {
                    "game" : self.client.stats.player_game_log(player_id=player["id"], season_id=self.season, game_type=2),
                    "name" : f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
                }

        for player in self.player_data:
            self.goalie_record[player] = {
                "Name" : self.player_data[player]["name"],
                "shotsAgainst" : [],
                "goalsAgainst" : [],
                "saves" : [],
            }
            for game in self.player_data[player]["game"]:
                self.goalie_record[player]["shotsAgainst"].append(game.get("shotsAgainst", 0))
                self.goalie_record[player]["goalsAgainst"].append(game.get("goalsAgainst", 0))
                self.goalie_record[player]["saves"].append((game.get("shotsAgainst", 0)-game.get("goalsAgainst", 0)))
        
        # Save the compiled list
        output_filename = f'goalie_analysis_sog_sv_gl{datetime.now().date()}.json'
        with open(os.path.join(save_dir, output_filename), 'w', encoding='utf-8') as f:
            json.dump(self.goalie_record, f, indent=4, ensure_ascii=False)

        print(f"--- Analysis Complete. Data saved to {output_filename} ---")


data_dump()