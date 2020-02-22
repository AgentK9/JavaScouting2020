data_structure = {  # Dict of Teams (key: number, data: data)
    "0000": {  # Team
        "0": {  # Match/Pre-Match Scouting
            "alliance_color": "red",
            "autonomous": {
                "num_skystones_delivered": 0,
                "num_stones_delivered": 0,
                "num_stones_placed": 0,
                "moved_foundation": False,
                "parked": False
            },
            "tele-op": {
                "num_stones_delivered": 0,
                "num_stones_placed": 0,
                "tallest_skyscraper_levels": 0
            },
            "end_game": {
                "capped": False,
                "num_cap_levels": 0,
                "moved_foundation": False,
                "parked": False
            },
            "penalties": 0

        },
        "1": {  # alternate (simpler) format
            "alliance_color": "red",
            "auto_score": 0,
            "tele-op_score": 0,
            "end_game_score": 0,
            "penalties": 0
        },
        "2": {  # alternate (simplest) format
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
    total += 5 if autonomous["parked"] else 0

    # tele-op
    teleOp = match["tele-op"]
    total += teleOp["num_stones_delivered"]
    total += teleOp["num_stones_placed"]
    total += teleOp["tallest_skyscraper_levels"] * 2

    # end game
    end_game = match["end_game"]
    total += 5 if end_game["capped"] else 0
    total += end_game["num_cap_levels"] if end_game["capped"] else 0
    total += 15 if end_game["moved_foundation"] else 0
    total += 5 if end_game["parked"] else 0

    return total


def get_score(match: dict):
    if "score" in match.keys():
        return match["score"], 1
    elif "auto_score" in match.keys():
        return sum(match[key] if "score" in key else 0 for key in match.keys()), 2
    else:
        return get_score_from_complex(match=match), 3


def get_avg_team_score(team: dict):
    total = 0

    # if we only have one entry and that entry is a pre-scouting entry...
    if len(team.keys()) == 1 and team.keys() == ["0"]:
        # use that entry
        return get_score_from_complex(team["0"])
    # otherwise (we have match data)
    else:
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
    
    # red score
    red_score = 0
    red_a_score, red_a_type = get_score(red_a_match)
    red_b_score, red_b_type = get_score(red_b_match)
    # if we have two alliance scores...
    if (red_a_type == 2 or red_a_type == 3) and (red_b_type == 2 or red_b_type == 3):
        # average the two alliance scores
        red_score += (red_a_score + red_b_score)/2
    # if we have two team scores...
    elif red_a_type == 1 and red_b_type == 1:
        # add the two scores together
        red_score += red_a_score + red_b_score
    # if we have one alliance and one team score...
    elif (red_a_type == 2 or red_a_type == 3) and red_b_type == 1:
        # use the alliance score
        red_score += red_a_score
    elif (red_b_type == 2 or red_b_type == 3) and red_a_type == 1:
        # use the alliance score
        red_score += red_b_score

    # blue score
    blue_score = 0
    blue_a_score, blue_a_type = get_score(blue_a_match)
    blue_b_score, blue_b_type = get_score(blue_b_match)
    # if we have two alliance scores...
    if (blue_a_type == 2 or blue_a_type == 3) and (blue_b_type == 2 or blue_b_type == 3):
        # average the two alliance scores
        blue_score += (blue_a_score + blue_b_score) / 2
    # if we have two team scores...
    elif blue_a_type == 1 and blue_b_type == 1:
        # add the two scores together
        blue_score += blue_a_score + blue_b_score
    # if we have one alliance and one team score...
    elif (blue_a_type == 2 or blue_a_type == 3) and blue_b_type == 1:
        # use the alliance score
        blue_score += blue_a_score
    elif (blue_b_type == 2 or blue_b_type == 3) and blue_a_type == 1:
        # use the alliance score
        blue_score += blue_b_score

    return red_score, blue_score


def get_current_standings(schedule: list, data: dict):
    teams = {}
    skipped = []
    for team in data.keys():
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

    return red_score, blue_score


def predict_analyze_qual_rankings(data: dict, schedule: list):
    standings, skipped = get_current_standings(schedule=schedule, data=data)

    for match_num in skipped:
        red_score, blue_score = sim_match(schedule=schedule, match_num=match_num, data=data)

        if red_score > blue_score:
            standings[str(schedule[match_num - 1]["red"][0])]["RP"].append(2)
            standings[str(schedule[match_num - 1]["red"][1])]["RP"].append(2)
            standings[str(schedule[match_num - 1]["blue"][0])]["RP"].append(0)
            standings[str(schedule[match_num - 1]["blue"][1])]["RP"].append(0)
        elif blue_score > red_score:
            standings[str(schedule[match_num - 1]["red"][0])]["RP"].append(0)
            standings[str(schedule[match_num - 1]["red"][1])]["RP"].append(0)
            standings[str(schedule[match_num - 1]["blue"][0])]["RP"].append(2)
            standings[str(schedule[match_num - 1]["blue"][1])]["RP"].append(2)
        else:
            standings[str(schedule[match_num - 1]["red"][0])]["RP"].append(1)
            standings[str(schedule[match_num - 1]["red"][1])]["RP"].append(1)
            standings[str(schedule[match_num - 1]["blue"][0])]["RP"].append(1)
            standings[str(schedule[match_num - 1]["blue"][1])]["RP"].append(1)

    return standings


def format_qual_standings(standings: dict, print_: bool = False):
    for team in standings.keys():
        standings[team]["TBP"].remove(min(standings[team]["TBP"]))
        standings[team]["TBP"] = round(sum(standings[team]["TBP"]) / len(standings[team]["TBP"]), 2)
        standings[team]["RP"] = round(sum(standings[team]["RP"]) / len(standings[team]["RP"]), 2)

    tbp_sorted = sorted(standings.items(), key=lambda item: item[1]["TBP"], reverse=True)
    rp_sorted = {k: v for k, v in sorted(tbp_sorted, key=lambda item: item[1]["RP"], reverse=True)}

    if print_:
        for (num, team) in enumerate(rp_sorted.keys()):
            print(num + 1, team, rp_sorted[team]["RP"], rp_sorted[team]["TBP"])

    return rp_sorted
