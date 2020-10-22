import json
from game_engine.utils.meta_classes import singleton


class config(metaclass=singleton):

    CONFIG_FILE_PATH = "config.json"

    _config = dict()

    def get(self, config_key):
        if (not bool(self._config)):
            self._config = self._get_config_json()

        if (config_key not in self._config):
            print(f"{config_key} configuration is not included in"
                  "{CONFIG_FILE_PATH}")
            exit()

        return self._config[config_key]

    def _get_config_json(self):
        try:
            with open(self.CONFIG_FILE_PATH, 'r') as json_file:
                return json.loads(json_file.read())
        except FileNotFoundError:
            print(f'{self.CONFIG_FILE_PATH} file not found!')
            exit()
