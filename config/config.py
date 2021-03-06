import json


class Config:
    # TODO: BETTER IMPLEMENTATION !!
    def __init__(self, config_file_dir="config_data", config_file_name="config.json"):
        self.config_file_dir = config_file_dir
        self.config_file_name = config_file_name
        self.config = {}
        self.load_config()

    # TODO: JUST A TEMP FIX, WILL BE UPDATED IN FUTURE UPDATES!!
    @property
    def meroshare_credentials(self):
        return self.config["third_party_services"]["meroshare"]["credentials"]

    def update_config(self, key, value):
        self.config[key] = value
        self.write_config()

    def del_key(self, key):
        pass

    def load_config(self):
        with open(f"{self.config_file_dir}/{self.config_file_name}", "r") as f:
            self.config = json.load(f)

    def write_config(self):
        with open(f"{self.config_file_dir}/{self.config_file_name}", "w") as f:
            json.dump(self.config, f)
