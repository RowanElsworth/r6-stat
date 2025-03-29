import json

# TODO: sort this shit out, ugh
class Round:
    pass

class Game:
    def __init__(self, map_name, total_rounds, timestamp, team_name_one, team_id_one, team_name_two, team_id_two):
        self.map_name = map_name
        self.total_rounds = total_rounds
        self.timestamp = timestamp
        self.teams = [Team(team_name_one, team_id_one), Team(team_name_two, team_id_two)]
        self.rounds = []

    def print(self):
        for key, value in vars(self).items():
            print(f"{key}: {value}")

    def add_round(self, game_round):
        self.rounds.append(game_round)

class Team:
    def __init__(self, team_name, team_id):
        self.team_name = team_name
        self.team_id = team_id
        self.rounds_won = 0
        self.rounds_lost = 0
        self.players = []

    def print(self):
        for key, value in vars(self).items():
            print(f"{key}: {value}")

    def print_players(self):
        for player in self.players:
            player.lim_print()

    def add_player(self, player):
        self.players.append(player)

    def won_round(self):
        self.rounds_won += 1

    def lose_round(self):
        self.rounds_lost += 1

class Player:
    def __init__(self, username):
        self.username = username
        self.kills = 0
        self.deaths = 0
        self.headshots = 0
        self.kd = None
        self.headshot_percentage = None
        self.kost = None
        self.entry_kills = 0
        self.entry_deaths = 0
        self.entry_diff = None
        self.survival = None
        self.trade_kills = 0
        self.trade_deaths = 0
        self.trade_diff = None
        self.clutches = 0
        self.plants = 0
        self.defuses = 0

    def print(self):
        for key, value in vars(self).items():
            print(f"{key}: {value}")

    def lim_print(self):
        print(self.username, self.kills, self.deaths, self.kd)

class Round:
    """
    Store the round data for later data manipulation if desired.
    """

def init_game(data):
    """
    Initialises the game class with game data
    :param data:
    :return:
    """
    round_data = data['rounds'][0]

    total_rounds = len(data['rounds'])

    return Game(
        round_data['map']['name'],
        total_rounds,
        round_data['timestamp'],
        round_data['teams'][0]['name'],
        0,
        round_data['teams'][1]['name'],
        1
    )

def init_teams(data, game):
    """
    Initialises the teams classes in the game class with teams data
    :param data:
    :return:
    """
    round_data = data['rounds'][0]

    team_0 = game.teams[0]
    team_1 = game.teams[1]

    for player in round_data['players']:
        player_obj = Player(player['username'])
        if player['teamIndex'] == 0:
            team_0.add_player(player_obj)
        else:
            team_1.add_player(player_obj)

def parse_round_data(data):
    """
    Parses through all the game rounds
    :param data:
    :return:
    """
    for round_info in data.get("rounds", []):
        print(f"Game Version: {round_info['gameVersion']}")
        print(f"Site: {round_info['site']}")
        print(f"Round Number: {round_info['roundNumber']}")

        # Player dictionary for fast lookups
        player_lookup = {player.username: player for team in game.teams for player in team.players}

        # Add who won
        team_that_won = 0 if round_info['teams'][0]['won'] else 1
        team_that_lost = 1 - team_that_won
        game.teams[team_that_won].won_round()
        game.teams[team_that_lost].lose_round()

        # Add entry kills/deaths then regular kills/deaths
        round_log = round_info['matchFeedback']

        kill_events = [event for event in round_info['matchFeedback'] if event['type']['name'] == 'Kill']

        for i, event in enumerate(kill_events):
            player_with_kill = event['username']
            player_with_death = event['target']
            kill_time = event['timeInSeconds']

            killer = player_lookup.get(player_with_kill)
            victim = player_lookup.get(player_with_death)

            if not (killer and victim):
                print(f"Missing player data. Killer: {player_with_kill}, Victim: {player_with_death}")
                continue

            if i == 0: # is the entry frag
                killer.entry_kills += 1
                victim.entry_deaths += 1

            # Add regular kills and deaths
            killer.kills += 1
            victim.deaths += 1

            # Add if headshot
            if event['headshot']:
                killer.headshots += 1

            # Edge case?
            if player_with_kill == player_with_death:
                print(f"{player_with_kill} killed themselves?!?!")

            # Check for trades
            for j in range(i + 1, len(kill_events)):
                next_kill = kill_events[j]
                next_kill_time = next_kill['timeInSeconds']
                next_killer = player_lookup.get(next_kill['username'])
                next_victim = player_lookup.get(next_kill['target'])

                # If next kill is longer than 10 secs, the kill isn't traded - break.
                # You get a kill, no one kills you / you get killed, no one kills who killed you
                if kill_time - next_kill_time > 10:
                    killer.trade_kills += 1
                    victim.trade_deaths += 1
                    break

                print(event)
                print(next_kill)
                print()

                # You get a kill, enemy then kills you
                if killer == next_victim:
                    next_killer.trade_kills += 1
                    break

        # Add plants
        plant_events = [event for event in round_info['matchFeedback'] if event['type']['name'] == 'DefuserPlantComplete']
        for i, event in enumerate(plant_events):
            player_with_plant = event['username']
            player_lookup.get(player_with_plant).defuses += 1



        # print("\nTeams:")
        # for team in round_info["teams"]:
        #     print(f"  - {team['name']} (Role: {team['role']}) | Score: {team['score']}")
        #
        # print("\nPlayers:")
        # for player in round_info["players"]:
        #     print(f"  - {player['username']} ({player['operator']['name']}) - Team Index: {player['teamIndex']}")
        #
        # print("\nKills:")
        # for event in round_info.get("matchFeedback", []):
        #     if event["type"]["name"] == "Kill":
        #         print(f"  - {event['username']} killed {event['target']} ({'Headshot' if event['headshot'] else 'Bodyshot'}) at {event['time']}")
        #
        # print("\nPlayer Stats:")
        # for stat in round_info.get("stats", []):
        #     print(f"  - {stat['username']}: {stat['kills']} Kills, {stat['headshots']} Headshots, Died: {stat['died']}")
        # print("\n" + "-"*50 + "\n")

# Example usage
if __name__ == "__main__":
    with open("game.json", "r") as file:
        data = json.load(file)
        game = init_game(data)
        init_teams(data, game)
        parse_round_data(data)

        # game.print()

        game.teams[0].print()
        print()
        game.teams[0].print_players()
        # game.teams[0].players[2].print()

        print()

        game.teams[1].print()
        print()
        game.teams[1].print_players()
