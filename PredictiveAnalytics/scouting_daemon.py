from PredictiveAnalytics.SheetHandler import *
from PredictiveAnalytics.SheetsClient import *
from datetime import datetime
from time import sleep
import sys


def set_status(service, message, error=None):
    push_data(service, "Script Status!A2:C2", data=[
        datetime.now(),
        message,
        error
    ])


def get_command(service):
    return get_data(service, "Script Status!D2")


def main():
    service = get_service()
    while True:
        team_data = None
        schedule = None
        try:
            global team_data, schedule
            set_status(service, "getting")
            team_data = get_team_data(service)
            schedule = get_schedule(service)

        except Exception as e:
            set_status(service, "error", error=str(e))
            print(str(e))

        try:
            set_status(service, "analyzing")
            standings = push_pred_analy_results(service, team_data, schedule)
            alliances = push_alliance_results(service, standings, team_data)
            elim_matches = push_elim_results(service, alliances, team_data)
        except Exception as e:
            set_status(service, "error", error=str(e))
            print(str(e))

        try:
            command = get_command(service)
            if command == "continue":
                continue
            elif command == "reset":
                # TODO: Implement Reset
                x = 0
            elif command == "quit":
                sys.exit()
            else:
                set_status(service, "pause")
                while get_command(service) != "continue" and command != "reset" and command != "quit":
                    sleep(2.5)


        except Exception as e:
            set_status(service, "error", error=str(e))
            print(str(e))


if __name__ == "__main__":
    main()