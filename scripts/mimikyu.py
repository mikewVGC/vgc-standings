
"""
Mimikyu simulates an ongoing tournament... you'll need to add it to 2026.json
and make sure not to deploy that because you'll sure look silly if you do! Also
note that this will only simulate phase 1 swiss. It's purely for testing live
updates, not making fake tournaments.

Format to add to 2026.json:

    {
        "name": "Test City Regional",
        "code": "test-city",
        "region": "Europe",
        "country": "Germany",
        "flag": "de",
        "start": "2026-02-08",
        "end": "2026-02-14",
        "game": "Scarlet & Violet",
        "format": "Regulation H"
    },

Make sure the current date falls within start/end dates. The other fields don't
matter too much.

Next:

In one terminal:
python3 scripts/mimikyu.py -p 36

The 36 can be whatever number of players you like. Once it's simulated the
round (should be very fast), you'll have to rebuild the regional. Don't exit
the script since it will build a fresh player list every time you start it.

In another terminal:
python3 scripts/porygon.py --process 2026:test-city

In your browser observe the data updating after ~4 minutes or so.

You can press enter when mimikyu tells you to get a new round of results. You
have to run the rebuild script each time to see the changes loaded.
"""

import argparse
import json
import random

from lib.tournament import get_tournament_structure

year = 2026

first_names = [
    'Abbey',
    'Britt',
    'Fern',
    'Jojo',
    'Kate',
    'Fawn',
    'Hetty',
    'Joy',
    'Lyn',
    'Maryl',
    'Raven',
    'Sharon',
    'Amalie',
    'Bobby',
    'Celia',
    'Elisha',
    'Jane',
    'Lori',
    'Olympia',
    'Teddy',
]

last_names = [
    'Alston',
    'Feld',
    'Lavor',
    'Noak',
    'Pigford',
    'Oldum',
    'Scotts',
    'Stubbing',
    'Vinal',
    'Whaley',
    'Yalden',
    'Hetford',
    'Ayer',
    'Daine',
    'Dyet',
    'Gome',
    'Nye',
    'Quirk',
    'Tibball',
    'Veckerman',
]

countries = [
    'US',
    'CA',
    'GB',
    'JP',
    'IT',
    'ES',
    'BR',
    'AR',
    'DE',
    'MX',
]

def main():
    
    parser = argparse.ArgumentParser(
        prog="python3 mimikyu.py",
        description="Mimikyu (poorly) simulates an ongoing tournament",
    )
    parser.add_argument('-p', '--players',   required=True, help="Number of players")

    cl = parser.parse_args()

    num_players = int(cl.players)

    players = []

    tour_format = get_tournament_structure(year, num_players, { 'code': 'test' })

    for i in range(num_players):

        first_name = first_names[random.randrange(len(first_names))]
        last_name = last_names[random.randrange(len(last_names))]
        country = countries[random.randrange(len(countries))]

        name = f"{first_name} {last_name} [{country}]"

        players.append({
            'name': name,
            'placing': 0,
            'record': {
                'wins': 0,
                'losses': 0,
                'ties': 0,
            },
            'resistances': {
                'self': 0,
                'opp': 0,
                'oppopp': 0,
            },
            'decklist': [],
            'drop': -1,
            'rounds': {}
        })

    for i in range(tour_format[0]):
        rnum = f"{i + 1}"
        print(f"[simulating] Round {rnum}")

        table = 1

        for pnum, cur_player in enumerate(players):

            if rnum in cur_player['rounds']:
                continue

            # this will just look for the next player who they haven't played yet
            for pid, player in enumerate(players):
                # can't play yourself
                if pid == pnum:
                    continue

                # this player has already played this round
                if rnum in player['rounds']:
                    continue

                # we've played them in a previous round
                if next((p for p in cur_player['rounds'].values() if p['name'] == player['name']), None):
                    continue

                winner = random.randrange(2)

                cur_player['rounds'][rnum] = {
                    'name': player['name'],
                    'result': 'W' if winner == 1 else 'L',
                    'table': table,
                }

                player['rounds'][rnum] = {
                    'name': cur_player['name'],
                    'result': 'L' if winner == 1 else 'W',
                    'table': table,
                }

                table += 1

                break

        for player in players:
            player['record']['wins'] = 0
            player['record']['losses'] = 0
            for round_info in player['rounds'].values():
                if round_info['result'] == 'W':
                    player['record']['wins'] += 1
                if round_info['result'] == 'L':
                    player['record']['losses'] += 1

        players.sort(key=lambda p: p['record']['wins'], reverse=True)

        with open(f"data/majors/{year}/test-city-standings.json", 'w') as file:
            file.write(json.dumps(players, indent=4))

        print('[simulating] Press enter when ready for next round', end="")
        input()

main()
