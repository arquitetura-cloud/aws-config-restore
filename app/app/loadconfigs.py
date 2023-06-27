import yaml
import os
class MenuOptions:
    def __init__(self):
        datapath = os.path.join(os.path.dirname(__file__), '../data/config.yaml')
        normpath = os.path.normpath(datapath)
        with open(normpath, 'r') as config_file:
            menu_yaml = config_file.read()
        self.menu_data = yaml.load(menu_yaml, Loader=yaml.FullLoader)

    def __call__(self):
        options = self.menu_data['menu_options']
        menu_list = [options[key]['DisplayName'] for key in options.keys()]
        menu_list.append("Quit")
        return menu_list

class LoadConfigs:
    def __init__(self):
        datapath = os.path.join(os.path.dirname(__file__), '../data/config.yaml')
        normpath = os.path.normpath(datapath)
        with open(normpath, 'r') as config_file:
            config_yaml = config_file.read()
        self.config_data = yaml.safe_load(config_yaml)

    def __call__(self):
        return self.config_data

    def get_config(self, config_name):
        return self.config_data[config_name]

    def get_resource_types(self, resource_name):
        options = self.config_data['menu_options']
        # Get the list of menu
        return_data = []
        for data in self.config_data["menu_options"]:
            if self.config_data["menu_options"][data]['DisplayName'] == resource_name:
               #print(f'Loop: \n {self.menu_data["menu_options"][data]}')
               return_data.append(self.config_data["menu_options"][data]['ResourceTypes'])
        #print(f'Geral :\n {self.menu_data["menu_options"]}')

        return return_data

    def get_service_name(self, resource_name):
        options = self.config_data['menu_options']
        # Get the list of menu
        return_data = ""
        for data in self.config_data["menu_options"]:
            if self.config_data["menu_options"][data]['DisplayName'] == resource_name:
               #print(f'Loop: \n {self.menu_data["menu_options"][data]}')
               return_data = self.config_data["menu_options"][data]['ServiceName']
        #print(f'Geral :\n {self.menu_data["menu_options"]}')

        return return_data
