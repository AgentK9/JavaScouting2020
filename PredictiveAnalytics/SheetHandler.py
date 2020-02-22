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
            match["penalties"] = int(row[8])
        elif "team" in row[3].lower():
            match["autonomous"] = {
                "num_skystones_delivered": int(row[9]),
                "num_stones_delivered": int(row[10]),
                "num_stones_placed": int(row[11]),
                "moved_foundation": bool_from_yes_no(row[12]),
                "parked": bool_from_yes_no(row[13])
            }
            match["tele-op"] = {
                "num_stones_delivered": int(row[14]),
                "num_stones_placed": int(row[15]),
                "tallest_skyscraper_levels": int(row[16])
            }
            match["end_game"] = {
                "capped": bool_from_yes_no(row[17]),
                "num_cap_levels": int(row[18]),
                "moved_foundation": bool_from_yes_no(row[19]),
                "parked": bool_from_yes_no(row[20])
            }
            match["penalties"] = int(row[23])

        if str(row[0]) not in teams.keys():
            teams[str(row[0])] = {}

        teams[str(row[0])][str(row[1])] = match

    return teams


def get_schedule(service):
    raw = get_data(service=service, location="Match Schedule/Predictions/Results!B3:E100")

    schedule = []

    for row in raw:
        schedule.append({
            "red": [row[0], row[1]],
            "blue": [row[2], row[3]]
        })

    return schedule


def push_pred_analy_results(service, data: dict, schedule: list):
    standings = format_qual_standings(predict_analyze_qual_rankings(data=data, schedule=schedule))

    for (num, team) in enumerate(standings.keys()):
        push_data(service, "Rank/Finals Predictions!B" + str(num + 2) + ":D" + str(num + 2), data=[
            [
                int(team), standings[team]["RP"], standings[team]["TBP"]
            ]
        ])

    for (num, match) in enumerate(schedule):
        red_score, blue_score = get_match_score(schedule, num+1, data)
        if not red_score and not blue_score:
            red_score, blue_score = sim_match(schedule, num+1, data)

            push_data(service, "Match Schedule/Predictions/Results!F" + str(num + 2) + ":H" + str(num + 2), data=[
                [
                    red_score, blue_score, "Red" if red_score > blue_score else "Blue"
                ]
            ])
        else:
            push_data(service, "Match Schedule/Predictions/Results!I" + str(num + 2) + ":K" + str(num + 2), data=[
                [
                    red_score, blue_score, "Red" if red_score > blue_score else "Blue"
                ]
            ])

    return standings


def push_alliance_results(service, standings: dict, data: dict):
    alliances = predict_alliance_selection(standings=standings, data=data)

    push_data(service, "Rank/Finals Predictions!G3:I6", data=alliances)


def main():
    service = get_service()
    team_data = get_team_data(service)
    schedule = get_schedule(service)
    standings = push_pred_analy_results(service, team_data, schedule)
    push_alliance_results(service, standings, team_data)


if __name__ == '__main__':
    main()
