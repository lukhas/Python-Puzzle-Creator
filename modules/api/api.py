import requests
import chess
import logging
import re
import time
from modules.bcolors.bcolors import bcolors

def get_pgn(token):
    logging.debug(bcolors.WARNING + "Getting new game..." + bcolors.ENDC)
    success = False
    while not success:
        try:
            response = requests.get('https://en.lichess.org/training/api/game.pgn?token=' + token)
            success = True
        except requests.ConnectionError:
            logging.debug(bcolors.WARNING + "CONNECTION ERROR: Failed to get new game.")
            logging.debug("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)
        except requests.exceptions.SSLError:
            logging.warning(bcolors.WARNING + "SSL ERROR: Failed to get new game.")
            logging.debug("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)


    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    return StringIO(response.text)

def post_puzzle(token, puzzle, slack_key, name):
    logging.info(bcolors.OKBLUE + str(puzzle.to_dict()) + bcolors.ENDC)
    success = False
    while not success:
        try:
            r = requests.post("https://en.lichess.org/training/api/puzzle?token=" + token, json=puzzle.to_dict())
            success = True
        except requests.ConnectionError:
            logging.warning(bcolors.WARNING + "CONNECTION ERROR: Failed to post puzzle.")
            logging.debug("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)
        except requests.SSLError:
            logging.warning(bcolors.WARNING + "SSL ERROR: Failed to post puzzle.")
            logging.debug("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)

    
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text)
    if len(urls) > 0:
        puzzle_id = urls[0].split('/')[-1:][0]
        logging.info(bcolors.WARNING + "Imported with ID " + puzzle_id + bcolors.ENDC)
        if slack_key is not None:
            message = {"channel": "#puzzles",
                "username": "Puzzle Generator",
                "text": name + " added puzzle " + urls[0],
                "icon_emoji": ":star:"}
            success = False
            while not success:
                try:
                    requests.post("https://hooks.slack.com/services/" + slack_key, json=message)
                    success = True
                except requests.ConnectionError:
                    logging.warning(bcolors.WARNING + "CONNECTION ERROR: Failed to post to slack.")
                    logging.debug("Trying again in 30 sec" + bcolors.ENDC)
                    time.sleep(30)
                except requests.SSLError:
                    logging.warning(bcolors.WARNING + "SSL ERROR: Failed to post to slack.")
                    logging.debug("Trying again in 30 sec" + bcolors.ENDC)
                    time.sleep(30)
    else:
        logging.error(bcolors.FAIL + "Failed to import with response: " + r.text + bcolors.ENDC)
