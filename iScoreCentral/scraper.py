import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse, parse_qs
from typing import Dict, List, Optional
import time

""" Uses the logic from fb.js from the iScoreCentral website. """

DEBUG = False

class PlayerStatsRecord:
    def __init__(self):
        self.games = 0
        self.points = 0
        self.fouls = 0
        self.assists = 0
        self.rebounds = 0
        self.fga3 = 0  # 3-point attempts
        self.fgm3 = 0  # 3-point makes
        self.fga2 = 0  # 2-point attempts
        self.fgm2 = 0  # 2-point makes
        self.fta = 0  # free throw attempts
        self.ftm = 0  # free throw makes
        self.blocks = 0
        self.steals = 0
        self.turnovers = 0
        self.off_rebounds = 0
        self.def_rebounds = 0
        self.deflections = 0
        self.plus_minus = 0

    def to_dict(self):
        return {
            "games": self.games,
            "points": self.points,
            "fouls": self.fouls,
            "assists": self.assists,
            "rebounds": self.rebounds,
            "three_point_attempts": self.fga3,
            "three_point_makes": self.fgm3,
            "two_point_attempts": self.fga2,
            "two_point_makes": self.fgm2,
            "free_throw_attempts": self.fta,
            "free_throw_makes": self.ftm,
            "blocks": self.blocks,
            "steals": self.steals,
            "turnovers": self.turnovers,
            "offensive_rebounds": self.off_rebounds,
            "defensive_rebounds": self.def_rebounds,
            "deflections": self.deflections,
            "plus_minus": self.plus_minus,
        }

class PlayerRecord:
    def __init__(self):
        self.player_name = ""
        self.player_guid = ""
        self.player_game_guid = ""
        self.player_number = 0
        self.position = ""
        self.is_starter = False
        self.stats_today = PlayerStatsRecord()
        self.stats_career = PlayerStatsRecord()

    def to_dict(self):
        return {
            "name": self.player_name,
            "guid": self.player_guid,
            "game_guid": self.player_game_guid,
            "number": self.player_number,
            "position": self.position,
            "is_starter": self.is_starter,
            "stats_today": self.stats_today.to_dict(),
            "stats_career": self.stats_career.to_dict(),
        }

class iScoreCentralScraper:
    BASE_URL = "http://dc.iscorecast.com/gamesync.jsp"
    STATS_URL = "http://data.iscorecentral.com/stats_historical.php"
    GAME_LIST_URL = "http://data.iscorecentral.com/iscorecast/lf_search_games.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    def get_game_list(self, customer_guid: str, password: str = "") -> List[Dict]:
        """Fetch list of games for a team."""
        params = {"cg": customer_guid, "p": password, "m": "1", "sport": "basketball"}

        try:
            if DEBUG:
                print(f"Fetching game list from: {self.GAME_LIST_URL}")
                print(f"Parameters: {params}")

            response = self.session.get(self.GAME_LIST_URL, params=params, timeout=10)

            if DEBUG:
                print(f"Response status: {response.status_code}")
                print(f"Response content (first 500 chars only): {response.text[:500]}")

            response.raise_for_status()

            if not response.content:
                print("Empty response received")
                return []

            root = ET.fromstring(response.content)
            games = []

            for game in root.findall("GAME"):
                games.append(
                    {
                        "game_guid": game.get("gg"),
                        "device_guid": game.get("dg"),
                        "home_team": game.get("htn"),
                        "visitor_team": game.get("vtn"),
                        "home_score": game.get("home_score"),
                        "visitor_score": game.get("visitor_score"),
                    }
                )

            print(f"Found {len(games)} games")
            return games

        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            print(f"Response: {response.text if 'response' in locals() else 'No response'}")
            return []
        except Exception as e:
            print(f"Error fetching game list: {e}")
            import traceback

            traceback.print_exc()
            return []

    def analyze_scorecast_page(self, iscore_url: str) -> Dict:
        """Analyze the scorecast HTML page to understand how data is loaded"""
        try:
            response = self.session.get(iscore_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Look for all script tags
            scripts = soup.find_all("script")

            print(f"Found {len(scripts)} script tags\n")

            # Look for the fb.js or game initialization
            for i, script in enumerate(scripts):
                if script.get("src"):
                    print(f"External script {i+1}: {script.get('src')}")
                elif script.string and len(script.string) > 50:
                    # Check if this script contains game initialization
                    if (
                        "FBGame" in script.string
                        or "game_guid" in script.string
                        or "_game" in script.string
                    ):
                        if DEBUG:
                            print(f"\n=== Found potential game initialization in script {i+1} ===")
                            print(script.string[:1000])

                        # Try to extract the actual API call
                        import re

                        # Look for FBGame constructor call
                        fbgame_match = re.search(
                            r'new FBGame\s*\(\s*["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?(?:\s*,\s*["\']([^"\']*)["\'])?',
                            script.string,
                        )
                        if fbgame_match:
                            print(f"\nFound FBGame initialization:")
                            print(f"  Game GUID: {fbgame_match.group(1)}")
                            if fbgame_match.group(2):
                                print(f"  Device GUID: {fbgame_match.group(2)}")
                            if fbgame_match.group(3):
                                print(f"  Customer GUID: {fbgame_match.group(3)}")

                            return {
                                "game_guid": fbgame_match.group(1),
                                "device_guid": fbgame_match.group(2) or "",
                                "customer_guid": fbgame_match.group(3) or "",
                            }

            return {"error": "Could not find game initialization"}

        except Exception as e:
            print(f"Error analyzing page: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def parse_game_data(
        self,
        game_guid: str,
        device_guid: str = "",
        customer_guid: str = "",
        password: str = "",
    ) -> Dict:
        parameters = {"g": game_guid, "dg": device_guid, "m": "1"}

        try:
            response = self.session.get(self.BASE_URL, params=parameters, timeout=10)

            if DEBUG:
                print(f"Response status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                print(f"Content-Length: {response.headers.get('Content-Length', 'Unknown')}")
                print(f"Response preview (first 500 chars): {response.text[:500]}")

            # Try to parse XML
            root = ET.fromstring(response.content)
            if DEBUG:
                print(f"Successfully parsed XML!")

            # Parse metadata
            game_data = self._parse_metadata(root)

            # Parse players from game start event
            players = self._parse_players_from_events(root)
            game_data["players"] = players

            # Update stats from all events
            self._process_game_events(root, players)

            return game_data

        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def _parse_metadata(self, root: ET.Element) -> Dict:
        metadata = root.find("METADATA")
        if metadata is None:
            return {}

        # Extract team GUIDs from metadata
        home_team_guid = metadata.get("htg", "")
        visitor_team_guid = metadata.get("vtg", "")

        # Store these for later use in tracking team stats
        self.home_team_guid_from_metadata = f"TEAM_{home_team_guid}" if home_team_guid else None
        self.visitor_team_guid_from_metadata = f"TEAM_{visitor_team_guid}" if visitor_team_guid else None

        if DEBUG:
            print(f"DEBUG METADATA: Home team GUID: {self.home_team_guid_from_metadata}")
            print(f"DEBUG METADATA: Visitor team GUID: {self.visitor_team_guid_from_metadata}")

        return {
            "home_team": unquote(metadata.get("htn", "")),
            "visitor_team": unquote(metadata.get("vtn", "")),
            "game_name": unquote(metadata.get("gn", "")),
            "sport": metadata.get("sport", ""),
            "periods": metadata.get("per", "4"),
            "period_length": metadata.get("plen", "12"),
        }

    def _parse_players_from_events(self, root: ET.Element) -> Dict[str, PlayerRecord]:
        """Parse players from GS (Game Start) events"""
        players = {}
        self.home_player_guids = set()
        self.visitor_player_guids = set()

        for update in root.findall("UPDATE"):
            for event in update.findall("EVENT"):
                if event.get("type") == "GS":
                    # Parse visitor team players
                    visitor_str = event.get("param", "")
                    home_str = event.get("player", "")

                    if DEBUG:
                        print(f"\nDEBUG GS Event:")
                        print(f"  Visitor string (param): {visitor_str[:100]}...")
                        print(f"  Home string (player): {home_str[:100]}...")

                    visitor_players = self._parse_player_string(visitor_str, "visitor")
                    players.update(visitor_players)
                    self.visitor_player_guids.update(visitor_players.keys())

                    home_players = self._parse_player_string(home_str, "home")
                    players.update(home_players)
                    self.home_player_guids.update(home_players.keys())

                    break

        # Use the team GUIDs from metadata
        visitor_team_guid = getattr(self, 'visitor_team_guid_from_metadata', None)
        home_team_guid = getattr(self, 'home_team_guid_from_metadata', None)

        if DEBUG:
            print(f"\nDEBUG: Home players: {self.home_player_guids}")
            print(f"DEBUG: Visitor players: {self.visitor_player_guids}")
            print(f"DEBUG: Using home team GUID: {home_team_guid}")
            print(f"DEBUG: Using visitor team GUID: {visitor_team_guid}")

        # Add placeholders for tracking stats with empty/missing player GUIDs
        # Use special keys to distinguish between home and visitor team stats
        visitor_team_placeholder = PlayerRecord()
        visitor_team_placeholder.player_name = "Visitor Team Stats"
        visitor_team_placeholder.player_guid = ""
        visitor_team_placeholder.player_game_guid = "__VISITOR_TEAM__"
        players["__VISITOR_TEAM__"] = visitor_team_placeholder

        # Also add the visitor team GUID if it exists
        if visitor_team_guid:
            players[visitor_team_guid] = visitor_team_placeholder
            self.visitor_player_guids.add(visitor_team_guid)

        home_team_placeholder = PlayerRecord()
        home_team_placeholder.player_name = "Home Team Stats"
        home_team_placeholder.player_guid = ""
        home_team_placeholder.player_game_guid = "__HOME_TEAM__"
        players["__HOME_TEAM__"] = home_team_placeholder

        # Also add the home team GUID if it exists
        if home_team_guid:
            players[home_team_guid] = home_team_placeholder
            self.home_player_guids.add(home_team_guid)

        return players

    def _parse_player_string(
        self, player_str: str, team: str
    ) -> Dict[str, PlayerRecord]:
        """Parse player information from comma-separated string"""
        players = {}

        if not player_str:
            return players

        player_list = player_str.split(",")

        for i, player_data in enumerate(player_list):
            parts = player_data.split(":")

            # Handle case where first item has Team Name prefix
            if i == 0 and len(parts) == 7:
                parts = parts[1:]

            if len(parts) >= 6:
                player = PlayerRecord()
                player.player_guid = parts[0]
                player.player_game_guid = parts[1]
                player.player_number = int(parts[2]) if parts[2] else 0
                player.position = parts[3]
                player.is_starter = parts[4] == "1"
                player.player_name = unquote(parts[5])

                players[player.player_game_guid] = player

        return players

    def _process_game_events(self, root: ET.Element, players: Dict[str, PlayerRecord]):
        for update in root.findall("UPDATE"):
            status = update.get("status", "")
            status_parts = status.split(",")

            # Debug output for first few events
            if DEBUG:
                debug_count = 0
                if debug_count < 3:
                    print(f"\nDEBUG Status {debug_count}: {status}")
                    print(f"DEBUG Status parts: {status_parts}")
                    debug_count += 1

            if len(status_parts) < 8:
                continue

            player_possession = status_parts[7]

            # Determine which team has possession based on the possession player
            # status_parts[1] contains 'V' for visitor or 'H' for home
            current_possession_team = status_parts[1] if len(status_parts) > 1 else ""

            for event in update.findall("EVENT"):
                event_type = event.get("type")
                player_guid = event.get("player", "")
                param = event.get("param", "")

                # Debug output for events with empty player_guid
                if DEBUG:
                    if player_guid == "" and event_type in ["FG", "MISS", "FT"]:
                        print(f"\nDEBUG Empty GUID Event: type={event_type}, param={param}, possession_team={current_possession_team}")

                self._update_player_stats(
                    players, event_type, player_guid, param, player_possession, current_possession_team
                )

    def _update_player_stats(
        self,
        players: Dict[str, PlayerRecord],
        event_type: str,
        player_guid: str,
        param: str,
        possession_player: str,
        possession_team: str = "",
    ):
        # Determine team based on possession_player if available
        # possession_player contains the GUID of the player with possession
        if possession_player in self.home_player_guids:
            team_fallback = "__HOME_TEAM__"
        elif possession_player in self.visitor_player_guids:
            team_fallback = "__VISITOR_TEAM__"
        else:
            # If possession_player is not in either team, check the player_guid
            if player_guid in self.home_player_guids:
                team_fallback = "__HOME_TEAM__"
            elif player_guid in self.visitor_player_guids:
                team_fallback = "__VISITOR_TEAM__"
            else:
                team_fallback = "__VISITOR_TEAM__"  # Default to visitor if unknown

        # If player_guid is empty or not found, use the appropriate team placeholder
        if player_guid == "" or player_guid not in players:
            effective_guid = team_fallback
            # Debug for scoring events
            if event_type in ["FG", "MISS", "FT"]:
                print(f"DEBUG EVENT: type={event_type}, player_guid='{player_guid}', possession={possession_player}, team_fallback={team_fallback}, effective={effective_guid}")
        else:
            effective_guid = player_guid

        if event_type == "FG": # Field goal made
            if effective_guid in players:
                points = int(param)
                players[effective_guid].stats_today.points += points
                if points == 3:
                    players[effective_guid].stats_today.fga3 += 1
                    players[effective_guid].stats_today.fgm3 += 1
                else:
                    players[effective_guid].stats_today.fga2 += 1
                    players[effective_guid].stats_today.fgm2 += 1

        elif event_type == "MISS": # Missed shot
            if effective_guid in players:
                if param == "3":
                    players[effective_guid].stats_today.fga3 += 1
                else:
                    players[effective_guid].stats_today.fga2 += 1

        elif event_type == "ASSIST":
            if effective_guid in players:
                players[effective_guid].stats_today.assists += 1

        elif event_type == "BLOCKED":
            if effective_guid in players:
                players[effective_guid].stats_today.blocks += 1
            if possession_player in players:
                players[possession_player].stats_today.fga2 += 1
            elif team_fallback in players:
                players[team_fallback].stats_today.fga2 += 1

        elif event_type == "MISSRESULT":
            if effective_guid in players:
                if param == "RBO": # Offensive rebound
                    players[effective_guid].stats_today.rebounds += 1
                    players[effective_guid].stats_today.off_rebounds += 1
                elif param == "RBD": # Defensive rebound
                    players[effective_guid].stats_today.rebounds += 1
                    players[effective_guid].stats_today.def_rebounds += 1

        elif event_type == "DEFLECTION":
            if effective_guid in players:
                players[effective_guid].stats_today.deflections += 1

        elif event_type == "TURNOVER":
            if param == "STEAL":
                parts = player_guid.split(":")
                if len(parts) > 0:
                    turnover_player = parts[0] if parts[0] in players else team_fallback
                    if turnover_player in players:
                        players[turnover_player].stats_today.turnovers += 1
                if len(parts) > 1:
                    steal_player = parts[1] if parts[1] in players else team_fallback
                    if steal_player in players:
                        players[steal_player].stats_today.steals += 1
            elif possession_player in players:
                players[possession_player].stats_today.turnovers += 1
            elif team_fallback in players:
                players[team_fallback].stats_today.turnovers += 1

        elif event_type == "FT": # Free throw
            parts = param.split(":")
            if len(parts) >= 2 and effective_guid in players:
                results = parts[1].split("-")
                for result in results:
                    players[effective_guid].stats_today.fta += 1
                    if result == "1":
                        players[effective_guid].stats_today.ftm += 1
                        players[effective_guid].stats_today.points += 1

        elif event_type == "FOUL":
            parts = player_guid.split(":")
            if len(parts) > 0:
                foul_player = parts[0] if parts[0] in players else team_fallback
                if foul_player in players:
                    players[foul_player].stats_today.fouls += 1

    def export_to_json(self, game_data: Dict, filename: str = "player_stats.json"):
        export_data = {
            "game_info": {
                "home_team": game_data.get("home_team", ""),
                "visitor_team": game_data.get("visitor_team", ""),
                "game_name": game_data.get("game_name", ""),
            },
            "players": [],
        }

        for player_guid, player in game_data.get("players", {}).items():
            export_data["players"].append(player.to_dict())

        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"Data exported to {filename}")
        return export_data

    def break_out_url(self, game_url):
        parsed_url = urlparse(game_url)
        query_params = parse_qs(parsed_url.query)
        game_guid = query_params.get("g", [None])[0]
        device_guid = query_params.get("dg", [None])[0]
        customer_guid = query_params.get("c", [""])[0]
        return game_guid, device_guid, customer_guid

    def get_latest_game(self, customer_guid):
        game_list = self.get_game_list(customer_guid, "")
        latest_game = game_list[0]
        game_guid = latest_game.get("game_guid", [None])
        device_guid = latest_game.get("device_guid", [None])
        print(f"Latest game: {latest_game}")
        if DEBUG:
            print(f"Game_guid: {game_guid} and Device_guid: {device_guid}")

        return game_guid, device_guid


if __name__ == "__main__":
    scraper = iScoreCentralScraper()

    # Game URL
    # game_url = "http://data.iscorecentral.com/iscorecast/basketball/scorecast.html?g=49a6f885-7797-420f-a8f2-999e4d4a2eb5&dg=1105445c-b6fd-4f07-a5e4-2725f9b124ce"
    # game_guid, device_guid, customer_guid = scraper.break_out_url(game_url)
    # print(f"Using game_guid: {game_guid}, device_guid: {device_guid}, and customer_guid: {customer_guid}")

    print("iScoreCentral Stats Scraper\n")
    home_url = "http://data.iscorecentral.com/iscorecast/basketball/scorecast.html?c="
    girls_varsity_customer_guid = "11054454CE"
    boys_varsity_customer_guid = ""
    print(f"Home Girls URL: {home_url}{girls_varsity_customer_guid}")
    print(f"Home Boys URL: {home_url}{boys_varsity_customer_guid}")

    game_guid, device_guid = scraper.get_latest_game(girls_varsity_customer_guid)
    game_data = scraper.parse_game_data(game_guid, device_guid=device_guid)

    if "error" not in game_data and game_data.get("players"):
        print(f"Home Team: {game_data.get('home_team', 'Unknown')}")
        print(f"Visitor Team: {game_data.get('visitor_team', 'Unknown')}")
        print(f"Total Players: {len(game_data['players'])}")

        if DEBUG:
            print("\nPlayers found:")
            for player_guid, player in list(game_data["players"].items()):
                if (player.stats_today.points > 0 or
                    player.player_name.endswith("(Unassigned)") or
                    player.stats_today.rebounds > 0 or
                    player.stats_today.assists > 0):
                    print(
                        f"  - #{player.player_number} {player.player_name}: {player.stats_today.points} pts, "
                        f"{player.stats_today.rebounds} reb, {player.stats_today.assists} ast, "
                        f"{player.stats_today.fgm2}-{player.stats_today.fga2} 2PT, "
                        f"{player.stats_today.fgm3}-{player.stats_today.fga3} 3PT"
                    )

        # Export to JSON
        scraper.export_to_json(game_data, "basketball_stats.json")
    else:
        print(f"\nError occurred: {game_data.get('error', 'Unknown error')}")
