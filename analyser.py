import json
from tabulate import tabulate

class Round:
    def __init__(self, round_json):
        self.round_json = round_json


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
        self.kd_percent = None
        self.kd_plus_minus = None
        self.headshot_percentage = None
        self.kpr = None
        self.kost_round_count = 0
        self.kost = None
        self.entry_kills = 0
        self.entry_deaths = 0
        self.entry_diff = None
        self.survival = None
        self.trade_kills = 0
        self.trade_deaths = 0
        self.trade_diff = None
        self.clutches = 0 # 1vX's
        self.plants = 0
        self.defuses = 0
        self.rating = None
        self.kost_flag = False

    def print(self):
        for key, value in vars(self).items():
            print(f"{key}: {value}")

    def lim_print(self):
        print(self.username, self.kills, self.deaths, self.kd)

    def reset_kost_flag(self):
        self.kost_flag = False

    def increase_kost(self):
        if not self.kost_flag:
            self.kost_round_count += 1
            self.kost_flag = True

    def calc_kd_percent(self):
        if self.kills != 0 and self.deaths != 0:
            self.kd_percent = round(self.kills / self.deaths, 2)
        else:
            self.kd_percent = 0

    def calc_kd_plus_minus(self):
        if self.kills != 0 and self.deaths != 0:
            self.kd_plus_minus = self.kills - self.deaths
        else:
            self.kd_plus_minus = 0

    def calc_headshot_percentage(self):
        if self.headshots != 0 and self.kills != 0:
            self.headshot_percentage = round(self.headshots / self.kills, 2)
        else:
            self.headshot_percentage = 0

    def calc_kpr(self, total_rounds):
        if self.kills != 0:
            self.kpr = round(self.kills / total_rounds, 2)
        else:
            self.kpr = 0

    def calc_kost(self, total_rounds):
        if self.kost_round_count != 0 and total_rounds != 0:
            self.kost = round(self.kost_round_count / total_rounds, 2)
        else:
            self.kost = 0

    def calc_entry_diff(self):
        self.entry_diff = self.entry_kills - self.entry_deaths

    def calc_survival(self, total_rounds):
        if self.deaths != 0 and total_rounds != 0:
            self.survival = round((total_rounds - self.deaths) / total_rounds, 2)
        else:
            self.survival = 0

    def calc_trade_diff(self):
        self.trade_diff = self.trade_kills - self.trade_deaths

    def calc_rating(self):
        self.rating = 0.037 + 0.004 * self.entry_kills - 0.005 * self.entry_deaths + 0.714 * self.kpr + 0.492 * self.survival + 0.471 * self.kost + 0.026 * self.clutches + 0.015 * self.plants + 0.019 * self.defuses

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

def parse_round_data(data, game):
    """
    Parses through all the game rounds
    :param data:
    :return:
    """
    for round_info in data.get("rounds", []):
        # print(f"Game Version: {round_info['gameVersion']}")
        # print(f"Site: {round_info['site']}")
        # print(f"Round Number: {round_info['roundNumber']}")

        # Player dictionary for fast lookups
        player_lookup = {player.username: player for team in game.teams for player in team.players}

        # Add who won
        team_that_won = 0 if round_info['teams'][0]['won'] else 1
        team_that_lost = 1 - team_that_won
        game.teams[team_that_won].won_round()
        game.teams[team_that_lost].lose_round()

        # Add entry kills/deaths then regular kills/deaths
        round_log = round_info['matchFeedback']

        for player in player_lookup.values():
            player.reset_kost_flag()

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

            # Edge case? TODO:
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

                # print(event)
                # print(next_kill)
                # print()

                # You get a kill, enemy then kills you
                if killer == next_victim:
                    next_killer.trade_kills += 1
                    victim.increase_kost()
                    break

            killer.increase_kost()

        # Add plants/defuses (Increase Kost)
        plant_events = [event for event in round_info['matchFeedback'] if event['type']['name'] == 'DefuserPlantComplete']
        for event in round_log:
            # print(event)
            if event['type']['name'] == 'DefuserPlantComplete':
                player_with_plant = event['username']
                player_lookup.get(player_with_plant).plants += 1
                player_lookup.get(player_with_plant).increase_kost()

            elif event['type']['name'] == 'DefuserDisableComplete':
                player_with_defuse = event['username']
                player_lookup.get(player_with_defuse).defuses += 1
                player_lookup.get(player_with_defuse).increase_kost()


        # Check if player survived (increase KOST)
        stats = round_info['stats']

        for stat in stats:
            # print(stat)
            if stat['died'] is False:
                temp = stat['username']
                player_lookup.get(temp).increase_kost()

        # Check if player clutched (1vX)
        # If player is the last alive, that means they won a 1vX
        alive_players_team_0 = []
        alive_players_team_1 = []

        for stat in stats:
            player = player_lookup.get(stat['username'])
            if player:
                if player in game.teams[0].players and stat['died'] is False:
                    alive_players_team_0.append(player.username)
                elif player in game.teams[1].players and stat['died'] is False:
                    alive_players_team_1.append(player.username)

        if team_that_won == 0 and len(alive_players_team_0) == 1:
            clutch_player = player_lookup.get(alive_players_team_0[0])
            if clutch_player:
                clutch_player.clutches += 1
        elif team_that_won == 1 and len(alive_players_team_1) == 1:
            clutch_player = player_lookup.get(alive_players_team_1[0])
            if clutch_player:
                clutch_player.clutches += 1



def calc_final_player_data(game):
    player_lookup = {player.username: player for team in game.teams for player in team.players}

    for player in player_lookup.values():
        player.calc_kd_percent()
        player.calc_kd_plus_minus()
        player.calc_headshot_percentage()
        player.calc_kpr(game.total_rounds)
        player.calc_kost(game.total_rounds)
        player.calc_entry_diff()
        player.calc_survival(game.total_rounds)
        player.calc_trade_diff()
        player.calc_rating()

# temp
def print_team_stats(team):
    print(f"\n{team.team_name} Stats:")

    headers = ["Username", "Rating", "K-D(+/-)", "K/D %", "Headshots", "KPR", "KOST", "Entry Kills", "Entry Deaths", "Entry Diff", "Survival", "Trade Kills", "Trade Deaths", "Trade Diff", "Clutches", "Plants", "Defuses"]

    player_data = []
    for player in team.players:
        player_data.append([
            player.username,
            f"{player.rating:.2f}",
            f"{player.kills}-{player.deaths}({player.kd_plus_minus})",
            player.kd_percent,
            f"{player.headshot_percentage * 100:.0f}%",
            f"{player.kpr:.2f}",
            f"{player.kost * 100:.0f}%",
            player.entry_kills,
            player.entry_deaths,
            player.entry_diff,
            f"{player.survival * 100:.0f}%",
            player.trade_kills,
            player.trade_deaths,
            player.trade_diff,
            player.clutches,
            player.plants,
            player.defuses
        ])

    print(tabulate(player_data, headers=headers, tablefmt="pretty"))

def run():
    with open("game.json", "r") as file:
        data = json.load(file)
        game = init_game(data)
        init_teams(data, game)
        parse_round_data(data, game)

        calc_final_player_data(game)

        print_team_stats(game.teams[0])
        print_team_stats(game.teams[1])

        return game, data


# run()