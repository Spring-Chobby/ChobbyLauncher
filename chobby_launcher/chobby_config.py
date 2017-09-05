import json
import pkgutil

class ChobbyConfig(object):
    def __init__(self):
        configFile = pkgutil.get_data("chobby_launcher", "config.json")
        configFile = configFile.decode('utf-8')
        json_data = json.loads(configFile)

        self.auto_download = json_data["auto_download"]
        self.auto_start = json_data["auto_start"]
        self.game_title = json_data["game_title"]

        self.game_rapid = json_data["game_rapid"]
        self.lobby_rapid = json_data["lobby_rapid"]
