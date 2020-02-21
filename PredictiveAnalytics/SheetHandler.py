from PredictiveAnalytics.SheetsClient import *
from PredictiveAnalytics.PredAnaLyb import *


def bool_from_yes_no(yesno: str):
    return True if "yes" in yesno.lower() else False if "no" in yesno.lower() else None


def get_team_data(service):
    raw = get_data(service=service, location="JavaScouting 2020 - Match Observation!B2:W100")
    teams = {}

    for row in raw:
        match = {
            "alliance_color": row[2].lower(),
        }
        if "total" in row[3].lower():
            match["score"] = int(row[4])
        elif "phase" in row[3].lower():
            match["auto_score"] = int(row[5])
            match["tele-op_score"] = int(row[6])
            match["end_game_score"] = int(row[7])
        elif "team" in row[3].lower():
            match["autonomous"] = {
                "num_skystones_delivered": int(row[8]),
                "num_stones_delivered": int(row[9]),
                "num_stones_placed": int(row[10]),
                "moved_foundation": bool_from_yes_no(row[11]),
                "parked": bool_from_yes_no(row[12])
            }
            match["tele-op"] = {
                "num_stones_delivered": int(row[13]),
                "num_stones_placed": int(row[14]),
                "tallest_skyscraper_levels": int(row[15])
            }
            match["end_game"] = {
                "capped": bool_from_yes_no(row[16]),
                "num_cap_levels": int(row[17]),
                "moved_foundation": bool_from_yes_no(row[18]),
                "parked": bool_from_yes_no(row[19])
            }


        if str(row[0]) not in teams.keys():
            teams[str(row[0])] = {}
        teams[str(row[0])][str(row[1])] = match





