from PredictiveAnalytics.SheetsClient import *
from PredictiveAnalytics.PredAnaLyb import *


def get_team_data(service):
    raw = get_data(service=service, location="JavaScouting 2020 - Match Observation!B2:W100")
    teams = {}

    for row in raw:
        match = {
            "alliance_color": row[2].lower(),
        }
        if "total" in row[3].lower():
            x = 0  # TODO: total based data translation
        elif "phase" in row[3].lower():
            x = 0  # TODO: phase based data translation
        elif "team" in row[3].lower():
            x = 0  # TODO: team based data translation

        if str(row[0]) not in teams.keys():
            teams[str(row[0])] = {}
        teams[str(row[0])][str(row[1])] = match





