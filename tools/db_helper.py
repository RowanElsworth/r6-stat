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
        try:
            self.connect()
            query = "SELECT name, aliases FROM team_players"
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
            self.cursor.execute(query, competition_type)
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

    def insert_new_team(self, team_name, rounds_won, rounds_lost, map_id, team_id):
        try:
            self.connect()
            query = "INSERT INTO teams (team_name, rounds_won, rounds_lost, map_id, team_id) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(query, (team_name, rounds_won, rounds_lost, map_id, team_id))
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
                name TEXT NOT NULL,
                aliases TEXT NOT NULL
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
        cursor.execute(query, "Scrim") # Init scrim type
        conn.commit()

        for player in players:
            query = "INSERT INTO team_players (name, aliases) VALUES (?, ?)"

            cursor.execute(query, (player[0], player[1]))
            conn.commit()

        cursor.close()
        conn.close()

        print(f"Database {db_path} created successfully!")

    def modify_team_details(self):
        pass