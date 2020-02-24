from SheetHandler import *
from SheetsClient import *
from datetime import datetime
from time import sleep
import sys


def set_status(service, message, error=None):
    push_data(service, "Script Status!A2:C2", data=[
        [
            str(datetime.now().time()),
            message,
            error
        ]
    ])


def get_command(service):
    return get_data(service, "Script Status!D2")


def main():
    service = get_service()
    while True:
        team_data = None
        schedule = None
        try:
            set_status(service, "getting")
            team_data = get_team_data(service)
            schedule = get_schedule(service)

        except Exception as e:
            set_status(service, "error-getting", error=str(e))
            print(str(e))

        try:
            set_status(service, "analyzing")
            standings = push_pred_analy_results(service, team_data, schedule)
            alliances = push_alliance_results(service, standings, team_data)
            elim_matches = push_elim_results(service, alliances, team_data)
        except Exception as e:
            set_status(service, "error-analyzing", error=str(e))
            print(str(e))

        try:
            set_status(service, "command")
            command = get_command(service)
            if command == "continue":
                continue
            elif command == "reset":
                # TODO: Implement Reset
                continue
            elif command == "quit":
                sys.exit()
            else:
                set_status(service, "pause")
                while get_command(service) != "continue" and command != "reset" and command != "quit":
                    sleep(2.5)
        except Exception as e:
            set_status(service, "error-command", error=str(e))
            print(str(e))


if __name__ == "__main__":
    main()
