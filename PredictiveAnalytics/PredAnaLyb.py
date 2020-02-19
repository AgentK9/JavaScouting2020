
data_structure = {  # Dict of Teams (key: number, data: data)
    "0000": {  # Team
        "0": {  # Match/Pre-Match Scouting
            "alliance_color": "red",
            "autonomous": {
                "num_skystones_delivered": 0,
                "num_stones_delivered": 0,
                "num_stones_placed":0,
                "moved_foundation": False,
                "parked": 0
            },
            "tele-op": {
                "num_stones_delivered": 0,
                "num_stones_placed": 0,
                "tallest_skyscraper_levels": 0
            },
            "end_game": {
                "num_caps": 0,
                "num_cap_levels_1": 0,
                "num_cap_levels_2": 0,
                "moved_foundation": False,
                "parked": 0
            }

        },
        "1": {  # alternate (simpler) format
            "alliance_color": "red",  # (red/blue)
            "score": 0
        }
    }
}
schedule_structure = [
    {
        "red": [1000, 1001],
        "blue": [1002, 1003]
    }
]


def get_score_from_complex(match: dict):
    total = 0

    # autonomous
    autonomous = match["autonomous"]
    total += autonomous["num_skystones_delivered"] * 10
    total += autonomous["num_stones_delivered"] * 2
    total += autonomous["num_stones_placed"] * 4
    total += 10 if autonomous["moved_foundation"] else 0
    total += autonomous["parked"] * 5

    # tele-op
    teleOp = match["tele-op"]
    total += teleOp["num_stones_delivered"]
    total += teleOp["num_stones_placed"]
    total += teleOp["tallest_skyscraper_levels"] * 2

    # end game
    end_game = match["end_game"]
    total += end_game["num_caps"] * 5
    total += end_game["num_cap_levels_1"]
    total += end_game["num_cap_levels_2"]
    total += 15 if end_game["moved_foundation"] else 0
    total += end_game["parked"] * 5

    return total


def get_score(match: dict):
    return match["score"] if "score" in match.keys() else get_score_from_complex(match=match)


def get_avg_team_score(team: dict):
    total = 0

    for key in team.keys():
        if key != "0":
            match = team[key]
            total += get_score(match=match)

    return total / len(team.keys()) + (-1 if "0" in team.keys() else 0)


def get_match_score(schedule: list, match_num: int, data: dict):
    # match objects
    try:
        red_a_match = data[schedule[match_num - 1]["red"][0]][str(match_num)]
        red_b_match = data[schedule[match_num - 1]["red"][1]][str(match_num)]
        blue_a_match = data[schedule[match_num - 1]["blue"][0]][str(match_num)]
        blue_b_match = data[schedule[match_num - 1]["blue"][1]][str(match_num)]
    except KeyError:
        # not enough data on this match
        return None, None

    # score totals (they should be the same, averaged just so it'll work and be somewhat accurate
    red_score = (get_score(red_a_match) + get_score(red_b_match))/2
    blue_score = (get_score(blue_a_match) + get_score(blue_b_match))/2

    return red_score, blue_score


def get_current_standings(schedule: list, data: dict):
    teams = {}
    skipped = []
    for team in data.keys():
        # teams[team] = {}
        teams[team] = {
            "RP": [],
            "TBP": []
        }

    for (num, match) in enumerate(schedule):
        red_score, blue_score = get_match_score(schedule=schedule, match_num=num+1, data=data)

        if red_score is None or blue_score is None:
            skipped.append(num)
            continue

        if red_score > blue_score:
            teams[match["red"][0]]["RP"].append(2)
            teams[match["red"][1]]["RP"].append(2)
            teams[match["blue"][0]]["RP"].append(0)
            teams[match["blue"][1]]["RP"].append(0)
        elif blue_score > red_score:
            teams[match["red"][0]]["RP"].append(0)
            teams[match["red"][1]]["RP"].append(0)
            teams[match["blue"][0]]["RP"].append(2)
            teams[match["blue"][1]]["RP"].append(2)
        else:
            teams[match["red"][0]]["RP"].append(1)
            teams[match["red"][1]]["RP"].append(1)
            teams[match["blue"][0]]["RP"].append(1)
            teams[match["blue"][1]]["RP"].append(1)

        teams[match["red"][0]]["TBP"].append(min(blue_score, red_score))
        teams[match["red"][1]]["TBP"].append(min(blue_score, red_score))
        teams[match["blue"][0]]["TBP"].append(min(blue_score, red_score))
        teams[match["blue"][1]]["TBP"].append(min(blue_score, red_score))

    return teams, skipped


def sim_match(schedule: list, match_num: int, data: dict):
    avg_red_a = get_avg_team_score(data[str(schedule[match_num - 1]["red"][0])])
    avg_red_b = get_avg_team_score(data[str(schedule[match_num - 1]["red"][1])])
    avg_blue_a = get_avg_team_score(data[str(schedule[match_num - 1]["blue"][0])])
    avg_blue_b = get_avg_team_score(data[str(schedule[match_num - 1]["blue"][1])])

    red_score = (avg_red_a + avg_red_b) / 2
    blue_score = (avg_blue_a + avg_blue_b) / 2

    winner = "red" if max(red_score, blue_score) == red_score else "blue"
    tbp = min(red_score, blue_score)

    return winner, tbp


def predict_analyze_qual_matches(data: dict, schedule: list, print_=False):
    standings, skipped = get_current_standings(schedule=schedule, data=data)

    for match_num in skipped:
        winner, tbp = sim_match(schedule=schedule, match_num=match_num, data=data)

        if winner == "red":
            standings[str(schedule[match_num - 1]["red"][0])]["RP"].append(2)
            standings[str(schedule[match_num - 1]["red"][1])]["RP"].append(2)
            standings[str(schedule[match_num - 1]["blue"][0])]["RP"].append(0)
            standings[str(schedule[match_num - 1]["blue"][1])]["RP"].append(0)
        elif winner == "blue":
            standings[str(schedule[match_num - 1]["red"][0])]["RP"].append(0)
            standings[str(schedule[match_num - 1]["red"][1])]["RP"].append(0)
            standings[str(schedule[match_num - 1]["blue"][0])]["RP"].append(2)
            standings[str(schedule[match_num - 1]["blue"][1])]["RP"].append(2)
        else:
            standings[str(schedule[match_num - 1]["red"][0])]["RP"].append(1)
            standings[str(schedule[match_num - 1]["red"][1])]["RP"].append(1)
            standings[str(schedule[match_num - 1]["blue"][0])]["RP"].append(1)
            standings[str(schedule[match_num - 1]["blue"][1])]["RP"].append(1)

    print_standings(standings) if print_ else None

    return standings


def print_standings(standings: dict):
    for team in standings.keys():
        standings[team]["TBP"] = sum(standings[team]["TBP"]) / len(standings[team]["TBP"])-1 #  TODO: remove lowest TBP
        standings[team]["RP"] = sum(standings[team]["RP"]) / len(standings[team]["RP"])-1

    print(standings)
