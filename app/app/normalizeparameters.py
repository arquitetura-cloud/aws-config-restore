import json
from deepdiff import DeepSearch, extract
import os
new_to_restore_config_str = ""


class NormalizeParameters:
    def __init__(self, to_restore_config, baseconfig=None):
        datapath = os.path.join(os.path.dirname(__file__), '../data/reference_cloudfront.json')
        normpath = os.path.normpath(datapath)
        with open(normpath) as f:
            self.base_config = json.load(f)
        f.close()

        self.to_restore_config = to_restore_config

    def normalize(self):
        global new_to_restore_config_str

        new_to_restore_config_str = str(self.to_restore_config)

        def parselist(data, counter, keyname):
            for i in range(len(data)):
                if type(data[i]) is dict:
                    parsedict(data[i], counter + 1, keyname)
                elif type(data[i]) is list:
                    parselist(data[i], counter + 1, keyname)
                else:
                    parsestring(data[i], counter + 1, keyname)

        def parsedict(data, counter, keyname):
            #tab = '\t' * counter
            for x, y in data.items():
                #print(f'{key} --> {ds_n}')
                #print(f'{tab} {x} --> {search_deepdiff(x)}')
                update_parameters(x, search_deepdiff(x))
                if type(y) is dict:
                    parsedict(y, counter + 1, keyname)
                elif type(y) is list:
                    parselist(y, counter + 1, keyname)
                else:
                    parsestring(x, counter + 1, keyname)

        def parsestring(data, counter, keyname):
            # tab = '\t'*counter
            # print(f'{tab} Param_do_config:, {type(data)}#SouStringdoParse')
            pass

        def search_deepdiff(string):
            #Append single quotes to string to match Regular Expression Search:
            string = "'" + string + "'"
            ds = DeepSearch(self.base_config, string, verbose_level=1, use_regexp=True)
            lst = extract(ds['matched_paths'], 'root[0]')
            ds_n = lst.split("['")[-1].replace("']", '')
            return ds_n

        def update_parameters(oldstring, newstring):
            global new_to_restore_config_str
            # Append single quotes to string to match only parameters and not values:
            oldstring = "'" + oldstring + "'"
            newstring = "'" + newstring + "'"
            new_to_restore_config_str = new_to_restore_config_str.replace(oldstring, newstring)

        for key, value in self.to_restore_config.items():
            #print(f'{key} --> {search_deepdiff(key)}')
            update_parameters(key, search_deepdiff(key))
            if type(value) is list:
                parselist(value, 1, key)
            elif type(value) is dict:
                parsedict(value, 1, key)
            else:
                # print(f'\t{value}, {type(value)}#SouString')
                pass

        # print('-------------------------------------------')
        # print(str(new_to_restore_config_str))
        return json.loads(new_to_restore_config_str.replace("'", '"').replace('True', 'true').replace('False', 'false'))
        # print('-------------------------------------------')
        # print(DeepDiff(base_config,json.loads(new_to_restore_config_str.replace("'",'"').replace('True', 'true').replace('False','false'))))
