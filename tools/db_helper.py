import sqlite3


class DBHelper:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_path = None

    def set_db_path(self, db_path):
        self.db_path = db_path

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            return [f"Error accessing {self.db_path}: {e}"]

    def close(self):
        if self.conn:
            self.conn.close()

    def get_players(self):
        """
        Gets the players in the selected team.

        :return:
        Array of Dicts
        [{'name': 'Spotty', 'aliases': 'Spotty.-,Spotty.PP'}]
        """
        try:
            self.connect()
            query = """
                SELECT tp.name, GROUP_CONCAT(pa.alias, ',') AS aliases
                FROM team_players tp
                LEFT JOIN player_aliases pa ON tp.id = pa.player_id
                GROUP BY tp.name;
            """
            self.cursor.execute(query)
            players = self.cursor.fetchall()
            self.close()

            return [{'name': name, 'aliases': aliases} for name, aliases in players]

        except sqlite3.Error as e:
            self.close()
            return [f"Error querying {self.db_path}: {e}"]

    def get_competition_types(self):
        try:
            self.connect()
            query = "SELECT type FROM competition_types"
            self.cursor.execute(query)
            types = self.cursor.fetchall()
            self.close()
            return [t[0] for t in types]
        except sqlite3.Error as e:
            self.close()
            return [f"Error querying {self.db_path}: {e}"]

    def insert_new_competition_type(self, competition_type):
        try:
            self.connect()
            query = "INSERT INTO competition_types (type) VALUES (?)"
            self.cursor.execute(query, (competition_type,))
            self.conn.commit()
            self.close()
        except sqlite3.Error as e:
            self.close()
            return [f"Error querying {self.db_path}: {e}"]

    def insert_new_game(self, game_name, game_type, series):
        try:
            self.connect()

            query = "SELECT id FROM competition_types WHERE type = ?"
            self.cursor.execute(query, (game_type,))
            result = self.cursor.fetchone()

            if result is None:
                raise ValueError(f"Invalid game type: {game_type}")

            game_type_id = result[0]

            query = "INSERT INTO games (game_name, game_type_id, series) VALUES (?, ?, ?)"
            self.cursor.execute(query, (game_name, game_type_id, series))
            self.conn.commit()

            game_id = self.cursor.lastrowid
            self.close()

            return game_id
        except sqlite3.Error as e:
            self.close()
            print(f"Error inserting game: {e}")
            return None

    def insert_new_map(self, map_name, total_rounds, timestamp, game_id):
        try:
            self.connect()
            query = "INSERT INTO maps (map_name, total_rounds, timestamp, game_id) VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (map_name, total_rounds, timestamp, game_id))
            self.conn.commit()

            map_id = self.cursor.lastrowid
            self.close()

            return map_id
        except sqlite3.Error as e:
            self.close()
            print(f"Error inserting map: {e}")
            return None

    def insert_new_team(self, team_name, rounds_won, rounds_lost, map_id, side_start, team_id):
        try:
            self.connect()
            query = "INSERT INTO teams (team_name, rounds_won, rounds_lost, map_id, side_start, team_id) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.execute(query, (team_name, rounds_won, rounds_lost, map_id, side_start, team_id))
            self.conn.commit()

            team_id = self.cursor.lastrowid
            self.close()

            return team_id
        except sqlite3.Error as e:
            self.close()
            print(f"Error inserting team: {e}")
            return None

    def update_team(self, data):
        try:
            for name, aliases in data:
                self.connect()
                query = "UPDATE team_players SET name = ?, aliases = ? WHERE id = ?"
                self.cursor.execute(query, (name, aliases))
                self.conn.commit()

            self.close()
            return True
        except sqlite3.Error as e:
            self.close()
            print(f"Error updating team: {e}")
            return False

    def insert_new_player(self, username, team_id, kills, deaths, headshots, kd_percent, kd_plus_minus,
                          headshot_percentage, kpr, kost, kost_round_count, entry_kills,
                          entry_deaths, entry_diff, survival, trade_kills, trade_deaths,
                          trade_diff, clutches, plants, defuses, rating):
        try:
            self.connect()
            query = """
                INSERT INTO players 
                (username, team_id, kills, deaths, headshots, kd_percent, kd_plus_minus, 
                 headshot_percentage, kpr, kost, kost_round_count, entry_kills, entry_deaths, 
                 entry_diff, survival, trade_kills, trade_deaths, trade_diff, clutches, 
                 plants, defuses, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            self.cursor.execute(query, (username, team_id, kills, deaths, headshots, kd_percent, kd_plus_minus,
                                        headshot_percentage, kpr, kost, kost_round_count, entry_kills, entry_deaths,
                                        entry_diff, survival, trade_kills, trade_deaths, trade_diff, clutches,
                                        plants, defuses, rating))
            self.conn.commit()

            player_id = self.cursor.lastrowid
            self.close()

            return player_id
        except sqlite3.Error as e:
            self.close()
            print(f"Error inserting player: {e}")
            return None

    def create_new_table(self, db_path, players):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE competition_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE team_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE player_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES team_players(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                game_type_id INTEGER NOT NULL,
                series INTEGER NOT NULL,
                FOREIGN KEY (game_type_id) REFERENCES competition_types(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_name TEXT NOT NULL,
                total_rounds INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                rounds_won INTEGER NOT NULL,
                rounds_lost INTEGER NOT NULL,
                map_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                side_start TEXT NOT NULL,
                FOREIGN KEY (map_id) REFERENCES maps(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                kills INTEGER NOT NULL,
                deaths INTEGER NOT NULL,
                headshots INTEGER NOT NULL,
                kd_percent REAL NOT NULL,
                kd_plus_minus REAL NOT NULL,
                headshot_percentage REAL NOT NULL,
                kpr REAL NOT NULL,
                kost REAL NOT NULL,
                kost_round_count INTEGER NOT NULL,
                entry_kills INTEGER NOT NULL,
                entry_deaths INTEGER NOT NULL,
                entry_diff INTEGER NOT NULL,
                survival INTEGER NOT NULL,
                trade_kills INTEGER NOT NULL,
                trade_deaths INTEGER NOT NULL,
                trade_diff INTEGER NOT NULL,
                clutches INTEGER NOT NULL,
                plants INTEGER NOT NULL,
                defuses INTEGER NOT NULL,
                rating REAL NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        """)

        conn.commit()

        query = "INSERT INTO competition_types (type) VALUES (?)"
        cursor.execute(query, ("Scrim",)) # Init scrim type
        conn.commit()

        for player in players:
            name = player[0]
            alias_list = [alias.strip() for alias in player[1].split(",")]

            cursor.execute("INSERT INTO team_players (name) VALUES (?)", (name,))
            player_id = cursor.lastrowid

            for alias in alias_list:
                cursor.execute("INSERT INTO player_aliases (player_id, alias) VALUES (?, ?)", (player_id, alias))

            conn.commit()

        cursor.close()
        conn.close()

        print(f"Database {db_path} created successfully!")

    def modify_team_details(self):
        # TODO:
        pass

    def get_map_stats(self):
        """
        Gets stats of the maps played
        :return:
        """
        pass

    def get_player_stats(self, game_id, game_type_id, map_id):
        """
        Gets the players in the team
        Outputs these player's stats from a type (Global, Competition, Certain Game)
        :return:
        """
        try:
            self.connect()

            clauses = ""

            if game_id is not None:
                clauses = f"WHERE g.id = {game_id}"
            elif game_type_id is not None:
                clauses = f"WHERE g.game_type_id = {game_type_id}"
            elif map_id is not None:
                clauses = f"WHERE m.id = {map_id}"

            query = f"""
                SELECT
                    tp.name AS username,
                    AVG(p.rating) AS avg_rating,
                    SUM(p.kills) AS total_kills,
                    SUM(p.deaths) AS total_deaths,
                    SUM(kd_plus_minus) AS avg_kd_plus_minus,
                    CASE
                        WHEN SUM(p.kills) = 0 THEN 0
                        WHEN SUM(p.deaths) = 0 THEN SUM(p.kills)
                        ELSE CAST(SUM(p.kills) AS REAL) / CAST(SUM(p.deaths) AS REAL)
                    END AS avg_kd_percent,
                    CASE
                        WHEN SUM(p.headshots) = 0 THEN 0
                        ELSE CAST(SUM(p.headshots) AS REAL) / CAST(SUM(p.kills) AS REAL)
                    END AS avg_headshot_percentage,
                    AVG(p.kpr) AS avg_kpr,
                    CASE
                        WHEN SUM(p.kost_round_count) = 0 THEN 0
                        ELSE CAST(SUM(p.kost_round_count) AS REAL) / SUM(m.total_rounds)
                    END AS avg_kost,
                    SUM(p.entry_kills) AS total_entry_kills,
                    SUM(p.entry_deaths) AS total_entry_deaths,
                    SUM(p.entry_diff) AS total_entry_diff,
                    CASE
                        WHEN SUM(p.deaths) = 0 THEN 100
                        ELSE CAST((SUM(m.total_rounds) - SUM(p.deaths)) AS REAL) / SUM(m.total_rounds)
                    END AS total_survival,
                    SUM(p.trade_kills) AS total_trade_kills,
                    SUM(p.trade_deaths) AS total_trade_deaths,
                    SUM(p.trade_diff) AS total_trade_diff,
                    SUM(p.clutches) AS total_clutches,
                    SUM(p.plants) AS total_plants,
                    SUM(p.defuses) AS total_defuses
                FROM players p
                JOIN teams t ON p.team_id = t.id
                JOIN maps m ON t.map_id = m.id
                JOIN games g ON m.game_id = g.id
                JOIN player_aliases pa ON pa.alias = p.username
                JOIN team_players tp ON tp.id = pa.player_id
                {clauses}
                GROUP BY tp.name
                ORDER BY avg_rating DESC;
            """

            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.close()

            return data
        except sqlite3.Error as e:
            self.close()
            return [f"Error querying {self.db_path}: {e}"]

    def get_map_stats(self, game_id, game_type_id, map_id):
        try:
            self.connect()

            clauses = ""

            if game_id is not None:
                clauses = f"WHERE g.id = {game_id}"
            elif game_type_id is not None:
                clauses = f"WHERE g.game_type_id = {game_type_id}"
            elif map_id is not None:
                clauses = f"WHERE m.id = {map_id}"

            query = f"""
                WITH player_matches AS (
                    SELECT DISTINCT
                        t.id AS team_id,
                        t.map_id,
                        m.map_name,
                        t.rounds_won,
                        t.rounds_lost,
                        (t.rounds_won + t.rounds_lost) AS rounds_played
                    FROM player_aliases pa
                    JOIN team_players tp ON tp.id = pa.player_id
                    JOIN players p ON p.username = pa.alias
                    JOIN teams t ON p.team_id = t.id
                    JOIN maps m ON m.id = t.map_id
                    JOIN games g ON m.game_id = g.id
                    {clauses}
                ),
                all_rounds AS (
                    SELECT SUM(rounds_played) AS total_rounds
                    FROM player_matches
                )
                
                SELECT
                    pm.map_name AS "Map Name",
                    COUNT(DISTINCT pm.map_id) AS "Played",
                    COUNT(DISTINCT CASE WHEN pm.rounds_won > pm.rounds_lost THEN pm.map_id END) AS "Won",
                    COUNT(DISTINCT CASE WHEN pm.rounds_won > pm.rounds_lost THEN pm.map_id END) * 100.0 / COUNT(DISTINCT pm.map_id) AS "Map Win %",
                    SUM(pm.rounds_played) AS "Rounds Played",
                    SUM(pm.rounds_won) AS "Rounds Won",
                    SUM(pm.rounds_won) * 100.0 / NULLIF(SUM(pm.rounds_played), 0) AS "Round Win %",
                    ROUND(SUM(pm.rounds_played) * 100.0 / ar.total_rounds, 1) AS "% Playtime"
                FROM player_matches pm
                JOIN all_rounds ar ON 1=1
                GROUP BY pm.map_name
                ORDER BY pm.map_name;
            """

            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.close()

            return data
        except sqlite3.Error as e:
            self.close()
            return [f"Error querying {self.db_path}: {e}"]